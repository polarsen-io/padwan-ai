import pytest

from padwan_ai import (
    GradiumClient,
    GradiumRealtimeS2SClient,
    GradiumRealtimeSTTClient,
    GradiumRealtimeTTSClient,
)
from padwan_ai.errors import LLMError

from .conftest import skip_no_gradium

pytestmark = [pytest.mark.e2e, skip_no_gradium]

# flagship voice from the Gradium docs examples
VOICE_ID = "YTpq7expH9539ERJ"
TEXT = "The quick brown fox jumps over the lazy dog."
# 80 ms of 24 kHz s16le mono
CHUNK = 3840


def _chunks(audio: bytes) -> list[bytes]:
    return [audio[i : i + CHUNK] for i in range(0, len(audio), CHUNK)]


async def test_speech_roundtrip():
    async with GradiumClient(voice_id=VOICE_ID) as client:
        speech = await client.generate_speech(TEXT)
        assert speech.audio.startswith(b"RIFF")

        result = await client.transcribe(speech.audio, language="en")

    assert "fox" in result["text"].lower()
    assert result["segments"][0]["start"] >= 0


async def test_stream_speech():
    async with GradiumClient(voice_id=VOICE_ID) as client:
        chunks = [c async for c in client.stream_speech(TEXT, chunk_size=1024)]

    assert b"".join(chunks).startswith(b"RIFF")
    assert len(chunks) > 1


async def test_realtime_tts_stt_roundtrip():
    tokens = ["The quick br", "own fox ", "jumps over the lazy dog."]
    async with GradiumRealtimeTTSClient(
        voice_id=VOICE_ID, output_format="pcm_24000"
    ) as tts:
        assert tts.ready["request_id"]
        audio = b"".join([a async for a in tts.stream(tokens)])
    assert audio

    async with GradiumRealtimeSTTClient(language="en") as stt:
        texts = [
            t async for m in stt.stream(_chunks(audio)) if (t := stt.transcript(m))
        ]

    assert "fox" in " ".join(texts).lower()


async def test_realtime_s2s():
    async with GradiumClient(voice_id=VOICE_ID) as client:
        speech = await client.generate_speech(TEXT, output_format="pcm_24000")

    async with GradiumRealtimeS2SClient(voice_id=VOICE_ID, target_language="fr") as s2s:
        messages = [m async for m in s2s.stream(_chunks(speech.audio))]

    assert any(s2s.audio_bytes(m) for m in messages)
    texts = [t for m in messages if (t := s2s.transcript(m))]
    assert "renard" in " ".join(texts).lower()


async def test_voices():
    async with GradiumClient(voice_id=VOICE_ID) as client:
        catalog = await client.list_voices(include_catalog=True)
        assert VOICE_ID in {v["uid"] for v in catalog}
        assert (await client.get_voice(VOICE_ID))["uid"] == VOICE_ID

        sample = await client.generate_speech(f"{TEXT} {TEXT} {TEXT}")
        try:
            voice_id = await client.clone_voice(
                "padwan-e2e", sample.audio, language="en", input_format="wav"
            )
        except LLMError as error:
            if "quota" in str(error).lower() or "plan" in str(error).lower():
                pytest.skip(f"plan does not allow custom voices: {error}")
            raise
        try:
            updated = await client.update_voice(voice_id, description="padwan e2e")
            assert updated.get("description") == "padwan e2e"
            assert voice_id in {v["uid"] for v in await client.list_voices()}
        finally:
            await client.delete_voice(voice_id)
