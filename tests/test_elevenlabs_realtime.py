import base64
import json
from contextlib import nullcontext
from typing import get_args, get_type_hints
from unittest.mock import AsyncMock, MagicMock

import pytest
from elevenlabs.realtime.scribe import AudioFormat, RealtimeAudioOptions
from elevenlabs.types import InitializeConnection, InputAudioChunkPayload, SendText

from padwan_ai.elevenlabs import (
    ElevenLabsRealtimeAudioFormat,
    ElevenLabsRealtimeSTTClient,
    ElevenLabsRealtimeTTSClient,
    ElevenLabsTTSConnection,
)
from padwan_ai.elevenlabs.realtime import _STTChunk, _TTSInit, _TTSText
from padwan_ai.errors import LLMError, QuotaExceededError
from tests.test_realtime import FakeExt


def _audio(data: bytes) -> str:
    return json.dumps({"audio": base64.b64encode(data).decode()})


def _session(ext: FakeExt) -> AsyncMock:
    resp = MagicMock(status_code=101, extension=ext)
    return AsyncMock(get=AsyncMock(return_value=resp))


TOKENS = ["Hel", "lo", " world", ".", " "]


async def _async_tokens():
    for token in TOKENS:
        yield token


@pytest.mark.parametrize(
    "texts",
    [
        pytest.param(lambda: iter(TOKENS), id="sync"),
        pytest.param(_async_tokens, id="async"),
    ],
)
async def test_tts_stream(texts):
    ext = FakeExt([_audio(b"a1"), _audio(b"a2"), json.dumps({"isFinal": True})])
    conn = ElevenLabsTTSConnection(ext)

    assert [a async for a in conn.stream(texts())] == [b"a1", b"a2"]
    # tokens are regrouped on word boundaries, then the empty text ends the input
    assert [json.loads(m) for m in ext.sent] == [
        {"text": "Hello "},
        {"text": "world. "},
        {"text": ""},
    ]


async def test_tts_connect():
    ext = FakeExt()
    client = ElevenLabsRealtimeTTSClient(
        api_key="k",
        voice_id="v1",
        output_format="pcm_16000",
        voice_settings={"stability": 0.5},
        chunk_length_schedule=[50, 120],
    )
    client._session = _session(ext)

    async with client._connect() as conn:
        await conn.send_text("Hi", flush=True)

    client._session.get.assert_awaited_once_with(
        "wss://api.elevenlabs.io/v1/text-to-speech/v1/stream-input",
        params={"model_id": "eleven_flash_v2_5", "output_format": "pcm_16000"},
        timeout=30.0,
    )
    assert [json.loads(m) for m in ext.sent] == [
        {
            "text": " ",
            "voice_settings": {"stability": 0.5},
            "generation_config": {"chunk_length_schedule": [50, 120]},
        },
        {"text": "Hi ", "flush": True},
    ]
    assert ext.closed


@pytest.mark.parametrize(
    "first, ctx",
    [
        pytest.param(
            {"message_type": "session_started", "session_id": "s"},
            nullcontext(),
            id="started",
        ),
        pytest.param(
            {"message_type": "auth_error", "error": "bad key"},
            pytest.raises(LLMError, match="auth_error: bad key"),
            id="auth-error",
        ),
        pytest.param(
            {"message_type": "quota_exceeded", "error": "no credits"},
            pytest.raises(QuotaExceededError),
            id="quota",
        ),
        pytest.param(
            None, pytest.raises(LLMError, match="session_started"), id="closed"
        ),
    ],
)
async def test_stt_session(first, ctx):
    ext = FakeExt(
        [
            json.dumps(first) if first else None,
            json.dumps({"message_type": "partial_transcript", "text": "Hel"}),
            json.dumps({"message_type": "committed_transcript", "text": "Hello"}),
        ]
    )
    client = ElevenLabsRealtimeSTTClient(
        api_key="k", audio_format="pcm_24000", language_code="en", keyterms=["Padwan"]
    )
    client._session = _session(ext)

    with ctx:
        async with client._connect() as conn:
            await conn.append_audio(b"\x00\x01", previous_text="Earlier")
            await conn.commit()
            messages = [m async for m in conn]
        assert [conn.transcript(m) for m in messages] == ["Hel", "Hello"]
        assert [conn.is_committed(m) for m in messages] == [False, True]
        assert [json.loads(m) for m in ext.sent] == [
            {
                "message_type": "input_audio_chunk",
                "audio_base_64": "AAE=",
                "commit": False,
                "sample_rate": 24000,
                "previous_text": "Earlier",
            },
            {
                "message_type": "input_audio_chunk",
                "audio_base_64": "",
                "commit": True,
                "sample_rate": 24000,
            },
        ]
        client._session.get.assert_awaited_once_with(
            "wss://api.elevenlabs.io/v1/speech-to-text/realtime",
            params=[
                ("model_id", "scribe_v2_realtime"),
                ("audio_format", "pcm_24000"),
                ("commit_strategy", "manual"),
                ("language_code", "en"),
                ("keyterms", "Padwan"),
            ],
            timeout=30.0,
        )
    assert ext.closed


async def test_no_upgrade_raises():
    client = ElevenLabsRealtimeSTTClient(api_key="k")
    client._session = AsyncMock(
        get=AsyncMock(return_value=MagicMock(status_code=403, extension=None))
    )
    with pytest.raises(LLMError, match="status 403"):
        async with client._connect():
            pass


@pytest.mark.parametrize(
    "local_type, sdk_keys",
    [
        pytest.param(_TTSInit, set(InitializeConnection.model_fields), id="TTSInit"),
        pytest.param(_TTSText, set(SendText.model_fields), id="TTSText"),
        pytest.param(
            _STTChunk, set(InputAudioChunkPayload.model_fields), id="STTChunk"
        ),
    ],
)
def test_sdk_compat(local_type: type, sdk_keys: set[str]):
    """Every field in our WebSocket messages exists on the elevenlabs SDK type."""
    for key in get_type_hints(local_type):
        assert key in sdk_keys, f"{local_type.__name__}.{key} not in SDK type"


def test_stt_params_sdk_compat():
    client = ElevenLabsRealtimeSTTClient(
        api_key="k",
        language_code="en",
        include_timestamps=True,
        keyterms=["a"],
        vad_silence_threshold_secs=1.0,
        vad_threshold=0.5,
        min_speech_duration_ms=100,
        min_silence_duration_ms=100,
    )
    sdk_keys = (
        RealtimeAudioOptions.__required_keys__ | RealtimeAudioOptions.__optional_keys__
    )
    assert {key for key, _ in client.connect_params()} <= sdk_keys
    assert set(get_args(ElevenLabsRealtimeAudioFormat)) == {
        f.value for f in AudioFormat
    }
