from typing import Any, cast

import pytest

from padwan_llm import (
    AgentSession,
    ChatResponse,
    ChatStream,
    LLMClientBase,
    McpTool,
    ToolCall,
    UsageToken,
)
from padwan_llm.testing import ScriptedClient, Step

_TOOL_CALL: ToolCall = {
    "id": "call_1_0",
    "type": "function",
    "function": {"name": "search", "arguments": '{"query": "pelle"}'},
}


async def _drain(stream: ChatStream) -> str:
    return "".join([chunk async for chunk in stream])


@pytest.mark.parametrize(
    ("step", "text", "usage", "tool_calls"),
    [
        pytest.param(
            Step(text="Bonjour", usage={"total": 5, "input": 3, "output": 2}),
            "Bonjour",
            {"total": 5, "input": 3, "output": 2},
            None,
            id="text",
        ),
        pytest.param(
            Step(tool_calls=[("search", {"query": "pelle"})]),
            "",
            {"total": 10, "input": 7, "output": 3},
            [_TOOL_CALL],
            id="tool_call",
        ),
    ],
)
async def test_stream_chat(
    step: Step, text: str, usage: UsageToken, tool_calls: list[ToolCall] | None
) -> None:
    stream = ScriptedClient([step]).stream_chat([{"role": "user", "content": "q"}])
    assert await _drain(stream) == text
    assert stream.usage == usage
    assert stream.tool_calls == tool_calls


@pytest.mark.parametrize(
    ("step", "response"),
    [
        pytest.param(
            Step(text="done"), {"content": "done", "finish_reason": "stop"}, id="text"
        ),
        pytest.param(
            Step(tool_calls=[("search", {"query": "pelle"})]),
            {
                "content": None,
                "finish_reason": "tool_calls",
                "tool_calls": [_TOOL_CALL],
            },
            id="tool_call",
        ),
    ],
)
async def test_complete_chat(step: Step, response: ChatResponse) -> None:
    client = ScriptedClient([step])
    assert await client.complete_chat([{"role": "user", "content": "go"}]) == (
        response,
        step.usage,
    )


async def test_requests_are_recorded_and_the_script_ends() -> None:
    client = ScriptedClient([Step(text="ok")])
    messages: list[Any] = [{"role": "user", "content": "q"}]
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
    seen: list[dict[str, Any]] = []

    async def echo(args: dict[str, Any]) -> dict[str, Any]:
        seen.append(args)
        return {"found": 1}

    client = ScriptedClient([Step(tool_calls=[("echo", {"x": 1})]), Step(text="done")])
    session = AgentSession(
        client=cast(LLMClientBase, client),
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
