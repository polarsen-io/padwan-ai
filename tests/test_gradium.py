import inspect
import json
from contextlib import nullcontext
from typing import get_type_hints
from unittest.mock import AsyncMock, MagicMock

import pytest
from gradium import voices
from gradium.speech import TTSSetup

from padwan_ai import GradiumClient
from padwan_ai.errors import LLMError, TooManyRequestsError
from padwan_ai.gradium import GRADIUM_ENDPOINT, GradiumSpeech
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
    "base_url, api_key, padwan_key, expected",
    [
        pytest.param(GRADIUM_ENDPOINT, None, None, "real-key", id="official"),
        pytest.param(
            "https://evil.example/api/", None, None, "no-key-required", id="other-host"
        ),
        pytest.param(
            "http://api.gradium.ai/api/", None, None, "no-key-required", id="plaintext"
        ),
        pytest.param(
            "https://evil.example/api/", None, "gw-key", "gw-key", id="padwan-key"
        ),
        pytest.param(
            "https://evil.example/api/", "explicit", "gw-key", "explicit", id="explicit"
        ),
    ],
)
def test_env_key_scoped_to_official_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    base_url: str,
    api_key: str | None,
    padwan_key: str | None,
    expected: str,
) -> None:
    monkeypatch.setenv("GRADIUM_API_KEY", "real-key")
    monkeypatch.delenv("PADWAN_API_KEY", raising=False)
    if padwan_key is not None:
        monkeypatch.setenv("PADWAN_API_KEY", padwan_key)
    assert GradiumClient(base_url=base_url, api_key=api_key)._api_key == expected


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
                "json_config": '{"temp": 0.0, "padding_bonus": -1}',
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
        result = await client.transcribe(file=file, **kwargs)
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
        pytest.param(
            200,
            '{"type": "text", "text": "Hi"}',
            r"\[gradium\] Malformed transcription line",
            id="missing-key",
        ),
        pytest.param(
            200, "not json", r"\[gradium\] Malformed transcription line", id="not-json"
        ),
        pytest.param(
            429,
            "slow down",
            None,
            id="rate-limit",
        ),
    ],
)
async def test_transcribe_errors(status, text, match, make_resp):
    resp = make_resp(status, {"detail": "Invalid or expired API key"})
    if text is not None:
        resp.json.side_effect = ValueError
        resp.text = text
    client, _ = _client(resp)

    error = TooManyRequestsError if match is None else LLMError
    with pytest.raises(error, match=match):
        await client.transcribe(file=b"AUDIO")


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


def _awaitable(value):
    async def get():
        return value

    return get()


@pytest.mark.parametrize(
    "status, chunks, ctx",
    [
        pytest.param(200, [b"RI", b"FF"], nullcontext(), id="ok"),
        pytest.param(
            500,
            None,
            pytest.raises(LLMError, match=r"500 error from server 1008: revoked"),
            id="plain-text-error",
        ),
    ],
)
async def test_stream_speech(status, chunks, ctx, make_resp):
    resp = make_resp(status, {})
    resp.close = AsyncMock()
    if status >= 400:
        resp.content = _awaitable(b"error from server 1008: revoked")

    async def iter_content(_size):
        async def gen():
            for chunk in chunks or ():
                yield chunk

        return gen()

    resp.iter_content = iter_content
    client, session = _client(resp, voice_id="v")

    with ctx:
        assert [c async for c in client.stream_speech("Hi")] == chunks
    session.post.assert_awaited_once_with(
        "post/speech/tts",
        json={
            "text": "Hi",
            "voice_id": "v",
            "output_format": "wav",
            "only_audio": True,
            "model_name": "default",
        },
        stream=True,
    )
    resp.close.assert_awaited_once()


@pytest.mark.parametrize(
    "file_name, kwargs, payload, expected, ctx",
    [
        pytest.param(
            "me.wav",
            {"description": "Narrator", "start_s": 1.5},
            {"uid": "new"},
            [
                ("audio_file", ("me.wav", b"RIFF", "audio/wav")),
                ("name", (None, "Me")),
                ("language", (None, "fr")),
                ("input_format", (None, "wav")),
                ("description", (None, "Narrator")),
                ("start_s", (None, "1.5")),
            ],
            nullcontext(),
            id="path",
        ),
        pytest.param(
            None,
            {"input_format": "mp3"},
            {"uid": "new"},
            [
                ("audio_file", ("audio.mp3", b"RIFF", "audio/mp3")),
                ("name", (None, "Me")),
                ("language", (None, "fr")),
                ("input_format", (None, "mp3")),
            ],
            nullcontext(),
            id="bytes",
        ),
        pytest.param(None, {}, None, None, pytest.raises(ValueError), id="no-format"),
        pytest.param(
            "me.wav",
            {},
            {"uid": None, "error": "audio too short"},
            None,
            pytest.raises(LLMError, match="audio too short"),
            id="error-in-body",
        ),
    ],
)
async def test_clone_voice(
    file_name, kwargs, payload, expected, ctx, tmp_path, make_resp
):
    client, session = _client(make_resp(201, payload))
    file = b"RIFF"
    if file_name:
        file = tmp_path / file_name
        file.write_bytes(b"RIFF")

    with ctx:
        assert await client.clone_voice("Me", file, language="fr", **kwargs) == "new"
    if expected is not None:
        session.post.assert_awaited_once_with("voices/", files=expected)


@pytest.mark.parametrize(
    "kwargs, body, ctx",
    [
        pytest.param(
            {"name": "New", "start_s": 0.0},
            {"name": "New", "start_s": 0.0},
            nullcontext(),
            id="partial",
        ),
        pytest.param({}, None, pytest.raises(ValueError), id="nothing-to-update"),
    ],
)
async def test_update_voice(kwargs, body, ctx, make_resp):
    client, session = _client(MagicMock())
    session.put.return_value = make_resp(200, {"uid": "v1", "name": "New"})

    with ctx:
        assert (await client.update_voice("v1", **kwargs))["name"] == "New"
        session.put.assert_awaited_once_with("voices/v1", json=body)


@pytest.mark.parametrize(
    "method, sdk_fn",
    [
        pytest.param(GradiumClient.clone_voice, voices.create, id="clone"),
        pytest.param(GradiumClient.update_voice, voices.update, id="update"),
        pytest.param(GradiumClient.list_voices, voices.get, id="list"),
    ],
)
def test_params_sdk_compat(method, sdk_fn):
    """Our parameters are SDK params (`voice_id` is `voice_uid`, the sample `audio_file`)."""
    renames = {"voice_id": "voice_uid", "file": "audio_file"}
    ours = {renames.get(p, p) for p in inspect.signature(method).parameters}
    assert ours - {"self"} <= set(inspect.signature(sdk_fn).parameters)
