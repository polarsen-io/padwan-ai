import inspect
from collections.abc import Awaitable, Callable, Sequence
from importlib.util import find_spec
from typing import Any, Literal, Protocol, get_type_hints

from .mcp import McpTool

__all__ = ("MsgspecValidator", "PydanticValidator", "ToolValidator", "tool")

type _Field = tuple[str, Any] | tuple[str, Any, Any]
"""(name, annotation[, default]); a 2-tuple is a required parameter."""

type _Validate = Callable[[dict[str, Any]], dict[str, Any]]

_KEYWORD_KINDS = (
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
    inspect.Parameter.KEYWORD_ONLY,
)


class ToolValidator(Protocol):
    """Schema generation, argument validation and result dumping for one library."""

    def compile(
        self, name: str, fields: Sequence[_Field]
    ) -> tuple[dict[str, Any], _Validate]:
        """JSON Schema for the model, and validate(raw_args) -> typed kwargs, raising on bad input."""
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
        # msgspec puts the struct itself under $defs behind a top-level $ref; inline it
        raw = msgspec.json.schema(struct)
        schema: dict[str, Any] = raw["$defs"].pop(raw["$ref"].rsplit("/", 1)[-1])
        schema.pop("title", None)
        if raw["$defs"]:
            schema["$defs"] = raw["$defs"]

        def validate(args: dict[str, Any]) -> dict[str, Any]:
            # strict=False: models send "3" for ints, coerce instead of rejecting
            parsed = msgspec.convert(args, struct, strict=False)
            return {f: getattr(parsed, f) for f in struct.__struct_fields__}

        return schema, validate

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
        schema = model.model_json_schema()
        schema.pop("title", None)

        def validate(args: dict[str, Any]) -> dict[str, Any]:
            parsed = model.model_validate(args)
            return {f: getattr(parsed, f) for f in model.model_fields}

        return schema, validate

    def dump(self, result: Any) -> Any:
        from pydantic_core import to_jsonable_python

        return to_jsonable_python(result)


_BACKENDS: dict[str, type[ToolValidator]] = {
    "msgspec": MsgspecValidator,
    "pydantic": PydanticValidator,
}


def _resolve(validator: ToolValidator | str | None) -> ToolValidator:
    if validator is None:
        installed = [lib for lib in _BACKENDS if find_spec(lib) is not None]
        if not installed:
            raise ImportError(
                "padwan_llm.tools.tool needs a validator: pip install msgspec or pydantic"
            )
        if len(installed) > 1:
            raise ValueError(
                "both msgspec and pydantic are installed; "
                "pass validator='msgspec' or validator='pydantic' to tool()"
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
    (``"msgspec"``, ``"pydantic"`` or any `ToolValidator`); when omitted, the only installed
    one is used. Constraints and error text are the chosen library's own.
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
    backend = _resolve(validator)
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
