import json
from contextlib import nullcontext
from typing import get_type_hints
from unittest.mock import AsyncMock, MagicMock

import pytest
from gradium.speech import TTSSetup

from padwan_ai import GradiumClient
from padwan_ai.errors import LLMError
from padwan_ai.gradium import GradiumSpeech
from padwan_ai.gradium.client import _SpeechBody

NDJSON = "\n".join(
    json.dumps(m)
    for m in (
        {"type": "text", "text": "Hello", "start_s": 0.5, "stream_id": 0},
        {"type": "end_text", "stop_s": 1.0, "stream_id": 0},
        {"type": "step", "vad": []},
        {"type": "text", "text": "world", "start_s": 1.2, "stream_id": 0},
    )
)


def _client(resp: MagicMock, **kwargs) -> tuple[GradiumClient, AsyncMock]:
    client = GradiumClient(api_key="secret", **kwargs)
    session = AsyncMock()
    session.post.return_value = resp
    client._session = session
    return client, session


@pytest.mark.parametrize(
    "client_voice, kwargs, body, ctx",
    [
        pytest.param(
            "v1",
            {},
            {
                "text": "Hi",
                "voice_id": "v1",
                "output_format": "wav",
                "only_audio": True,
                "model_name": "default",
            },
            nullcontext(),
            id="defaults",
        ),
        pytest.param(
            "v1",
            {
                "voice_id": "v2",
                "model": "tts-2",
                "output_format": "pcm_24000",
                "config": {"temp": 0.0, "padding_bonus": -1},
            },
            {
                "text": "Hi",
                "voice_id": "v2",
                "output_format": "pcm_24000",
                "only_audio": True,
                "model_name": "tts-2",
                "json_config": {"temp": 0.0, "padding_bonus": -1},
            },
            nullcontext(),
            id="overrides",
        ),
        pytest.param(None, {}, None, pytest.raises(ValueError), id="no-voice"),
    ],
)
async def test_generate_speech(client_voice, kwargs, body, ctx, make_resp):
    resp = make_resp(200, {}, {"content-type": "audio/wav"})
    resp.content = b"RIFF"
    client, session = _client(resp, voice_id=client_voice)

    with ctx:
        assert await client.generate_speech("Hi", **kwargs) == GradiumSpeech(
            b"RIFF", "audio/wav"
        )
        session.post.assert_awaited_once_with("post/speech/tts", json=body)


@pytest.mark.parametrize(
    "file_name, kwargs, content_type, json_config, ctx",
    [
        pytest.param(
            "a.wav", {}, "audio/wav", {"language": "any"}, nullcontext(), id="wav-path"
        ),
        pytest.param(
            "a.opus",
            {
                "language": "fr",
                "config": {"keywords": {"words": ["Padwan"], "boost": 3}},
            },
            "audio/ogg",
            {"keywords": {"words": ["Padwan"], "boost": 3}, "language": "fr"},
            nullcontext(),
            id="opus-with-config",
        ),
        pytest.param(
            None,
            {},
            "audio/wav",
            {"language": "any"},
            nullcontext(),
            id="bytes-default-wav",
        ),
        pytest.param(
            None,
            {"input_format": "pcm"},
            "audio/pcm",
            {"language": "any"},
            nullcontext(),
            id="bytes-pcm",
        ),
        pytest.param(
            "a.mp3", {}, None, None, pytest.raises(ValueError), id="unsupported-suffix"
        ),
    ],
)
async def test_transcribe(
    file_name, kwargs, content_type, json_config, ctx, tmp_path, make_resp
):
    resp = make_resp(200, {})
    resp.text = NDJSON
    client, session = _client(resp)
    file = b"AUDIO"
    if file_name:
        file = tmp_path / file_name
        file.write_bytes(b"AUDIO")

    with ctx:
        result = await client.transcribe(file, **kwargs)
        assert result == {
            "text": "Hello world",
            "segments": [
                {"text": "Hello", "start": 0.5, "end": 1.0},
                {"text": "world", "start": 1.2, "end": None},
            ],
        }
        call = session.post.await_args
        assert call.args == ("post/speech/asr",)
        assert call.kwargs["data"] == b"AUDIO"
        assert call.kwargs["headers"] == {"Content-Type": content_type}
        assert call.kwargs["params"]["model"] == "default"
        assert json.loads(call.kwargs["params"]["json_config"]) == json_config


@pytest.mark.parametrize(
    "status, text, match",
    [
        pytest.param(
            401,
            None,
            r"\[gradium\] 401 Invalid or expired API key",
            id="json-detail",
        ),
        pytest.param(
            500,
            "error from server 1008: API key is revoked or expired",
            r"\[gradium\] 500 error from server 1008: API key is revoked",
            id="http-error",
        ),
        pytest.param(
            200,
            '{"type": "text", "text": "Hi", "start_s": 0}\n'
            '{"type": "error", "message": "worker crashed"}',
            r"\[gradium\] worker crashed",
            id="in-stream-error",
        ),
    ],
)
async def test_transcribe_errors(status, text, match, make_resp):
    resp = make_resp(status, {"detail": "Invalid or expired API key"})
    if text is not None:
        resp.json.side_effect = ValueError
        resp.text = text
    client, _ = _client(resp)

    with pytest.raises(LLMError, match=match):
        await client.transcribe(b"AUDIO")


@pytest.mark.parametrize(
    "local_type, sdk_keys",
    [
        pytest.param(
            _SpeechBody,
            set(get_type_hints(TTSSetup)) | {"text", "only_audio"},
            id="SpeechBody",
        ),
    ],
)
def test_sdk_compat(local_type: type, sdk_keys: set[str]):
    """Every field in our request TypedDicts exists in the gradium SDK setup."""
    for key in get_type_hints(local_type):
        assert key in sdk_keys, f"{local_type.__name__}.{key} not in SDK type"
