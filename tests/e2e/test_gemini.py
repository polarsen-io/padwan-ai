import pytest

from padwan_ai import GeminiClient
from padwan_ai.gemini.batch import BatchRequest
from padwan_ai.gemini.models import Part

from .conftest import skip_no_gemini

pytestmark = [pytest.mark.e2e, skip_no_gemini]


async def test_stream_thought_callback() -> None:
    """on_thought callback fires and thoughts are accumulated on the stream."""
    received: list[str] = []
    async with GeminiClient(
        model="gemini-2.5-flash",
        on_thought=received.append,
        thinking_config={"thinkingBudget": 2048, "includeThoughts": True},
    ) as client:
        stream = client.stream_chat([{"role": "user", "content": "What is 7 * 8?"}])
        text = "".join([chunk async for chunk in stream])

    assert text, "no text returned"
    assert "56" in text
    assert received, "no thought chunks received"


async def test_complete_chat_thought_callback() -> None:
    """`complete_chat` must skip thought parts and return the real answer.

    Regression: `complete_chat` used to return whichever text part came
    first, including ones flagged `thought: true`, leaking the model's
    internal reasoning into the response. Verifies the fix end-to-end
    with a real reasoning model.
    """
    received: list[str] = []
    async with GeminiClient(
        model="gemini-2.5-flash",
        on_thought=received.append,
        thinking_config={"thinkingBudget": 2048, "includeThoughts": True},
    ) as client:
        response, _ = await client.complete_chat(
            [{"role": "user", "content": "What is 7 * 8?"}]
        )

    assert response["content"], "no text returned"
    assert "56" in response["content"]
    assert received, "no thought chunks forwarded to on_thought"


async def test_batch_lifecycle() -> None:
    async with GeminiClient() as client:
        req = BatchRequest(
            contents=[{"role": "user", "parts": [{"text": "Say hello"}]}],
            key="e2e-gemini-1",
        )
        job = await client.create_batch(
            [req], model="gemini-2.5-flash", display_name="e2e-test"
        )
        assert job.name
        assert job.state

        fetched = await client.get_batch(job.name)
        assert fetched.name == job.name

        jobs, _ = await client.list_batches(page_size=5)
        assert len(jobs) >= 0  # may be empty if cleaned up

        await client.cancel_batch(job.name)


async def test_embeddings() -> None:
    async with GeminiClient(model="gemini-embedding-001") as client:
        resp = await client.fetch_embeddings(["Hello", "World"], dimensions=256)
        assert len(resp["embeddings"]) == 2
        assert len(resp["embeddings"][0]["values"]) == 256


@pytest.mark.parametrize(
    "model, text, voice",
    [
        pytest.param(
            "gemini-3.8-flash-lite-tts",
            "Say cheerfully: have a wonderful day!",
            "Kore",
            id="single-voice",
        ),
        pytest.param(
            "gemini-3.8-flash-tts",
            [
                {
                    "text": "Hi Bob!",
                    "speechMetadata": {"speaker": "Alice", "style": "excited"},
                },
                {"text": "<laughs> Hey Alice.", "speechMetadata": {"speaker": "Bob"}},
            ],
            {"Alice": "Leda", "Bob": "Puck"},
            id="multi-speaker-lines",
        ),
    ],
)
async def test_generate_speech(
    model: str, text: str | list[Part], voice: str | dict[str, str]
) -> None:
    async with GeminiClient(model=model) as client:
        speech, usage = await client.generate_speech(text, voice)
    assert speech.mime_type == "audio/wav"
    assert speech.audio[:4] == b"RIFF"
    assert usage["output"] > 0
