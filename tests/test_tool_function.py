import json
from typing import Any, cast

import pytest

pydantic = pytest.importorskip("pydantic")

from padwan_llm import AgentSession, LLMClientBase, McpTool  # noqa: E402
from padwan_llm.tools import tool  # noqa: E402
from tests.test_agent import FakeChatStream, FakeClient, make_tool_call  # noqa: E402


class Ref(pydantic.BaseModel):
    id: int
    name: str


async def search_references(query: str, limit: int = 5) -> list[Ref]:
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
    assert t.input_schema["properties"]["query"] == {"title": "Query", "type": "string"}
    assert t.input_schema["properties"]["limit"]["default"] == 5
    assert t.input_schema["required"] == ["query"]
    assert "title" not in t.input_schema


def test_name_and_description_can_be_overridden() -> None:
    t = tool(search_references, name="search", description="Find things.")
    assert (t.name, t.description) == ("search", "Find things.")


async def test_handler_validates_coerces_and_dumps_the_result() -> None:
    result = await tool(search_references).handler({"query": "pelle", "limit": "3"})
    assert result == [{"id": 1, "name": "pelle 3"}]
    assert await tool(read_reference).handler({"ref_id": 7}) == {
        "id": 7,
        "name": "EXCAVATOR 20-22T",
    }


async def test_handler_rejects_bad_arguments_before_calling() -> None:
    with pytest.raises(pydantic.ValidationError):
        await tool(search_references).handler({"limit": 3})


def test_an_unannotated_parameter_is_refused() -> None:
    async def loose(query, limit: int = 1) -> str:  # type: ignore[no-untyped-def]
        return query

    with pytest.raises(TypeError, match="needs a type annotation"):
        tool(loose)


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


def test_without_pydantic_the_error_says_which_extra_to_install(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    import builtins

    real_import = builtins.__import__

    def no_pydantic(name: str, *args: Any, **kwargs: Any) -> Any:
        if name == "pydantic":
            raise ImportError("no pydantic")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_pydantic)
    with pytest.raises(ImportError, match=r"padwan-llm\[pydantic\]"):
        tool(read_reference)
