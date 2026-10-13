import dataclasses
import json
from dataclasses import field
from functools import partial
from pathlib import Path
from typing import Any, ClassVar, Literal, NotRequired, TypedDict

import niquests
from urllib3.util.retry import Retry

from .._base import StandaloneClientMixin, env_api_key
from ..content import _read_audio
from ..errors import LLMError, Provider, _error_message

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
    json_config: NotRequired[GradiumTTSConfig]


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


def _check_resp_status(resp: niquests.Response) -> niquests.Response:
    """Raise `LLMError` on non-2xx; bodies are JSON `{"detail": ...}` or plain text."""
    try:
        return resp.raise_for_status()
    except niquests.exceptions.HTTPError as error:
        try:
            data: Any = resp.json()
        except Exception:
            data = None
        body = data if isinstance(data, dict) else None
        message = _error_message(data) or (resp.text or "").strip()
        raise LLMError(
            "gradium", f"{resp.status_code} {message}".rstrip(), cause=error, body=body
        ) from error


def _parse_transcription(body: str) -> GradiumTranscription:
    """Fold the NDJSON stream into segments; `end_text` closes the latest `text`."""
    segments: list[GradiumSegment] = []
    for line in body.splitlines():
        if not line.strip():
            continue
        msg = json.loads(line)
        match msg.get("type"):
            case "text":
                segments.append(
                    {"text": msg["text"], "start": msg["start_s"], "end": None}
                )
            case "end_text" if segments:
                segments[-1]["end"] = msg["stop_s"]
            case "error":
                raise LLMError("gradium", msg.get("message", "transcription failed"))
    return {"text": " ".join(s["text"] for s in segments), "segments": segments}


@dataclasses.dataclass
class GradiumClient(StandaloneClientMixin):
    """Async client for Gradium text-to-speech and speech-to-text (REST).

    https://docs.gradium.ai/api-reference/introduction
    """

    provider: ClassVar[Provider] = "gradium"
    voice_id: str | None = None
    """Default voice for `generate_speech`; see https://docs.gradium.ai/guides/voices/flagship-voices."""
    timeout: float = 60
    api_key: str | None = field(default=None, repr=False)
    base_url: str = GRADIUM_ENDPOINT
    # no 500: the docs say pre-stream auth and input errors use it too
    _retry: Retry = field(
        default_factory=partial(
            Retry,
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 502, 503, 504],
            allowed_methods=["GET", "POST"],
            respect_retry_after_header=True,
            raise_on_status=False,
        ),
        repr=False,
    )
    _api_key: str = field(init=False, repr=False)
    _session: niquests.AsyncSession | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self._api_key = self.api_key or env_api_key(self.provider, "GRADIUM_API_KEY")

    def _set_auth_headers(self, session: niquests.AsyncSession) -> None:
        session.headers["x-api-key"] = self._api_key

    async def generate_speech(
        self,
        text: str,
        voice_id: str | None = None,
        *,
        model: str = "default",
        output_format: GradiumOutputFormat = "wav",
        config: GradiumTTSConfig | None = None,
    ) -> GradiumSpeech:
        """Synthesize `text` with `voice_id` (else the client's default); `model="default"` is the latest."""
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
            body["json_config"] = config
        resp = _check_resp_status(await self.session.post("post/speech/tts", json=body))
        return GradiumSpeech(
            audio=resp.content or b"",
            mime_type=resp.headers.get("content-type", "application/octet-stream"),
        )

    async def transcribe(
        self,
        file: str | Path | bytes,
        *,
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
        return _parse_transcription(_check_resp_status(resp).text or "")
