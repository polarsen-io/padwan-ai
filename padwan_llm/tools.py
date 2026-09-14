import inspect
from collections.abc import Awaitable, Callable
from typing import Any, get_type_hints

from .mcp import McpTool

__all__ = ("tool",)

_KEYWORD_KINDS = (
    inspect.Parameter.POSITIONAL_OR_KEYWORD,
    inspect.Parameter.KEYWORD_ONLY,
)


def _require_msgspec() -> Any:
    try:
        import msgspec
    except ImportError as e:
        raise ImportError(
            "padwan_llm.tools.tool requires msgspec: pip install 'padwan-llm[msgspec]'"
        ) from e
    return msgspec


def tool(
    fn: Callable[..., Awaitable[Any]],
    *,
    name: str | None = None,
    description: str | None = None,
) -> McpTool:
    """An `McpTool` whose schema is `fn`'s typed signature; arguments are validated before `fn` runs.

    ``name`` defaults to the function name and ``description`` to its docstring. Every
    parameter needs a type annotation and must be passable by keyword; a default makes it
    optional. The result goes through `msgspec.to_builtins` so structs and dataclasses
    reach the model as plain JSON data.
    """
    msgspec = _require_msgspec()
    hints = get_type_hints(fn, include_extras=True)
    fields: list[tuple[str, Any] | tuple[str, Any, Any]] = []
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
    args_struct = msgspec.defstruct(f"{fn.__name__}_args", fields, kw_only=True)
    # msgspec puts the struct itself under $defs behind a top-level $ref; inline it
    raw = msgspec.json.schema(args_struct)
    schema: dict[str, Any] = raw["$defs"].pop(args_struct.__name__)
    schema.pop("title", None)
    if raw["$defs"]:
        schema["$defs"] = raw["$defs"]

    async def handler(args: dict[str, Any]) -> Any:
        # strict=False: models send "3" for ints, coerce instead of rejecting
        parsed = msgspec.convert(args, args_struct, strict=False)
        result = await fn(
            **{f: getattr(parsed, f) for f in args_struct.__struct_fields__}
        )
        return msgspec.to_builtins(result)

    return McpTool(
        name=name or fn.__name__,
        description=description
        if description is not None
        else (inspect.getdoc(fn) or ""),
        input_schema=schema,
        handler=handler,
    )
