import dataclasses
import json
from collections.abc import AsyncGenerator
from dataclasses import field
from functools import partial
from pathlib import Path
from typing import Any, ClassVar, Literal, NotRequired, TypedDict, cast

import niquests
from niquests.typing import MultiPartFilesType
from urllib3.util.retry import Retry

from .._base import StandaloneClientMixin, env_api_key_for_base_url, standalone_retry
from ..content import _read_audio
from ..errors import LLMError, Provider

GradiumOutputFormat = Literal[
    "wav",
    "pcm",
    "opus",
    "ulaw_8000",
    "mulaw_8000",
    "alaw_8000",
    "pcm_8000",
    "pcm_16000",
    "pcm_22050",
    "pcm_24000",
    "pcm_44100",
    "pcm_48000",
]
GradiumInputFormat = Literal["wav", "pcm", "opus"]
GradiumLanguage = Literal["en", "fr", "de", "es", "pt", "any"]
GradiumVoiceLanguage = Literal["en", "fr", "de", "es", "pt"]

GRADIUM_ENDPOINT = "https://api.gradium.ai/api/"

__all__ = (
    "GRADIUM_ENDPOINT",
    "GradiumClient",
    "GradiumInputFormat",
    "GradiumKeywords",
    "GradiumLanguage",
    "GradiumOutputFormat",
    "GradiumSegment",
    "GradiumSpeech",
    "GradiumSTTConfig",
    "GradiumTranscription",
    "GradiumTTSConfig",
    "GradiumVoice",
    "GradiumVoiceLanguage",
    "GradiumVoiceTag",
)

# Content-Type selects the STT input format; .wav guesses to audio/x-wav, which the API rejects
_INPUT_CONTENT_TYPES: dict[GradiumInputFormat, str] = {
    "wav": "audio/wav",
    "pcm": "audio/pcm",
    "opus": "audio/ogg",
}
_SUFFIX_FORMATS: dict[str, GradiumInputFormat] = {
    ".wav": "wav",
    ".pcm": "pcm",
    ".raw": "pcm",
    ".ogg": "opus",
    ".opus": "opus",
}


class GradiumTTSConfig(TypedDict, total=False):
    """Synthesis tuning sent as `json_config`; see https://docs.gradium.ai/guides/voice-settings."""

    temp: float
    padding_bonus: float
    rewrite_rules: str


class GradiumKeywords(TypedDict):
    words: list[str]
    boost: float


class GradiumSTTConfig(TypedDict, total=False):
    """Transcription tuning sent as `json_config`; see https://docs.gradium.ai/guides/transcription-settings."""

    temp: float
    padding_bonus: float
    delay_in_frames: int
    keywords: GradiumKeywords


class _SpeechBody(TypedDict):
    text: str
    voice_id: str
    output_format: GradiumOutputFormat
    only_audio: bool
    model_name: str
    json_config: NotRequired[str]
    """`GradiumTTSConfig` serialized: the API takes this field as a JSON string."""


class _VoiceUpdate(TypedDict, total=False):
    name: str
    description: str
    language: GradiumVoiceLanguage
    start_s: float


class GradiumVoiceTag(TypedDict):
    value: str
    category: NotRequired[str | None]


class GradiumVoice(TypedDict):
    """A voice from `voices/`; catalog voices have `is_catalog` set."""

    uid: str
    name: str
    description: NotRequired[str | None]
    language: NotRequired[str | None]
    filename: NotRequired[str | None]
    start_s: NotRequired[float | None]
    is_catalog: NotRequired[bool]
    is_pro_clone: NotRequired[bool]
    tags: NotRequired[list[GradiumVoiceTag]]


type _Part = tuple[str, tuple[str | None, str | bytes] | tuple[str, bytes, str]]


class GradiumSegment(TypedDict):
    text: str
    start: float
    end: float | None


class GradiumTranscription(TypedDict):
    text: str
    segments: list[GradiumSegment]


@dataclasses.dataclass(frozen=True, slots=True)
class GradiumSpeech:
    """Synthesized audio in the requested output format."""

    audio: bytes
    mime_type: str


def _parse_transcription(body: str) -> GradiumTranscription:
    """Fold the NDJSON stream into segments; `end_text` closes the latest `text`."""
    segments: list[GradiumSegment] = []
    for line in body.splitlines():
        if not line.strip():
            continue
        try:
            msg = json.loads(line)
            match msg.get("type"):
                case "text":
                    segments.append(
                        {"text": msg["text"], "start": msg["start_s"], "end": None}
                    )
                case "end_text" if segments:
                    segments[-1]["end"] = msg["stop_s"]
                case "error":
                    raise LLMError(
                        "gradium", msg.get("message", "transcription failed")
                    )
        except (ValueError, KeyError, AttributeError) as error:
            raise LLMError(
                "gradium", f"Malformed transcription line: {line!r}", cause=error
            ) from error
    return {"text": " ".join(s["text"] for s in segments), "segments": segments}


@dataclasses.dataclass
class GradiumClient(StandaloneClientMixin):
    """Async client for Gradium text-to-speech and speech-to-text (REST).

    Experimental: the interface and typed payloads may change between minor releases.

    https://docs.gradium.ai/api-reference/introduction
    """

    provider: ClassVar[Provider] = "gradium"
    voice_id: str | None = None
    """Default voice for `generate_speech`; see https://docs.gradium.ai/guides/voices/flagship-voices."""
    timeout: float = 60
    api_key: str | None = field(default=None, repr=False)
    base_url: str = GRADIUM_ENDPOINT
    # no 500: the docs say pre-stream auth and input errors use it too
    # Failures are plain-text 500s (not retried); POSTs bill or create voices, so only
    # connection errors are retried for them.
    _retry: Retry = field(
        default_factory=partial(
            standalone_retry, (502, 503, 504), ("GET", "PUT", "DELETE")
        ),
        repr=False,
    )
    _api_key: str = field(init=False, repr=False)
    _session: niquests.AsyncSession | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self._api_key = self.api_key or env_api_key_for_base_url(
            self.provider, "GRADIUM_API_KEY", self.base_url, GRADIUM_ENDPOINT
        )

    def _set_auth_headers(self, session: niquests.AsyncSession) -> None:
        session.headers["x-api-key"] = self._api_key

    def _speech_body(
        self,
        text: str,
        voice_id: str | None,
        model: str,
        output_format: GradiumOutputFormat,
        config: GradiumTTSConfig | None,
    ) -> _SpeechBody:
        voice = voice_id or self.voice_id
        if not voice:
            raise ValueError(
                "voice_id is required (pass it or set GradiumClient.voice_id)"
            )
        body: _SpeechBody = {
            "text": text,
            "voice_id": voice,
            "output_format": output_format,
            "only_audio": True,
            "model_name": model,
        }
        if config:
            body["json_config"] = json.dumps(config)
        return body

    async def generate_speech(
        self,
        text: str,
        voice_id: str | None = None,
        *,
        model: str = "default",
        output_format: GradiumOutputFormat = "wav",
        config: GradiumTTSConfig | None = None,
    ) -> GradiumSpeech:
        """Synthesize `text` with `voice_id` (else the client's default); `model="default"` is the latest.

        The audio is requested whole (`only_audio`), so a failure after the response
        started comes back as truncated audio, not an error.
        """
        body = self._speech_body(text, voice_id, model, output_format, config)
        resp = self._check_resp_status(
            await self.session.post("post/speech/tts", json=body)
        )
        return GradiumSpeech(
            audio=resp.content or b"",
            mime_type=resp.headers.get("content-type", "application/octet-stream"),
        )

    async def stream_speech(
        self,
        text: str,
        voice_id: str | None = None,
        *,
        model: str = "default",
        output_format: GradiumOutputFormat = "wav",
        config: GradiumTTSConfig | None = None,
        chunk_size: int = 4096,
    ) -> AsyncGenerator[bytes]:
        """Like `generate_speech`, but yield audio chunks as the API produces them."""
        body = self._speech_body(text, voice_id, model, output_format, config)
        resp = await self.session.post("post/speech/tts", json=body, stream=True)
        try:
            resp = await self._check_stream_status(resp)
            async for chunk in await resp.iter_content(chunk_size):
                yield bytes(chunk)
        finally:
            await resp.close()

    async def list_voices(self, *, include_catalog: bool = False) -> list[GradiumVoice]:
        """Custom voices of the organization, plus the shared catalog with `include_catalog`."""
        # limit=0 lifts the API's default page size of 100, as the SDK does
        params = {"limit": "0", "include_catalog": str(include_catalog).lower()}
        resp = self._check_resp_status(await self.session.get("voices/", params=params))
        voices: list[GradiumVoice] = resp.json()
        return voices

    async def get_voice(self, voice_id: str) -> GradiumVoice:
        resp = self._check_resp_status(await self.session.get(f"voices/{voice_id}"))
        voice: GradiumVoice = resp.json()
        return voice

    async def clone_voice(
        self,
        name: str,
        file: str | Path | bytes,
        *,
        language: GradiumVoiceLanguage,
        description: str | None = None,
        start_s: float | None = None,
        input_format: str | None = None,
    ) -> str:
        """Create a custom voice from an audio sample and return its ID.

        `start_s` picks where the sample starts; `input_format` (e.g. `wav`, `mp3`) is inferred from a path's suffix.
        """
        filename, audio, _ = await _read_audio(file)
        fmt = input_format or Path(filename).suffix.lstrip(".").lower()
        if not fmt:
            raise ValueError("input_format is required for raw bytes")
        # the SDK sends audio/<format>; mimetypes' audio/x-wav is rejected
        parts: list[_Part] = [
            ("audio_file", (f"{Path(filename).stem}.{fmt}", audio, f"audio/{fmt}")),
            ("name", (None, name)),
            ("language", (None, language)),
            ("input_format", (None, fmt)),
        ]
        if description is not None:
            parts.append(("description", (None, description)))
        if start_s is not None:
            parts.append(("start_s", (None, str(start_s))))
        resp = await self.session.post(
            "voices/", files=cast("MultiPartFilesType", parts)
        )
        created: dict[str, Any] = self._check_resp_status(resp).json()
        if not (uid := created.get("uid")):
            raise LLMError(
                "gradium", created.get("error") or "voice creation failed", body=created
            )
        return uid

    async def update_voice(
        self,
        voice_id: str,
        *,
        name: str | None = None,
        description: str | None = None,
        language: GradiumVoiceLanguage | None = None,
        start_s: float | None = None,
    ) -> GradiumVoice:
        """Update the given fields of a custom voice and return it."""
        body: _VoiceUpdate = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        if language is not None:
            body["language"] = language
        if start_s is not None:
            body["start_s"] = start_s
        if not body:
            raise ValueError("update_voice needs at least one field to change")
        resp = self._check_resp_status(
            await self.session.put(f"voices/{voice_id}", json=body)
        )
        voice: GradiumVoice = resp.json()
        return voice

    async def delete_voice(self, voice_id: str) -> None:
        self._check_resp_status(await self.session.delete(f"voices/{voice_id}"))

    async def transcribe(
        self,
        *,
        file: str | Path | bytes,
        language: GradiumLanguage = "any",
        model: str = "default",
        input_format: GradiumInputFormat | None = None,
        config: GradiumSTTConfig | None = None,
    ) -> GradiumTranscription:
        """Transcribe a wav, raw pcm (24 kHz s16le mono) or Ogg Opus `file` (path or bytes).

        `input_format` is inferred from a path's extension and defaults to wav for bytes.
        """
        name, data, _ = await _read_audio(file)
        fmt = input_format or _SUFFIX_FORMATS.get(Path(name).suffix.lower())
        if fmt is None:
            if not isinstance(file, bytes):
                raise ValueError(
                    f"Unsupported audio format for {name!r}: expected wav, pcm or opus "
                    "(pass input_format= to override)"
                )
            fmt = "wav"
        params = {
            "model": model,
            "json_config": json.dumps({**(config or {}), "language": language}),
        }
        resp = await self.session.post(
            "post/speech/asr",
            data=data,
            params=params,
            headers={"Content-Type": _INPUT_CONTENT_TYPES[fmt]},
        )
        return _parse_transcription(self._check_resp_status(resp).text or "")
