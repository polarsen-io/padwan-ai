"""Build an `McpTool` from a typed async function: the signature is the schema.

Requires Pydantic (``pip install "padwan-llm[pydantic]"``): the parameters are turned into
a model that produces the JSON Schema the model sees and validates the arguments it sends
back, so a handler never runs on malformed input.
"""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable
from typing import Any, cast, get_type_hints

from .mcp import McpTool

__all__ = ("tool",)


def _require_pydantic() -> Any:
    try:
        import pydantic
    except ImportError as e:
        raise ImportError(
            "padwan_llm.tools.tool requires Pydantic: pip install 'padwan-llm[pydantic]'"
        ) from e
    return pydantic


def _plain(value: Any, base_model: type) -> Any:
    """Tool results travel to the model as JSON: dump models, recurse into lists and dicts."""
    if isinstance(value, base_model):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_plain(v, base_model) for v in value]
    if isinstance(value, dict):
        return {k: _plain(v, base_model) for k, v in value.items()}
    return value


def tool(
    fn: Callable[..., Awaitable[Any]],
    *,
    name: str | None = None,
    description: str | None = None,
) -> McpTool:
    """An `McpTool` whose schema is `fn`'s typed signature and whose handler validates first.

    ``name`` defaults to the function name and ``description`` to its docstring. Every
    parameter needs a type annotation; a default value makes it optional in the schema.
    A `pydantic.BaseModel` result (or a list/dict of them) is dumped to plain JSON data;
    anything else is passed through for `AgentSession` to serialize.
    """
    pydantic = _require_pydantic()
    hints = get_type_hints(fn)
    fields: dict[str, Any] = {}
    for param_name, param in inspect.signature(fn).parameters.items():
        if param_name not in hints:
            raise TypeError(
                f"tool {fn.__name__!r}: parameter {param_name!r} needs a type annotation"
            )
        default = ... if param.default is inspect.Parameter.empty else param.default
        fields[param_name] = (hints[param_name], default)
    args_model = pydantic.create_model(f"{fn.__name__}_args", **fields)
    schema = args_model.model_json_schema()
    schema.pop("title", None)

    async def handler(args: dict[str, Any]) -> Any:
        parsed = args_model.model_validate(args)
        result = await fn(**{field: getattr(parsed, field) for field in fields})
        return _plain(result, pydantic.BaseModel)

    return McpTool(
        name=name or fn.__name__,
        description=description
        if description is not None
        else (inspect.getdoc(fn) or ""),
        input_schema=schema,
        handler=cast(Any, handler),
    )
