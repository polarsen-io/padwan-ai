import pytest

from padwan_ai import ElevenLabsClient

from .conftest import skip_no_elevenlabs

pytestmark = [pytest.mark.e2e, skip_no_elevenlabs]

# "George", a premade voice available on every account
VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"


async def test_speech_roundtrip():
    async with ElevenLabsClient(voice_id=VOICE_ID) as client:
        speech = await client.generate_speech(
            "The quick brown fox jumps over the lazy dog.", model="eleven_flash_v2_5"
        )
        assert speech.audio
        assert speech.mime_type.startswith("audio/")

        result = await client.transcribe(
            file=speech.audio, filename="fox.mp3", language="en"
        )

    assert "fox" in result["text"].lower()
    assert any(w["type"] == "word" for w in result["words"])
