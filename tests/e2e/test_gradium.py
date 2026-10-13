import pytest

from padwan_ai import GradiumClient

from .conftest import skip_no_gradium

pytestmark = [pytest.mark.e2e, skip_no_gradium]

# flagship voice from the Gradium docs examples
VOICE_ID = "YTpq7expH9539ERJ"


async def test_speech_roundtrip():
    async with GradiumClient(voice_id=VOICE_ID) as client:
        speech = await client.generate_speech(
            "The quick brown fox jumps over the lazy dog."
        )
        assert speech.audio.startswith(b"RIFF")

        result = await client.transcribe(speech.audio, language="en")

    assert "fox" in result["text"].lower()
    assert result["segments"][0]["start"] >= 0
