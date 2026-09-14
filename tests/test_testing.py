import pytest

from padwan_llm import AgentSession, ChatStream, McpTool, Message
from padwan_llm.testing import ScriptedClient, Step


async def _drain(stream: ChatStream) -> str:
    return "".join([chunk async for chunk in stream])


async def test_complete_chat_with_tool_calls() -> None:
    client = ScriptedClient([Step(tool_calls=[("search", {"query": "pelle"})])])
    response, usage = await client.complete_chat([{"role": "user", "content": "go"}])
    assert response == {
        "content": None,
        "finish_reason": "tool_calls",
        "tool_calls": [
            {
                "id": "call_1_0",
                "type": "function",
                "function": {"name": "search", "arguments": '{"query": "pelle"}'},
            }
        ],
    }
    assert usage == {"total": 10, "input": 7, "output": 3}


async def test_requests_are_recorded_and_the_script_ends() -> None:
    client = ScriptedClient([Step(text="ok")])
    messages: list[Message] = [{"role": "user", "content": "q"}]
    extra_params = {"metadata": {"trace_id": "abc"}}
    await _drain(
        client.stream_chat(
            messages,
            tools=[{"name": "t", "description": "", "parameters": {}}],
            extra_params=extra_params,
        )
    )
    # regression: the record is a snapshot, later mutation must not leak into it
    messages[0]["content"] = "changed"
    extra_params["metadata"]["trace_id"] = "changed"
    (request,) = client.requests
    assert request.messages == [{"role": "user", "content": "q"}]
    assert request.tool_names == ["t"]
    assert request.extra_params == {"metadata": {"trace_id": "abc"}}
    assert client.remaining == 0
    with pytest.raises(AssertionError, match="exhausted after 1 round"):
        client.stream_chat([])


async def test_it_drives_an_agent_session() -> None:
    seen: list[dict[str, object]] = []

    async def echo(args: dict[str, object]) -> dict[str, object]:
        seen.append(args)
        return {"found": 1}

    client = ScriptedClient([Step(tool_calls=[("echo", {"x": 1})]), Step(text="done")])
    session = AgentSession(
        client=client,
        system="s",
        mcp_tools=[McpTool("echo", "", {"type": "object"}, echo)],
    )
    async with session:
        assert client.is_open
        assert await session.send("go") == "done"
    assert not client.is_open
    assert seen == [{"x": 1}]
    assert session.total_usage["total"] == 20  # two steps, default usage each
    assert client.requests[1].messages[-1]["role"] == "tool"
