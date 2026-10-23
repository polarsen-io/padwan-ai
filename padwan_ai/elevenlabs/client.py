import dataclasses
from collections.abc import AsyncGenerator, Mapping, Sequence
from contextlib import aclosing
from dataclasses import field
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Literal,
    NotRequired,
    TypedDict,
    Unpack,
    cast,
    get_args,
)

import niquests
from niquests.typing import MultiPartFilesType
from urllib3.util.retry import Retry

from .._base import StandaloneClientMixin, env_api_key_for_base_url, standalone_retry
from .._json import dumps as _json_dumps
from ..content import _read_audio
from ..errors import (
    Provider,
)

ElevenLabsTTSModel = Literal[
    "eleven_v4",
    "eleven_v4_turbo",
    "eleven_v3",
    "eleven_v3_conversational",
    "eleven_multilingual_v2",
    "eleven_flash_v2_5",
    "eleven_flash_v2",
]
ElevenLabsSTTModel = Literal["scribe_v2", "scribe_v2_medical"]
ElevenLabsRealtimeSTTModel = Literal["scribe_v2_realtime"]
ElevenLabsSTSModel = Literal["eleven_multilingual_sts_v2", "eleven_english_sts_v2"]
ElevenLabsModel = (
    ElevenLabsTTSModel
    | ElevenLabsSTTModel
    | ElevenLabsRealtimeSTTModel
    | ElevenLabsSTSModel
)

ElevenLabsOutputFormat = Literal[
    "alaw_8000",
    "mp3_22050_32",
    "mp3_24000_48",
    "mp3_44100_32",
    "mp3_44100_64",
    "mp3_44100_96",
    "mp3_44100_128",
    "mp3_44100_192",
    "opus_48000_32",
    "opus_48000_64",
    "opus_48000_96",
    "opus_48000_128",
    "opus_48000_192",
    "pcm_8000",
    "pcm_16000",
    "pcm_22050",
    "pcm_24000",
    "pcm_32000",
    "pcm_44100",
    "pcm_48000",
    "ulaw_8000",
    "wav_8000",
    "wav_16000",
    "wav_22050",
    "wav_24000",
    "wav_32000",
    "wav_44100",
    "wav_48000",
]

ELEVENLABS_MODELS: set[str] = (
    set(get_args(ElevenLabsTTSModel))
    | set(get_args(ElevenLabsSTTModel))
    | set(get_args(ElevenLabsRealtimeSTTModel))
    | set(get_args(ElevenLabsSTSModel))
)
ELEVENLABS_ENDPOINT = "https://api.elevenlabs.io/v1/"

__all__ = (
    "ELEVENLABS_ENDPOINT",
    "ELEVENLABS_MODELS",
    "ElevenLabsClient",
    "ElevenLabsModel",
    "ElevenLabsOutputFormat",
    "ElevenLabsRealtimeSTTModel",
    "ElevenLabsSTSModel",
    "ElevenLabsSTTModel",
    "ElevenLabsAudio",
    "ElevenLabsTTSModel",
    "ElevenLabsTranscription",
    "ElevenLabsVoice",
    "ElevenLabsWord",
    "SpeechOptions",
    "SpeechToSpeechOptions",
    "VoiceSettings",
)


# niquests types omit the None filename it encodes as a plain form field
type _Part = tuple[str, tuple[str | None, str | bytes] | tuple[str, bytes, str]]


class VoiceSettings(TypedDict, total=False):
    """Per-request override of the voice's stored settings."""

    stability: float
    similarity_boost: float
    style: float
    speed: float
    use_speaker_boost: bool


class SpeechOptions(TypedDict, total=False):
    """Optional text-to-speech settings shared by `generate_speech` and `stream_speech`."""

    language_code: str
    voice_settings: VoiceSettings
    seed: int
    previous_text: str
    next_text: str
    previous_request_ids: Sequence[str]


class _SpeechBody(TypedDict, total=False):
    text: str
    model_id: str
    language_code: str
    voice_settings: VoiceSettings
    seed: int
    previous_text: str
    next_text: str
    previous_request_ids: list[str]


class SpeechToSpeechOptions(TypedDict, total=False):
    """Optional settings for `speech_to_speech`; `file_format="pcm_s16le_16"` skips decoding raw 16 kHz PCM input."""

    voice_settings: VoiceSettings
    seed: int
    remove_background_noise: bool
    file_format: Literal["pcm_s16le_16", "other"]


class _SoundBody(TypedDict, total=False):
    text: str
    model_id: str
    duration_seconds: float
    prompt_influence: float
    loop: bool


class _MusicBody(TypedDict, total=False):
    prompt: str
    composition_plan: Mapping[str, Any]
    music_length_ms: int
    model_id: str
    seed: int
    force_instrumental: bool


class ElevenLabsVoice(TypedDict):
    voice_id: str
    name: str
    category: NotRequired[str]
    description: NotRequired[str | None]
    labels: NotRequired[dict[str, str]]
    preview_url: NotRequired[str | None]
    settings: NotRequired[VoiceSettings | None]


class ElevenLabsCharacter(TypedDict):
    text: str
    start: float
    end: float


class ElevenLabsWord(TypedDict):
    text: str
    type: Literal["word", "spacing", "audio_event"]
    logprob: float
    start: float | None
    end: float | None
    speaker_id: NotRequired[str | None]
    characters: NotRequired[list[ElevenLabsCharacter] | None]


class ElevenLabsTranscription(TypedDict):
    language_code: str
    language_probability: float
    text: str
    words: list[ElevenLabsWord]
    transcription_id: NotRequired[str | None]
    audio_duration_secs: NotRequired[float | None]


@dataclasses.dataclass(frozen=True, slots=True)
class ElevenLabsAudio:
    """Generated audio; for speech, pass `request_id` as `previous_request_ids` to stitch the next chunk."""

    audio: bytes
    mime_type: str
    request_id: str | None = None


def _speech_body(text: str, model: str, options: SpeechOptions) -> _SpeechBody:
    body: _SpeechBody = {"text": text, "model_id": model}
    for key in (
        "language_code",
        "voice_settings",
        "seed",
        "previous_text",
        "next_text",
    ):
        if (value := options.get(key)) is not None:
            body[key] = value
    if (ids := options.get("previous_request_ids")) is not None:
        body["previous_request_ids"] = list(ids)
    return body


async def _sts_parts(
    audio: str | Path | bytes,
    model: str,
    options: SpeechToSpeechOptions,
) -> MultiPartFilesType:
    fields: list[tuple[str, str]] = [("model_id", model)]
    if (settings := options.get("voice_settings")) is not None:
        fields.append(("voice_settings", _json_dumps(settings)))
    if (seed := options.get("seed")) is not None:
        fields.append(("seed", str(seed)))
    if options.get("remove_background_noise"):
        fields.append(("remove_background_noise", "true"))
    if (file_format := options.get("file_format")) is not None:
        fields.append(("file_format", file_format))
    parts: list[_Part] = [(name, (None, value)) for name, value in fields]
    parts.append(("audio", await _read_audio(audio)))
    return cast("MultiPartFilesType", parts)


@dataclasses.dataclass
class ElevenLabsClient(StandaloneClientMixin):
    """Async client for ElevenLabs text-to-speech and speech-to-text.

    Experimental: the interface and typed payloads may change between minor releases.

    https://elevenlabs.io/docs/api-reference
    """

    provider: ClassVar[Provider] = "elevenlabs"
    voice_id: str | None = None
    """Default voice for `generate_speech`; find IDs in the ElevenLabs voice library."""
    timeout: float = 60
    api_key: str | None = field(default=None, repr=False)
    base_url: str = ELEVENLABS_ENDPOINT
    _retry: Retry = field(default_factory=standalone_retry, repr=False)
    _api_key: str = field(init=False, repr=False)
    _session: niquests.AsyncSession | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self._api_key = self.api_key or env_api_key_for_base_url(
            self.provider, "ELEVENLABS_API_KEY", self.base_url, ELEVENLABS_ENDPOINT
        )

    def _set_auth_headers(self, session: niquests.AsyncSession) -> None:
        session.headers["xi-api-key"] = self._api_key

    def _quota_exceeded(self, body: dict[str, Any] | None) -> bool:
        detail = body.get("detail") if body else None
        return isinstance(detail, dict) and detail.get("status") == "quota_exceeded"

    def _voice(self, voice_id: str | None) -> str:
        voice = voice_id or self.voice_id
        if not voice:
            raise ValueError(
                "voice_id is required (pass it or set ElevenLabsClient.voice_id)"
            )
        return voice

    async def _post_audio(
        self, path: str, output_format: str | None, **request: Any
    ) -> ElevenLabsAudio:
        params = {"output_format": output_format} if output_format else None
        resp = self._check_resp_status(
            await self.session.post(path, params=params, **request)
        )
        return ElevenLabsAudio(
            audio=resp.content or b"",
            mime_type=resp.headers.get("content-type", "audio/mpeg"),
            request_id=resp.headers.get("request-id"),
        )

    async def generate_speech(
        self,
        text: str,
        voice_id: str | None = None,
        *,
        model: ElevenLabsTTSModel | str = "eleven_multilingual_v2",
        output_format: ElevenLabsOutputFormat | None = None,
        **options: Unpack[SpeechOptions],
    ) -> ElevenLabsAudio:
        """Synthesize `text` with `voice_id` (else the client's default); the API defaults to 128 kbps MP3."""
        voice = self._voice(voice_id)
        body = _speech_body(text, model, options)
        return await self._post_audio(
            f"text-to-speech/{voice}", output_format, json=body
        )

    async def stream_speech(
        self,
        text: str,
        voice_id: str | None = None,
        *,
        model: ElevenLabsTTSModel | str = "eleven_multilingual_v2",
        output_format: ElevenLabsOutputFormat | None = None,
        chunk_size: int = 4096,
        **options: Unpack[SpeechOptions],
    ) -> AsyncGenerator[bytes]:
        """Like `generate_speech`, but yield audio chunks as the API produces them."""
        voice = self._voice(voice_id)
        body = _speech_body(text, model, options)
        stream = self._stream_audio(
            f"text-to-speech/{voice}/stream", output_format, chunk_size, json=body
        )
        async with aclosing(stream) as chunks:
            async for chunk in chunks:
                yield chunk

    async def _stream_audio(
        self,
        path: str,
        output_format: str | None,
        chunk_size: int,
        **request: Any,
    ) -> AsyncGenerator[bytes]:
        params = {"output_format": output_format} if output_format else None
        resp = await self.session.post(path, params=params, stream=True, **request)
        try:
            resp = await self._check_stream_status(resp)
            async for chunk in await resp.iter_content(chunk_size):
                yield bytes(chunk)
        finally:
            await resp.close()

    async def speech_to_speech(
        self,
        audio: str | Path | bytes,
        voice_id: str | None = None,
        *,
        model: ElevenLabsSTSModel | str = "eleven_multilingual_sts_v2",
        output_format: ElevenLabsOutputFormat | None = None,
        **options: Unpack[SpeechToSpeechOptions],
    ) -> ElevenLabsAudio:
        """Re-voice recorded speech (path or bytes) with `voice_id`, keeping its delivery and timing."""
        voice = self._voice(voice_id)
        files = await _sts_parts(audio, model, options)
        return await self._post_audio(
            f"speech-to-speech/{voice}", output_format, files=files
        )

    async def stream_speech_to_speech(
        self,
        audio: str | Path | bytes,
        voice_id: str | None = None,
        *,
        model: ElevenLabsSTSModel | str = "eleven_multilingual_sts_v2",
        output_format: ElevenLabsOutputFormat | None = None,
        chunk_size: int = 4096,
        **options: Unpack[SpeechToSpeechOptions],
    ) -> AsyncGenerator[bytes]:
        """Like `speech_to_speech`, but yield audio chunks as the API produces them."""
        voice = self._voice(voice_id)
        files = await _sts_parts(audio, model, options)
        stream = self._stream_audio(
            f"speech-to-speech/{voice}/stream", output_format, chunk_size, files=files
        )
        async with aclosing(stream) as chunks:
            async for chunk in chunks:
                yield chunk

    async def generate_sound_effect(
        self,
        text: str,
        *,
        model: str = "eleven_text_to_sound_v2",
        duration_seconds: float | None = None,
        prompt_influence: float | None = None,
        loop: bool | None = None,
        output_format: ElevenLabsOutputFormat | None = None,
    ) -> ElevenLabsAudio:
        """Generate a sound effect from a text prompt; the API picks the duration unless set (0.5 to 30 s)."""
        body: _SoundBody = {"text": text, "model_id": model}
        if duration_seconds is not None:
            body["duration_seconds"] = duration_seconds
        if prompt_influence is not None:
            body["prompt_influence"] = prompt_influence
        if loop is not None:
            body["loop"] = loop
        return await self._post_audio("sound-generation", output_format, json=body)

    async def compose_music(
        self,
        prompt: str | None = None,
        *,
        composition_plan: Mapping[str, Any] | None = None,
        music_length_ms: int | None = None,
        model: str = "music_v1",
        force_instrumental: bool | None = None,
        seed: int | None = None,
        output_format: ElevenLabsOutputFormat | None = None,
    ) -> ElevenLabsAudio:
        """Compose music from a `prompt` or a `composition_plan` (exactly one).

        See https://elevenlabs.io/docs/api-reference/music/compose for the plan schema.
        """
        if (prompt is None) == (composition_plan is None):
            raise ValueError("Provide exactly one of prompt or composition_plan")
        body: _MusicBody = {"model_id": model}
        if prompt is not None:
            body["prompt"] = prompt
        if composition_plan is not None:
            body["composition_plan"] = composition_plan
        if music_length_ms is not None:
            body["music_length_ms"] = music_length_ms
        if force_instrumental is not None:
            body["force_instrumental"] = force_instrumental
        if seed is not None:
            body["seed"] = seed
        return await self._post_audio("music", output_format, json=body)

    async def list_voices(self, *, show_legacy: bool = False) -> list[ElevenLabsVoice]:
        """Voices available to the account: premade, cloned and added from the library."""
        params = {"show_legacy": "true"} if show_legacy else None
        resp = self._check_resp_status(await self.session.get("voices", params=params))
        voices: list[ElevenLabsVoice] = resp.json()["voices"]
        return voices

    async def get_voice(self, voice_id: str) -> ElevenLabsVoice:
        resp = self._check_resp_status(await self.session.get(f"voices/{voice_id}"))
        voice: ElevenLabsVoice = resp.json()
        return voice

    async def clone_voice(
        self,
        name: str,
        files: Sequence[str | Path | bytes],
        *,
        description: str | None = None,
        labels: Mapping[str, str] | None = None,
        remove_background_noise: bool = False,
    ) -> str:
        """Create an instant voice clone from audio samples and return its voice ID."""
        if not files:
            raise ValueError("clone_voice needs at least one audio sample")
        parts: list[_Part] = [("name", (None, name))]
        if description is not None:
            parts.append(("description", (None, description)))
        if labels:
            parts.append(("labels", (None, _json_dumps(dict(labels)))))
        if remove_background_noise:
            parts.append(("remove_background_noise", (None, "true")))
        for file in files:
            parts.append(("files", await _read_audio(file)))
        resp = await self.session.post(
            "voices/add", files=cast("MultiPartFilesType", parts)
        )
        voice_id: str = self._check_resp_status(resp).json()["voice_id"]
        return voice_id

    async def delete_voice(self, voice_id: str) -> None:
        self._check_resp_status(await self.session.delete(f"voices/{voice_id}"))

    async def transcribe(
        self,
        *,
        file: str | Path | bytes | None = None,
        filename: str | None = None,
        content_type: str | None = None,
        source_url: str | None = None,
        model: ElevenLabsSTTModel | str = "scribe_v2",
        language: str | None = None,
        diarize: bool = False,
        num_speakers: int | None = None,
        tag_audio_events: bool | None = None,
        timestamps_granularity: Literal["none", "word", "character"] | None = None,
        keyterms: Sequence[str] | None = None,
        temperature: float | None = None,
        seed: int | None = None,
    ) -> ElevenLabsTranscription:
        """Transcribe a local `file` (path or raw bytes) or a remote `source_url`; exactly one is required.

        ``filename`` and ``content_type`` override what the path (or raw bytes) imply.
        """
        if (file is None) == (source_url is None):
            raise ValueError("Provide exactly one of file or source_url")
        fields: list[tuple[str, str]] = [("model_id", model)]
        if source_url is not None:
            fields.append(("source_url", source_url))
        if language is not None:
            fields.append(("language_code", language))
        if diarize:
            fields.append(("diarize", "true"))
        if num_speakers is not None:
            fields.append(("num_speakers", str(num_speakers)))
        if tag_audio_events is not None:
            fields.append(("tag_audio_events", str(tag_audio_events).lower()))
        if timestamps_granularity is not None:
            fields.append(("timestamps_granularity", timestamps_granularity))
        if temperature is not None:
            fields.append(("temperature", str(temperature)))
        if seed is not None:
            fields.append(("seed", str(seed)))
        fields.extend(("keyterms", term) for term in keyterms or ())

        # every field goes in `files` so source_url-only requests stay multipart
        parts: list[_Part] = [(name, (None, value)) for name, value in fields]
        if file is not None:
            parts.append(
                (
                    "file",
                    await _read_audio(
                        file, filename=filename, content_type=content_type
                    ),
                )
            )
        resp = await self.session.post(
            "speech-to-text", files=cast("MultiPartFilesType", parts)
        )
        result: ElevenLabsTranscription = self._check_resp_status(resp).json()
        return result
