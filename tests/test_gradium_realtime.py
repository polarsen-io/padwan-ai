import base64
import json
from contextlib import nullcontext
from typing import get_type_hints
from unittest.mock import AsyncMock, MagicMock

import pytest
from gradium.speech import S2SSetup, STTSetup, TTSSetup

from padwan_ai.errors import LLMError
from padwan_ai.gradium import (
    GradiumRealtimeS2SClient,
    GradiumRealtimeSTTClient,
    GradiumRealtimeTTSClient,
    GradiumTTSConnection,
)
from padwan_ai.gradium.realtime import _S2SSetup, _STTSetup, _TTSSetup
from tests.test_realtime import FakeExt

READY = json.dumps({"type": "ready", "request_id": "r1"})
EOS = json.dumps({"type": "end_of_stream"})


def _audio(data: bytes) -> str:
    return json.dumps({"type": "audio", "audio": base64.b64encode(data).decode()})


def _session(ext: FakeExt | None, status: int = 101) -> AsyncMock:
    resp = MagicMock(status_code=status, extension=ext)
    return AsyncMock(get=AsyncMock(return_value=resp))


TOKENS = ["Hel", "lo", " world", ".", " How", " are", " you?"]


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
    ext = FakeExt(
        [
            _audio(b"a1"),
            json.dumps({"type": "text", "text": "Hello"}),
            _audio(b"a2"),
            EOS,
        ]
    )
    conn = GradiumTTSConnection(ext)

    assert [a async for a in conn.stream(texts())] == [b"a1", b"a2"]
    # the server joins messages with a space, so words and punctuation stay whole
    assert [json.loads(m) for m in ext.sent] == [
        {"type": "text", "text": "Hello"},
        {"type": "text", "text": "world."},
        {"type": "text", "text": "How"},
        {"type": "text", "text": "are"},
        {"type": "text", "text": "you?"},
        {"type": "end_of_stream"},
    ]


@pytest.mark.parametrize(
    "client, route, setup",
    [
        pytest.param(
            GradiumRealtimeTTSClient(
                api_key="k", voice_id="v1", config={"temp": 0.3}, pronunciation_id="p1"
            ),
            "speech/tts",
            {
                "type": "setup",
                "model_name": "default",
                "voice_id": "v1",
                "output_format": "pcm",
                "json_config": {"temp": 0.3},
                "pronunciation_id": "p1",
            },
            id="tts",
        ),
        pytest.param(
            GradiumRealtimeSTTClient(
                api_key="k", language="fr", config={"delay_in_frames": 16}
            ),
            "speech/asr",
            {
                "type": "setup",
                "model_name": "default",
                "input_format": "pcm",
                "json_config": {"delay_in_frames": 16, "language": "fr"},
            },
            id="stt",
        ),
        pytest.param(
            GradiumRealtimeS2SClient(api_key="k", voice_id="v1", target_language="en"),
            "speech/s2s",
            {
                "type": "setup",
                "model_name": "s2s-translate",
                "stt_model_name": "stt-translate",
                "tts_model_name": "default",
                "input_format": "pcm",
                "output_format": "pcm",
                "json_config": {"target_language": "en"},
                "voice_id": "v1",
            },
            id="s2s",
        ),
    ],
)
async def test_connect_setup(client, route, setup):
    ext = FakeExt([READY])
    client._session = _session(ext)

    async with client._connect() as conn:
        assert conn.ready == {"type": "ready", "request_id": "r1"}

    client._session.get.assert_awaited_once_with(
        f"wss://api.gradium.ai/api/{route}", timeout=30.0
    )
    assert [json.loads(m) for m in ext.sent] == [setup]
    assert ext.closed


@pytest.mark.parametrize(
    "first, status, ctx",
    [
        pytest.param(READY, 101, nullcontext(), id="ready"),
        pytest.param(
            json.dumps({"type": "error", "message": "bad key", "code": 1008}),
            101,
            pytest.raises(LLMError, match="1008 bad key"),
            id="error-frame",
        ),
        pytest.param(
            None, 101, pytest.raises(LLMError, match="closed before ready"), id="closed"
        ),
        pytest.param(
            None, 403, pytest.raises(LLMError, match="status 403"), id="no-upgrade"
        ),
    ],
)
async def test_stt_stream(first, status, ctx):
    ext = FakeExt(
        [
            first,
            json.dumps({"type": "text", "text": "Hello", "start_s": 0.5}),
            json.dumps({"type": "step", "vad": []}),
            EOS,
        ]
    )
    client = GradiumRealtimeSTTClient(api_key="k")
    client._session = _session(ext if status == 101 else None, status)

    with ctx:
        async with client._connect() as conn:
            await conn.flush(3)
            messages = [m async for m in conn.stream([b"\x00\x01"])]
        assert [conn.transcript(m) for m in messages] == ["Hello", None]
        assert [json.loads(m) for m in ext.sent][1:] == [
            {"type": "flush", "flush_id": 3},
            {"type": "audio", "audio": "AAE="},
            {"type": "end_of_stream"},
        ]
    assert ext.closed == (status == 101)


@pytest.mark.parametrize(
    "local_type, sdk_type",
    [
        pytest.param(_TTSSetup, TTSSetup, id="TTSSetup"),
        pytest.param(_STTSetup, STTSetup, id="STTSetup"),
        pytest.param(_S2SSetup, S2SSetup, id="S2SSetup"),
    ],
)
def test_sdk_compat(local_type: type, sdk_type: type):
    """Every field of our setup messages exists on the gradium SDK setup (plus `type`)."""
    sdk_keys = set(get_type_hints(sdk_type)) | {"type"}
    for key in get_type_hints(local_type):
        assert key in sdk_keys, f"{local_type.__name__}.{key} not in SDK type"
