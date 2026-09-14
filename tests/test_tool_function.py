import json
from contextlib import nullcontext
from typing import Annotated, Any, cast

import pytest

msgspec = pytest.importorskip("msgspec")

from padwan_llm import AgentSession, LLMClientBase, McpTool  # noqa: E402
from padwan_llm.tools import tool  # noqa: E402
from tests.test_agent import FakeChatStream, FakeClient, make_tool_call  # noqa: E402


class Ref(msgspec.Struct):
    id: int
    name: str


async def search_references(
    query: str, limit: Annotated[int, msgspec.Meta(ge=1, le=10)] = 5
) -> list[Ref]:
    """Search the references by name."""
    return [Ref(id=1, name=f"{query} {limit}")]


async def read_reference(ref_id: int) -> Ref:
    """Read one reference."""
    return Ref(id=ref_id, name="EXCAVATOR 20-22T")


def test_name_description_and_schema_come_from_the_signature() -> None:
    t = tool(search_references)
    assert isinstance(t, McpTool)
    assert t.name == "search_references"
    assert t.description == "Search the references by name."
    assert t.input_schema["properties"]["query"] == {"type": "string"}
    assert t.input_schema["properties"]["limit"] == {
        "type": "integer",
        "minimum": 1,
        "maximum": 10,
        "default": 5,
    }
    assert t.input_schema["required"] == ["query"]
    assert "title" not in t.input_schema


def test_name_and_description_can_be_overridden() -> None:
    t = tool(search_references, name="search", description="Find things.")
    assert (t.name, t.description) == ("search", "Find things.")


@pytest.mark.parametrize(
    ("fn", "args", "expected", "raises"),
    [
        pytest.param(
            search_references,
            {"query": "pelle", "limit": "3"},
            [{"id": 1, "name": "pelle 3"}],
            nullcontext(),
            id="coerces_and_dumps_list",
        ),
        pytest.param(
            read_reference,
            {"ref_id": 7},
            {"id": 7, "name": "EXCAVATOR 20-22T"},
            nullcontext(),
            id="dumps_struct",
        ),
        pytest.param(
            search_references,
            {"limit": 3},
            None,
            pytest.raises(msgspec.ValidationError, match="query"),
            id="missing_required",
        ),
        pytest.param(
            search_references,
            {"query": "pelle", "limit": -100},
            None,
            pytest.raises(msgspec.ValidationError, match=">= 1"),
            id="constraint_violated",
        ),
        pytest.param(
            read_reference,
            {"ref_id": "seven"},
            None,
            pytest.raises(msgspec.ValidationError, match="int"),
            id="wrong_type",
        ),
    ],
)
async def test_handler_validates_before_calling(
    fn: Any, args: dict[str, Any], expected: Any, raises: Any
) -> None:
    with raises:
        assert await tool(fn).handler(args) == expected


async def _unannotated(query, limit: int = 1) -> str:  # type: ignore[no-untyped-def]
    return query


async def _positional_only(query: str, /) -> str:
    return query


async def _var_positional(*queries: str) -> str:
    return " ".join(queries)


async def _var_keyword(query: str, **extra: Any) -> str:
    return query


@pytest.mark.parametrize(
    ("fn", "match"),
    [
        pytest.param(_unannotated, "needs a type annotation", id="unannotated"),
        pytest.param(_positional_only, "passable by keyword", id="positional_only"),
        pytest.param(_var_positional, "passable by keyword", id="var_positional"),
        pytest.param(_var_keyword, "passable by keyword", id="var_keyword"),
    ],
)
def test_unsupported_signatures_are_refused_at_build_time(fn: Any, match: str) -> None:
    with pytest.raises(TypeError, match=match):
        tool(fn)


async def test_it_plugs_into_an_agent_session() -> None:
    client = FakeClient(
        [
            FakeChatStream(
                chunks=[],
                tool_calls=[make_tool_call("search_references", {"query": "pelle"})],
            ),
            FakeChatStream(
                chunks=[],
                tool_calls=[
                    make_tool_call("search_references", {"limit": 2}, call_id="call_2")
                ],
            ),
            FakeChatStream(chunks=["done"]),
        ]
    )
    session = AgentSession(
        client=cast(LLMClientBase, client), mcp_tools=[tool(search_references)]
    )
    async with session:
        assert await session.send("go") == "done"
    tool_results = [m["content"] for m in session.messages if m["role"] == "tool"]
    assert json.loads(cast(str, tool_results[0])) == [{"id": 1, "name": "pelle 5"}]
    # invalid arguments reach the model as a tool error, not as an exception
    assert "error" in json.loads(cast(str, tool_results[1]))


def test_without_msgspec_the_error_says_which_extra_to_install(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import builtins

    real_import = builtins.__import__

    def no_msgspec(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "msgspec":
            raise ImportError("no msgspec")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_msgspec)
    with pytest.raises(ImportError, match=r"padwan-llm\[msgspec\]"):
        tool(read_reference)
