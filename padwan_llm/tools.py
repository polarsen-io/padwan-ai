import inspect
import json
from collections.abc import Awaitable, Callable, Mapping, Sequence
from importlib.util import find_spec
from typing import (
    Annotated,
    Any,
    Literal,
    Protocol,
    get_args,
    get_origin,
    get_type_hints,
)

from .mcp import McpTool

__all__ = ("MsgspecValidator", "PydanticValidator", "ToolValidator", "tool")

type _Field = tuple[str, Any] | tuple[str, Any, Any]
"""(name, annotation[, default]); a 2-tuple is a required parameter."""

type _Validate = Callable[[dict[str, Any]], dict[str, Any]]
type _Convert = Callable[[Any], Any]

_KEYWORD_KINDS = (
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
    inspect.Parameter.KEYWORD_ONLY,
)


def _inline_root(raw: dict[str, Any]) -> dict[str, Any]:
    """Lift the class behind a top-level `$ref` out of `$defs`, dropping its title.

    A recursive class keeps its definition under `$defs` so the inner `$ref`s stay valid.
    """
    if "$ref" not in raw:
        raw.pop("title", None)
        return raw
    name = raw["$ref"].rsplit("/", 1)[-1]
    defs: dict[str, Any] = raw["$defs"]
    schema = {k: v for k, v in defs[name].items() if k != "title"}
    if f'"#/$defs/{name}"' not in json.dumps(defs):
        del defs[name]
    if defs:
        schema["$defs"] = defs
    return schema


class ToolValidator(Protocol):
    """Schema generation, argument validation and result dumping for one library."""

    def compile(
        self, name: str, fields: Sequence[_Field]
    ) -> tuple[dict[str, Any], _Validate]:
        """JSON Schema for the model, and validate(raw_args) -> typed kwargs, raising on bad input."""
        ...

    def adapt(self, cls: type) -> tuple[dict[str, Any], _Convert]:
        """JSON Schema of `cls` (top-level inlined, no title) and convert(json_data) -> instance.

        Called once per class: the returned converter holds whatever the library builds up front.
        """
        ...

    def dump(self, result: Any) -> Any:
        """Tool result -> JSON-able builtins, raising when the library can't serialise it."""
        ...


class MsgspecValidator:
    def compile(
        self, name: str, fields: Sequence[_Field]
    ) -> tuple[dict[str, Any], _Validate]:
        import msgspec

        struct = msgspec.defstruct(name, fields, kw_only=True)
        schema, convert = self.adapt(struct)

        def validate(args: dict[str, Any]) -> dict[str, Any]:
            parsed = convert(args)
            return {f: getattr(parsed, f) for f in struct.__struct_fields__}

        return schema, validate

    def adapt(self, cls: type) -> tuple[dict[str, Any], _Convert]:
        import msgspec

        schema = _inline_root(msgspec.json.schema(cls))

        def convert(obj: Any) -> Any:
            # strict=False: models send "3" for ints, coerce instead of rejecting
            return msgspec.convert(obj, cls, strict=False)

        return schema, convert

    def dump(self, result: Any) -> Any:
        import msgspec

        return msgspec.to_builtins(result)


class PydanticValidator:
    def compile(
        self, name: str, fields: Sequence[_Field]
    ) -> tuple[dict[str, Any], _Validate]:
        import pydantic

        for f in fields:
            # pydantic silently drops private names; BaseModel attributes would be shadowed
            if f[0].startswith("_") or hasattr(pydantic.BaseModel, f[0]):
                raise TypeError(
                    f"tool {name!r}: parameter {f[0]!r} is reserved by pydantic"
                )
        # Any: create_model's **kwargs are typed per reserved name, not for field tuples
        defs: dict[str, Any] = {
            f[0]: (f[1], ... if len(f) == 2 else f[2]) for f in fields
        }
        model = pydantic.create_model(name, **defs)
        schema, convert = self.adapt(model)

        def validate(args: dict[str, Any]) -> dict[str, Any]:
            parsed = convert(args)
            return {f: getattr(parsed, f) for f in model.model_fields}

        return schema, validate

    def adapt(self, cls: type) -> tuple[dict[str, Any], _Convert]:
        from pydantic import TypeAdapter

        # building the adapter is the expensive part; do it once per class, not per call
        adapter = TypeAdapter(cls)
        return _inline_root(adapter.json_schema()), adapter.validate_python

    def dump(self, result: Any) -> Any:
        from pydantic_core import to_jsonable_python

        return to_jsonable_python(result)


_BACKENDS: dict[str, type[ToolValidator]] = {
    "msgspec": MsgspecValidator,
    "pydantic": PydanticValidator,
}


def _markers(lib: str) -> tuple[type, ...]:
    """Classes whose presence in an annotation ties it to `lib`."""
    if lib == "msgspec":
        import msgspec

        return (msgspec.Meta, msgspec.Struct)
    import annotated_types
    import pydantic
    from pydantic.fields import FieldInfo

    return (FieldInfo, annotated_types.BaseMetadata, pydantic.BaseModel)


def _annotated_libs(hints: Mapping[str, Any]) -> set[str]:
    """Libraries the annotations name, through Annotated metadata, unions and generics."""
    markers = {lib: _markers(lib) for lib in _BACKENDS if find_spec(lib) is not None}
    found: set[str] = set()

    def walk(tp: Any) -> None:
        if get_origin(tp) is Annotated or get_origin(tp) is not None:
            for arg in get_args(tp):
                walk(arg)
            return
        for lib, classes in markers.items():
            if isinstance(tp, classes) or (
                isinstance(tp, type) and issubclass(tp, classes)
            ):
                found.add(lib)

    for tp in hints.values():
        walk(tp)
    return found


def _resolve(
    validator: ToolValidator | str | None, hints: Mapping[str, Any]
) -> ToolValidator:
    if validator is None:
        libs = _annotated_libs(hints)
        if len(libs) > 1:
            raise ValueError("annotations mix msgspec and pydantic types; pick one")
        installed = list(libs) or [
            lib for lib in _BACKENDS if find_spec(lib) is not None
        ]
        if not installed:
            raise ImportError(
                "validation needs a library: pip install msgspec or pydantic"
            )
        if len(installed) > 1:
            raise ValueError(
                "both msgspec and pydantic are installed and the annotations name neither; "
                "pass validator='msgspec' or validator='pydantic'"
            )
        return _BACKENDS[installed[0]]()
    if isinstance(validator, str):
        return _BACKENDS[validator]()
    return validator


def tool(
    fn: Callable[..., Awaitable[Any]],
    *,
    name: str | None = None,
    description: str | None = None,
    validator: ToolValidator | Literal["msgspec", "pydantic"] | None = None,
) -> McpTool:
    """An `McpTool` whose schema is `fn`'s typed signature; arguments are validated before `fn` runs.

    ``name`` defaults to the function name and ``description`` to its docstring. Every
    parameter needs a type annotation and must be passable by keyword; a default makes it
    optional. ``validator`` picks the library doing schema, validation and result dumping
    (``"msgspec"``, ``"pydantic"`` or any `ToolValidator`); when omitted, the library the
    annotations name is used, else the only installed one. Constraints and error text are the chosen library's own.
    """
    hints = get_type_hints(fn, include_extras=True)
    fields: list[_Field] = []
    for param_name, param in inspect.signature(fn).parameters.items():
        if param.kind not in _KEYWORD_KINDS:
            raise TypeError(
                f"tool {fn.__name__!r}: parameter {param_name!r} must be passable by keyword"
            )
        if param_name not in hints:
            raise TypeError(
                f"tool {fn.__name__!r}: parameter {param_name!r} needs a type annotation"
            )
        if param.default is inspect.Parameter.empty:
            fields.append((param_name, hints[param_name]))
        else:
            fields.append((param_name, hints[param_name], param.default))
    backend = _resolve(validator, hints)
    schema, validate = backend.compile(f"{fn.__name__}_args", fields)

    async def handler(args: dict[str, Any]) -> Any:
        return backend.dump(await fn(**validate(args)))

    return McpTool(
        name=name or fn.__name__,
        description=description
        if description is not None
        else (inspect.getdoc(fn) or ""),
        input_schema=schema,
        handler=handler,
    )
