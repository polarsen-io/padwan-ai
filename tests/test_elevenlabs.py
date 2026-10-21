import inspect
from collections.abc import Callable
from contextlib import nullcontext
from typing import get_args, get_type_hints
from unittest.mock import AsyncMock, MagicMock

import niquests
import pytest
from elevenlabs.speech_to_text.client import AsyncSpeechToTextClient
from elevenlabs.speech_to_text.types import (
    SpeechToTextConvertRequestTimestampsGranularity,
)
from elevenlabs.text_to_speech.client import AsyncTextToSpeechClient
from elevenlabs.text_to_speech.types import TextToSpeechConvertRequestOutputFormat
from elevenlabs.types import (
    SpeechToTextCharacterResponseModel,
    SpeechToTextChunkResponseModel,
    SpeechToTextWordResponseModel,
    VoiceSettings as SdkVoiceSettings,
)

from padwan_ai import ElevenLabsClient
from padwan_ai.elevenlabs import (
    ElevenLabsOutputFormat,
    ElevenLabsSpeech,
    ElevenLabsTranscription,
    ElevenLabsWord,
    VoiceSettings,
)
from padwan_ai.elevenlabs.client import ElevenLabsCharacter, _SpeechBody
from padwan_ai.errors import LLMError, QuotaExceededError, TooManyRequestsError

TRANSCRIPTION = {
    "language_code": "en",
    "language_probability": 0.98,
    "text": "Hello",
    "words": [
        {"text": "Hello", "type": "word", "logprob": -0.1, "start": 0.0, "end": 0.4}
    ],
}


def _client(resp: MagicMock, **kwargs) -> tuple[ElevenLabsClient, AsyncMock]:
    client = ElevenLabsClient(api_key="secret", **kwargs)
    session = AsyncMock()
    session.post.return_value = resp
    client._session = session
    return client, session


@pytest.mark.parametrize(
    "client_voice, kwargs, path, body, params, ctx",
    [
        pytest.param(
            "default-voice",
            {},
            "text-to-speech/default-voice",
            {"text": "Hi", "model_id": "eleven_multilingual_v2"},
            None,
            nullcontext(),
            id="client-default-voice",
        ),
        pytest.param(
            "default-voice",
            {
                "voice_id": "other",
                "model": "eleven_v3",
                "output_format": "pcm_24000",
                "language_code": "fr",
                "voice_settings": {"stability": 0.3},
                "seed": 7,
                "previous_request_ids": ("req-0",),
            },
            "text-to-speech/other",
            {
                "text": "Hi",
                "model_id": "eleven_v3",
                "language_code": "fr",
                "voice_settings": {"stability": 0.3},
                "seed": 7,
                "previous_request_ids": ["req-0"],
            },
            {"output_format": "pcm_24000"},
            nullcontext(),
            id="overrides",
        ),
        pytest.param(
            None, {}, None, None, None, pytest.raises(ValueError), id="no-voice"
        ),
    ],
)
async def test_generate_speech(
    client_voice, kwargs, path, body, params, ctx, make_resp
):
    resp = make_resp(200, {}, {"content-type": "audio/pcm", "request-id": "req-1"})
    resp.content = b"\x00\x01"
    client, session = _client(resp, voice_id=client_voice)

    with ctx:
        speech = await client.generate_speech("Hi", **kwargs)
        assert speech == ElevenLabsSpeech(b"\x00\x01", "audio/pcm", "req-1")
        session.post.assert_awaited_once_with(path, json=body, params=params)


@pytest.mark.parametrize(
    "kwargs, expected, ctx",
    [
        pytest.param(
            {"file": b"RIFF", "diarize": True, "keyterms": ["Padwan", "Polarsen"]},
            [
                ("model_id", (None, "scribe_v2")),
                ("diarize", (None, "true")),
                ("keyterms", (None, "Padwan")),
                ("keyterms", (None, "Polarsen")),
                ("file", ("audio", b"RIFF", "application/octet-stream")),
            ],
            nullcontext(),
            id="bytes",
        ),
        pytest.param(
            {
                "source_url": "https://x/a.mp3",
                "tag_audio_events": False,
                "num_speakers": 2,
                "timestamps_granularity": "character",
            },
            [
                ("model_id", (None, "scribe_v2")),
                ("source_url", (None, "https://x/a.mp3")),
                ("num_speakers", (None, "2")),
                ("tag_audio_events", (None, "false")),
                ("timestamps_granularity", (None, "character")),
            ],
            nullcontext(),
            id="source-url",
        ),
        pytest.param({}, None, pytest.raises(ValueError), id="no-source"),
        pytest.param(
            {"file": b"RIFF", "source_url": "https://x/a.mp3"},
            None,
            pytest.raises(ValueError),
            id="two-sources",
        ),
    ],
)
async def test_transcribe(kwargs, expected, ctx, make_resp):
    client, session = _client(make_resp(200, TRANSCRIPTION))

    with ctx:
        assert await client.transcribe(**kwargs) == TRANSCRIPTION
        session.post.assert_awaited_once_with("speech-to-text", files=expected)


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        pytest.param({}, ("clip.mp3", b"RIFF", "audio/mpeg"), id="from-path"),
        pytest.param(
            {"filename": "clip.ogg", "content_type": "audio/ogg"},
            ("clip.ogg", b"RIFF", "audio/ogg"),
            id="overrides",
        ),
    ],
)
async def test_transcribe_path(tmp_path, make_resp, kwargs, expected):
    audio = tmp_path / "clip.mp3"
    audio.write_bytes(b"RIFF")
    client, session = _client(make_resp(200, TRANSCRIPTION))

    await client.transcribe(file=audio, **kwargs)

    assert session.post.await_args.kwargs["files"][-1] == ("file", expected)


@pytest.mark.parametrize(
    "status, payload, headers, ctx",
    [
        pytest.param(
            422,
            {"detail": [{"loc": ["body", "text"], "msg": "field required"}]},
            None,
            pytest.raises(LLMError, match=r"\[elevenlabs\] 422 field required"),
            id="validation",
        ),
        pytest.param(
            401,
            {"detail": {"status": "quota_exceeded", "message": "No credits left"}},
            None,
            pytest.raises(QuotaExceededError),
            id="quota",
        ),
        pytest.param(
            401,
            {"detail": {"status": "invalid_api_key", "message": "Invalid key"}},
            None,
            pytest.raises(LLMError, match="401 Invalid key"),
            id="auth",
        ),
        pytest.param(
            429,
            {"detail": {"status": "too_many_concurrent_requests", "message": "Slow"}},
            {"retry-after": "3"},
            pytest.raises(TooManyRequestsError),
            id="rate-limit",
        ),
        pytest.param(
            429,
            "<html>Too Many Requests</html>",
            {"retry-after": "Wed, 21 Oct 2026 10:00:00 GMT"},
            pytest.raises(TooManyRequestsError),
            id="rate-limit-http-date-no-json",
        ),
    ],
)
async def test_errors(status, payload, headers, ctx, make_resp):
    resp = make_resp(status, payload, headers)
    if not isinstance(payload, dict):
        resp.json.side_effect = ValueError("not json")
    client, _ = _client(resp, voice_id="v")

    with ctx as exc:
        await client.generate_speech("Hi")
    if isinstance(exc.value, TooManyRequestsError):
        assert exc.value.retry_delay >= 1
        if headers == {"retry-after": "3"}:
            assert exc.value.retry_delay == 3


async def test_multipart_wire_format():
    """`None` filenames must encode as plain form fields, not file parts."""
    client = ElevenLabsClient(api_key="secret")
    sent = []

    async def capture(url, files):
        sent.append(niquests.Request("POST", "https://x/" + url, files=files).prepare())
        resp = MagicMock()
        resp.raise_for_status.return_value = resp
        resp.json.return_value = TRANSCRIPTION
        return resp

    client._session = MagicMock(post=capture)
    await client.transcribe(source_url="https://x/a.mp3")

    body = sent[0].body.decode()
    assert sent[0].headers["Content-Type"].startswith("multipart/form-data")
    assert 'name="source_url"\r\n\r\nhttps://x/a.mp3' in body
    assert "filename" not in body


def _literal_values(tp: object) -> set[str]:
    """Literal members of an SDK alias like `Literal[...] | Any`."""
    return {v for arg in get_args(tp) for v in get_args(arg)} or set(get_args(tp))


def _sdk_params(method: Callable[..., object]) -> set[str]:
    return set(inspect.signature(method).parameters) - {"self", "request_options"}


@pytest.mark.parametrize(
    "local_type, sdk_keys",
    [
        pytest.param(
            VoiceSettings, set(SdkVoiceSettings.model_fields), id="VoiceSettings"
        ),
        pytest.param(
            _SpeechBody,
            _sdk_params(AsyncTextToSpeechClient.convert) | {"text"},
            id="SpeechBody",
        ),
        pytest.param(
            ElevenLabsTranscription,
            set(SpeechToTextChunkResponseModel.model_fields),
            id="Transcription",
        ),
        pytest.param(
            ElevenLabsWord, set(SpeechToTextWordResponseModel.model_fields), id="Word"
        ),
        pytest.param(
            ElevenLabsCharacter,
            set(SpeechToTextCharacterResponseModel.model_fields),
            id="Character",
        ),
    ],
)
def test_sdk_compat(local_type: type, sdk_keys: set[str]):
    """Every field in our TypedDicts exists on the elevenlabs SDK type."""
    for key in get_type_hints(local_type):
        assert key in sdk_keys, f"{local_type.__name__}.{key} not in SDK type"


def test_transcribe_params_sdk_compat():
    """`transcribe` options are SDK speech-to-text params, bar the padwan-wide upload/language names."""
    renamed = {"model": "model_id", "language": "language_code"}
    local = {"filename", "content_type"}
    ours = {renamed.get(p, p) for p in _sdk_params(ElevenLabsClient.transcribe) - local}
    assert ours <= _sdk_params(AsyncSpeechToTextClient.convert)


@pytest.mark.parametrize(
    "local, sdk",
    [
        pytest.param(
            ElevenLabsOutputFormat,
            TextToSpeechConvertRequestOutputFormat,
            id="output-format",
        ),
        pytest.param(
            get_type_hints(ElevenLabsClient.transcribe)["timestamps_granularity"],
            SpeechToTextConvertRequestTimestampsGranularity,
            id="timestamps-granularity",
        ),
    ],
)
def test_literal_sdk_compat(local: object, sdk: object):
    assert _literal_values(local) == _literal_values(sdk)
