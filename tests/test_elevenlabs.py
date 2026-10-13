import inspect
from collections.abc import Callable
from contextlib import aclosing, nullcontext
from typing import get_args, get_type_hints
from unittest.mock import AsyncMock, MagicMock

import niquests
import pytest
from elevenlabs.music.client import AsyncMusicClient
from elevenlabs.speech_to_speech.client import AsyncSpeechToSpeechClient
from elevenlabs.speech_to_speech.types import SpeechToSpeechRequestFileFormat
from elevenlabs.speech_to_text.client import AsyncSpeechToTextClient
from elevenlabs.speech_to_text.types import (
    SpeechToTextConvertRequestTimestampsGranularity,
)
from elevenlabs.text_to_sound_effects.client import AsyncTextToSoundEffectsClient
from elevenlabs.text_to_speech.client import AsyncTextToSpeechClient
from elevenlabs.text_to_speech.types import TextToSpeechConvertRequestOutputFormat
from elevenlabs.types import (
    SpeechToTextCharacterResponseModel,
    SpeechToTextChunkResponseModel,
    SpeechToTextWordResponseModel,
    Voice as SdkVoice,
    VoiceSettings as SdkVoiceSettings,
)
from elevenlabs.voices.ivc.client import AsyncIvcClient

from padwan_ai import ElevenLabsClient
from padwan_ai.elevenlabs import (
    ElevenLabsAudio,
    ElevenLabsOutputFormat,
    ElevenLabsTranscription,
    ElevenLabsVoice,
    ElevenLabsWord,
    SpeechToSpeechOptions,
    VoiceSettings,
)
from padwan_ai.elevenlabs.client import (
    ElevenLabsCharacter,
    _MusicBody,
    _SoundBody,
    _SpeechBody,
)
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
        assert speech == ElevenLabsAudio(b"\x00\x01", "audio/pcm", "req-1")
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


async def test_transcribe_path(tmp_path, make_resp):
    audio = tmp_path / "clip.mp3"
    audio.write_bytes(b"RIFF")
    client, session = _client(make_resp(200, TRANSCRIPTION))

    await client.transcribe(audio)

    assert session.post.await_args.kwargs["files"][-1] == (
        "file",
        ("clip.mp3", b"RIFF", "audio/mpeg"),
    )


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
    ],
)
async def test_errors(status, payload, headers, ctx, make_resp):
    client, _ = _client(make_resp(status, payload, headers), voice_id="v")

    with ctx as exc:
        await client.generate_speech("Hi")
    if isinstance(exc.value, TooManyRequestsError):
        assert exc.value.retry_delay == 3


@pytest.mark.parametrize(
    "method, kwargs, path, body, params, ctx",
    [
        pytest.param(
            "generate_sound_effect",
            {"text": "door knock"},
            "sound-generation",
            {"text": "door knock", "model_id": "eleven_text_to_sound_v2"},
            None,
            nullcontext(),
            id="sound-defaults",
        ),
        pytest.param(
            "generate_sound_effect",
            {
                "text": "rain",
                "duration_seconds": 2.5,
                "prompt_influence": 0.7,
                "loop": True,
                "output_format": "pcm_24000",
            },
            "sound-generation",
            {
                "text": "rain",
                "model_id": "eleven_text_to_sound_v2",
                "duration_seconds": 2.5,
                "prompt_influence": 0.7,
                "loop": True,
            },
            {"output_format": "pcm_24000"},
            nullcontext(),
            id="sound-options",
        ),
        pytest.param(
            "compose_music",
            {"prompt": "calm piano", "music_length_ms": 10_000, "seed": 1},
            "music",
            {
                "model_id": "music_v1",
                "prompt": "calm piano",
                "music_length_ms": 10_000,
                "seed": 1,
            },
            None,
            nullcontext(),
            id="music-prompt",
        ),
        pytest.param(
            "compose_music",
            {"composition_plan": {"sections": []}, "force_instrumental": True},
            "music",
            {
                "model_id": "music_v1",
                "composition_plan": {"sections": []},
                "force_instrumental": True,
            },
            None,
            nullcontext(),
            id="music-plan",
        ),
        pytest.param(
            "compose_music",
            {},
            None,
            None,
            None,
            pytest.raises(ValueError),
            id="music-no-input",
        ),
        pytest.param(
            "compose_music",
            {"prompt": "x", "composition_plan": {}},
            None,
            None,
            None,
            pytest.raises(ValueError),
            id="music-two-inputs",
        ),
    ],
)
async def test_generate_audio(method, kwargs, path, body, params, ctx, make_resp):
    resp = make_resp(200, {}, {"content-type": "audio/mpeg"})
    resp.content = b"ID3"
    client, session = _client(resp)

    with ctx:
        assert await getattr(client, method)(**kwargs) == ElevenLabsAudio(
            b"ID3", "audio/mpeg"
        )
        session.post.assert_awaited_once_with(path, json=body, params=params)


@pytest.mark.parametrize(
    "status, chunks, early, ctx",
    [
        pytest.param(200, [b"ab", b"cd"], False, nullcontext(), id="ok"),
        pytest.param(200, [b"ab", b"cd"], True, nullcontext(), id="early-close"),
        pytest.param(
            401,
            None,
            False,
            pytest.raises(LLMError, match="401 Invalid key"),
            id="error-body",
        ),
    ],
)
async def test_stream_speech(status, chunks, early, ctx, make_resp):
    resp = make_resp(status, {})
    resp.close = AsyncMock()
    if status >= 400:
        resp.content = _awaitable(
            b'{"detail": {"status": "invalid_api_key", "message": "Invalid key"}}'
        )

    async def iter_content(_size):
        async def gen():
            for chunk in chunks or ():
                yield chunk

        return gen()

    resp.iter_content = iter_content
    client, session = _client(resp, voice_id="v")

    with ctx:
        got = []
        async with aclosing(client.stream_speech("Hi", seed=3)) as stream:
            async for chunk in stream:
                got.append(chunk)
                if early:
                    break
        assert got == (chunks[:1] if early else chunks)
    session.post.assert_awaited_once_with(
        "text-to-speech/v/stream",
        json={"text": "Hi", "model_id": "eleven_multilingual_v2", "seed": 3},
        params=None,
        stream=True,
    )
    resp.close.assert_awaited_once()


def _awaitable(value):
    async def get():
        return value

    return get()


@pytest.mark.parametrize(
    "files, kwargs, expected, ctx",
    [
        pytest.param(
            [b"RIFF", b"OggS"],
            {"description": "Narrator", "labels": {"accent": "fr"}},
            [
                ("name", (None, "Me")),
                ("description", (None, "Narrator")),
                ("labels", (None, '{"accent": "fr"}')),
                ("files", ("audio", b"RIFF", "application/octet-stream")),
                ("files", ("audio", b"OggS", "application/octet-stream")),
            ],
            nullcontext(),
            id="samples",
        ),
        pytest.param([], {}, None, pytest.raises(ValueError), id="no-samples"),
    ],
)
async def test_clone_voice(files, kwargs, expected, ctx, make_resp):
    client, session = _client(make_resp(200, {"voice_id": "new"}))

    with ctx:
        assert await client.clone_voice("Me", files, **kwargs) == "new"
        session.post.assert_awaited_once_with("voices/add", files=expected)


@pytest.mark.parametrize(
    "stream, kwargs, expected, ctx",
    [
        pytest.param(
            False,
            {},
            [
                ("model_id", (None, "eleven_multilingual_sts_v2")),
                ("audio", ("audio", b"RIFF", "application/octet-stream")),
            ],
            nullcontext(),
            id="defaults",
        ),
        pytest.param(
            True,
            {
                "voice_settings": {"stability": 0.5},
                "seed": 4,
                "remove_background_noise": True,
                "file_format": "pcm_s16le_16",
            },
            [
                ("model_id", (None, "eleven_multilingual_sts_v2")),
                ("voice_settings", (None, '{"stability": 0.5}')),
                ("seed", (None, "4")),
                ("remove_background_noise", (None, "true")),
                ("file_format", (None, "pcm_s16le_16")),
                ("audio", ("audio", b"RIFF", "application/octet-stream")),
            ],
            nullcontext(),
            id="stream-options",
        ),
        pytest.param(
            False, {"voice_id": None}, None, pytest.raises(ValueError), id="no-voice"
        ),
    ],
)
async def test_speech_to_speech(stream, kwargs, expected, ctx, make_resp):
    resp = make_resp(200, {}, {"content-type": "audio/mpeg"})
    resp.content = b"ID3"
    resp.close = AsyncMock()

    async def iter_content(_size):
        async def gen():
            yield b"ID3"

        return gen()

    resp.iter_content = iter_content
    client, session = _client(resp, voice_id=None if "voice_id" in kwargs else "v")
    kwargs.pop("voice_id", None)

    with ctx:
        if stream:
            out = b"".join(
                [c async for c in client.stream_speech_to_speech(b"RIFF", **kwargs)]
            )
            path, extra = "speech-to-speech/v/stream", {"stream": True}
        else:
            out = (await client.speech_to_speech(b"RIFF", **kwargs)).audio
            path, extra = "speech-to-speech/v", {}
        assert out == b"ID3"
        session.post.assert_awaited_once_with(
            path, files=expected, params=None, **extra
        )


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
    params = inspect.signature(method).parameters.values()
    names = {p.name for p in params if p.kind is not p.VAR_KEYWORD}
    return names - {"self", "request_options"}


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
        pytest.param(ElevenLabsVoice, set(SdkVoice.model_fields), id="Voice"),
        pytest.param(
            _SoundBody,
            _sdk_params(AsyncTextToSoundEffectsClient.convert),
            id="SoundBody",
        ),
        pytest.param(_MusicBody, _sdk_params(AsyncMusicClient.compose), id="MusicBody"),
        pytest.param(
            SpeechToSpeechOptions,
            _sdk_params(AsyncSpeechToSpeechClient.convert),
            id="SpeechToSpeechOptions",
        ),
    ],
)
def test_sdk_compat(local_type: type, sdk_keys: set[str]):
    """Every field in our TypedDicts exists on the elevenlabs SDK type."""
    for key in get_type_hints(local_type):
        assert key in sdk_keys, f"{local_type.__name__}.{key} not in SDK type"


@pytest.mark.parametrize(
    "method, sdk_method",
    [
        pytest.param(
            ElevenLabsClient.transcribe,
            AsyncSpeechToTextClient.convert,
            id="transcribe",
        ),
        pytest.param(ElevenLabsClient.clone_voice, AsyncIvcClient.create, id="clone"),
        pytest.param(
            ElevenLabsClient.speech_to_speech,
            AsyncSpeechToSpeechClient.convert,
            id="speech-to-speech",
        ),
    ],
)
def test_params_sdk_compat(method, sdk_method):
    """Our keyword options are SDK params (`model` maps to `model_id`)."""
    ours = {"model_id" if p == "model" else p for p in _sdk_params(method)}
    assert ours <= _sdk_params(sdk_method)


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
        pytest.param(
            get_type_hints(SpeechToSpeechOptions)["file_format"],
            SpeechToSpeechRequestFileFormat,
            id="sts-file-format",
        ),
    ],
)
def test_literal_sdk_compat(local: object, sdk: object):
    assert _literal_values(local) == _literal_values(sdk)
