import os

import pytest

from padwan_ai import OpenAIClient
from padwan_ai.conversation import Message

from .conftest import _skip_no_key

pytestmark = [pytest.mark.e2e, _skip_no_key("VLLM_BASE_URL")]

PROMPT = [Message(role="user", content="What is 7 * 8?")]


@pytest.mark.parametrize(
    "stream", [pytest.param(True, id="stream"), pytest.param(False, id="complete")]
)
async def test_reasoning_forwarded_to_on_thought(stream: bool) -> None:
    """vLLM `reasoning` field reaches on_thought, not the answer text."""
    received: list[str] = []
    async with OpenAIClient(
        model=os.environ.get("VLLM_MODEL") or "Qwen/Qwen3-0.6B",
        base_url=os.environ["VLLM_BASE_URL"],
        api_key="EMPTY",
        on_thought=received.append,
    ) as client:
        if stream:
            text = "".join([chunk async for chunk in client.stream_chat(PROMPT)])
        else:
            response, _ = await client.complete_chat(PROMPT)
            text = response["content"]

    assert text and "56" in text
    assert received, "no reasoning forwarded to on_thought"
    assert "".join(received) not in text
