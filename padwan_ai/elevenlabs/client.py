import dataclasses
from collections.abc import Sequence
from dataclasses import field
from pathlib import Path
from typing import (
    Any,
    ClassVar,
    Literal,
    NotRequired,
    TypedDict,
    cast,
    get_args,
)

import niquests
from niquests.typing import MultiPartFilesType
from urllib3.util.retry import Retry

from .._base import StandaloneClientMixin, env_api_key, standalone_retry
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
ElevenLabsModel = ElevenLabsTTSModel | ElevenLabsSTTModel

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

ELEVENLABS_MODELS: set[str] = set(get_args(ElevenLabsTTSModel)) | set(
    get_args(ElevenLabsSTTModel)
)
ELEVENLABS_ENDPOINT = "https://api.elevenlabs.io/v1/"

__all__ = (
    "ELEVENLABS_ENDPOINT",
    "ELEVENLABS_MODELS",
    "ElevenLabsClient",
    "ElevenLabsModel",
    "ElevenLabsOutputFormat",
    "ElevenLabsSTTModel",
    "ElevenLabsSpeech",
    "ElevenLabsTTSModel",
    "ElevenLabsTranscription",
    "ElevenLabsWord",
    "VoiceSettings",
)


class VoiceSettings(TypedDict, total=False):
    """Per-request override of the voice's stored settings."""

    stability: float
    similarity_boost: float
    style: float
    speed: float
    use_speaker_boost: bool


class _SpeechBody(TypedDict, total=False):
    text: str
    model_id: str
    language_code: str
    voice_settings: VoiceSettings
    seed: int
    previous_text: str
    next_text: str
    previous_request_ids: list[str]


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
class ElevenLabsSpeech:
    """Synthesized audio; pass `request_id` as `previous_request_ids` to stitch the next chunk."""

    audio: bytes
    mime_type: str
    request_id: str | None = None


@dataclasses.dataclass
class ElevenLabsClient(StandaloneClientMixin):
    """Async client for ElevenLabs text-to-speech and speech-to-text.

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
        self._api_key = self.api_key or env_api_key(self.provider, "ELEVENLABS_API_KEY")

    def _set_auth_headers(self, session: niquests.AsyncSession) -> None:
        session.headers["xi-api-key"] = self._api_key

    def _quota_exceeded(self, body: dict[str, Any] | None) -> bool:
        detail = body.get("detail") if body else None
        return isinstance(detail, dict) and detail.get("status") == "quota_exceeded"

    async def generate_speech(
        self,
        text: str,
        voice_id: str | None = None,
        *,
        model: ElevenLabsTTSModel | str = "eleven_multilingual_v2",
        output_format: ElevenLabsOutputFormat | None = None,
        language_code: str | None = None,
        voice_settings: VoiceSettings | None = None,
        seed: int | None = None,
        previous_text: str | None = None,
        next_text: str | None = None,
        previous_request_ids: Sequence[str] | None = None,
    ) -> ElevenLabsSpeech:
        """Synthesize `text` with `voice_id` (else the client's default); the API defaults to 128 kbps MP3."""
        voice = voice_id or self.voice_id
        if not voice:
            raise ValueError(
                "voice_id is required (pass it or set ElevenLabsClient.voice_id)"
            )
        body: _SpeechBody = {"text": text, "model_id": model}
        if language_code is not None:
            body["language_code"] = language_code
        if voice_settings is not None:
            body["voice_settings"] = voice_settings
        if seed is not None:
            body["seed"] = seed
        if previous_text is not None:
            body["previous_text"] = previous_text
        if next_text is not None:
            body["next_text"] = next_text
        if previous_request_ids is not None:
            body["previous_request_ids"] = list(previous_request_ids)
        params = {"output_format": output_format} if output_format else None
        resp = await self.session.post(
            f"text-to-speech/{voice}", json=body, params=params
        )
        checked = self._check_resp_status(resp)
        return ElevenLabsSpeech(
            audio=checked.content or b"",
            mime_type=checked.headers.get("content-type", "audio/mpeg"),
            request_id=checked.headers.get("request-id"),
        )

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
        parts: list[
            tuple[str, tuple[str | None, str | bytes] | tuple[str, bytes, str]]
        ] = [(name, (None, value)) for name, value in fields]
        if file is not None:
            parts.append(
                (
                    "file",
                    await _read_audio(
                        file, filename=filename, content_type=content_type
                    ),
                )
            )
        # niquests types omit the None filename it encodes as a plain form field
        resp = await self.session.post(
            "speech-to-text", files=cast("MultiPartFilesType", parts)
        )
        result: ElevenLabsTranscription = self._check_resp_status(resp).json()
        return result
