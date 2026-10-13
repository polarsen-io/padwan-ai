import pytest

from padwan_ai import (
    ElevenLabsClient,
    ElevenLabsRealtimeSTTClient,
    ElevenLabsRealtimeTTSClient,
)
from padwan_ai.errors import LLMError

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

        result = await client.transcribe(speech.audio, language_code="en")

    assert "fox" in result["text"].lower()
    assert any(w["type"] == "word" for w in result["words"])


async def test_stream_speech_and_voices():
    async with ElevenLabsClient(voice_id=VOICE_ID) as client:
        chunks = [c async for c in client.stream_speech("Streaming check.")]
        voices = await client.list_voices()
        voice = await client.get_voice(VOICE_ID)

    assert len(b"".join(chunks)) > 1000
    assert VOICE_ID in {v["voice_id"] for v in voices}
    assert voice["voice_id"] == VOICE_ID


async def test_clone_and_delete_voice():
    async with ElevenLabsClient(voice_id=VOICE_ID) as client:
        sample = await client.generate_speech(
            "This is a short sample used to clone a voice for a test. " * 3
        )
        try:
            voice_id = await client.clone_voice("padwan-e2e", [sample.audio])
        except LLMError as e:
            if "subscription does not include" in str(e):
                pytest.skip("plan has no instant voice cloning")
            raise
        try:
            assert (await client.get_voice(voice_id))["name"] == "padwan-e2e"
        finally:
            await client.delete_voice(voice_id)


@pytest.mark.parametrize(
    "method, kwargs",
    [
        pytest.param(
            "generate_sound_effect",
            {"text": "a single door knock", "duration_seconds": 1},
            id="sound-effect",
        ),
        pytest.param(
            "compose_music",
            {"prompt": "calm piano jingle", "music_length_ms": 10_000},
            id="music",
        ),
    ],
)
async def test_generate_audio(method, kwargs):
    async with ElevenLabsClient() as client:
        audio = await getattr(client, method)(**kwargs)

    assert len(audio.audio) > 1000
    assert audio.mime_type == "audio/mpeg"


async def test_realtime_tts_to_stt():
    pcm = b""
    async with ElevenLabsRealtimeTTSClient(
        voice_id=VOICE_ID, output_format="pcm_16000"
    ) as tts:
        async for audio in tts.stream(
            ["The qu", "ick brown fox", " jumps over the dog."]
        ):
            pcm += audio

    async with ElevenLabsRealtimeSTTClient(language_code="en") as stt:
        for i in range(0, len(pcm), 32_000):  # 1 s chunks
            await stt.append_audio(pcm[i : i + 32_000])
        await stt.commit()
        text = ""
        async for message in stt:
            if stt.is_committed(message):
                text = stt.transcript(message) or ""
                break

    assert "fox" in text.lower()


@pytest.mark.parametrize(
    "stream", [pytest.param(False, id="full"), pytest.param(True, id="stream")]
)
async def test_speech_to_speech(stream):
    async with ElevenLabsClient(voice_id=VOICE_ID) as client:
        source = await client.generate_speech(
            "The quick brown fox jumps over the lazy dog.", model="eleven_flash_v2_5"
        )
        target = next(
            v for v in await client.list_voices() if v["voice_id"] != VOICE_ID
        )
        if stream:
            chunks = client.stream_speech_to_speech(source.audio, target["voice_id"])
            audio = b"".join([c async for c in chunks])
        else:
            audio = (
                await client.speech_to_speech(source.audio, target["voice_id"])
            ).audio
        result = await client.transcribe(audio, language_code="en")

    assert "fox" in result["text"].lower()
