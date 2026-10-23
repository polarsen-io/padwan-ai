import base64
from collections.abc import (
    AsyncGenerator,
    AsyncIterable,
    AsyncIterator,
    Iterable,
    Mapping,
    Sequence,
)
from contextlib import aclosing, asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal, NotRequired, TypedDict

from .._base import ApiKeyWsAuth, RealtimeClientBase
from .._ws import WsConnection, aiter_items
from ..errors import LLMError, Provider, QuotaExceededError, TooManyRequestsError
from .client import ElevenLabsOutputFormat, VoiceSettings

__all__ = (
    "ELEVENLABS_WS_ENDPOINT",
    "ElevenLabsRealtimeAudioFormat",
    "ElevenLabsRealtimeSTTClient",
    "ElevenLabsRealtimeTTSClient",
    "ElevenLabsSTTConnection",
    "ElevenLabsTTSConnection",
)

ELEVENLABS_WS_ENDPOINT = "wss://api.elevenlabs.io/v1/"

ElevenLabsRealtimeAudioFormat = Literal[
    "pcm_8000",
    "pcm_16000",
    "pcm_22050",
    "pcm_24000",
    "pcm_44100",
    "pcm_48000",
    "ulaw_8000",
]

_TRANSCRIPT_TYPES = frozenset(
    {
        "partial_transcript",
        "committed_transcript",
        "committed_transcript_with_timestamps",
    }
)


class _TTSInit(TypedDict):
    text: Literal[" "]
    voice_settings: NotRequired[VoiceSettings]
    generation_config: NotRequired[dict[str, list[int]]]


class _TTSText(TypedDict):
    text: str
    flush: NotRequired[bool]


class _STTChunk(TypedDict):
    message_type: Literal["input_audio_chunk"]
    audio_base_64: str
    commit: bool
    sample_rate: int
    previous_text: NotRequired[str]


_THROTTLE_KINDS = frozenset({"rate_limited", "commit_throttled", "queue_overflow"})


def _raise_on_error(message: Mapping[str, Any]) -> None:
    """Raise padwan errors for error frames (TTS sends `error`, Scribe also sets `message_type`)."""
    error = message.get("error")
    if not error:
        return
    kind = message.get("message_type") or "error"
    detail = message.get("message") or error
    if kind == "quota_exceeded":
        raise QuotaExceededError(body=dict(message))
    if kind in _THROTTLE_KINDS:
        raise TooManyRequestsError(retry_delay=1, message=f"{kind}: {detail}")
    raise LLMError("elevenlabs", f"{kind}: {detail}", body=dict(message))


_SPLITTERS = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")


async def _word_chunks(
    texts: AsyncIterable[str] | Iterable[str],
) -> AsyncIterator[str]:
    """Regroup token streams into chunks ending on a word boundary (as the SDK's `text_chunker`)."""
    if not isinstance(texts, AsyncIterable):
        texts = aiter_items(texts)
    buffer = ""
    async for text in texts:
        if buffer.endswith(_SPLITTERS):
            yield buffer
            buffer = text
        elif text.startswith(_SPLITTERS):
            yield buffer + text[0]
            buffer = text[1:]
        else:
            buffer += text
    if buffer:
        yield buffer


class _ElevenLabsWsAuth(ApiKeyWsAuth):
    provider: ClassVar[Provider] = "elevenlabs"
    api_key_env: ClassVar[str] = "ELEVENLABS_API_KEY"
    api_key_header: ClassVar[str] = "xi-api-key"
    api_key_endpoint: ClassVar[str] = ELEVENLABS_WS_ENDPOINT


@dataclass
class ElevenLabsRealtimeTTSClient(
    _ElevenLabsWsAuth, RealtimeClientBase["ElevenLabsTTSConnection"]
):
    """Text-to-speech over a WebSocket: send text as it arrives (e.g. from an LLM stream), receive audio.

    https://elevenlabs.io/docs/api-reference/text-to-speech/v-1-text-to-speech-voice-id-stream-input
    """

    model: str = "eleven_flash_v2_5"
    voice_id: str = field(kw_only=True)
    base_url: str = field(default=ELEVENLABS_WS_ENDPOINT, kw_only=True)
    output_format: ElevenLabsOutputFormat | None = None
    language_code: str | None = None
    voice_settings: VoiceSettings | None = None
    chunk_length_schedule: Sequence[int] | None = None
    """Characters buffered before each generation; lower means lower latency."""
    auto_mode: bool | None = None
    """Let the server pick generation boundaries, ignoring `chunk_length_schedule`."""

    def connect_params(self) -> dict[str, str]:
        params = {"model_id": self.model}
        if self.output_format:
            params["output_format"] = self.output_format
        if self.language_code:
            params["language_code"] = self.language_code
        if self.auto_mode is not None:
            params["auto_mode"] = str(self.auto_mode).lower()
        return params

    def init_payload(self) -> _TTSInit:
        payload: _TTSInit = {"text": " "}
        if self.voice_settings:
            payload["voice_settings"] = self.voice_settings
        if self.chunk_length_schedule:
            payload["generation_config"] = {
                "chunk_length_schedule": list(self.chunk_length_schedule)
            }
        return payload

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator["ElevenLabsTTSConnection"]:
        url = f"{self.base_url}text-to-speech/{self.voice_id}/stream-input"
        conn = ElevenLabsTTSConnection(await self._open_ws(url, self.connect_params()))
        try:
            await conn.send_event(self.init_payload())
            yield conn
        finally:
            await conn.close()


@dataclass
class ElevenLabsTTSConnection(WsConnection):
    """An open stream-input session; iterating it yields server messages and raises on error frames."""

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        async for message in super().__aiter__():
            _raise_on_error(message)
            yield message

    async def send_text(self, text: str, *, flush: bool = False) -> None:
        """Queue `text`, which should end on a word boundary; `flush` forces generation of what is buffered."""
        # the API expects each chunk to end with a space
        payload: _TTSText = {"text": text if text.endswith(" ") else f"{text} "}
        if flush:
            payload["flush"] = True
        await self.send_event(payload)

    async def end_input(self) -> None:
        """Signal the end of the text; the server sends the remaining audio, then `isFinal`."""
        await self.send_event({"text": ""})

    async def stream(
        self, texts: AsyncIterable[str] | Iterable[str]
    ) -> AsyncGenerator[bytes]:
        """Send `texts` while yielding audio chunks until the final message."""

        async def send_all() -> None:
            async for chunk in _word_chunks(texts):
                if chunk.strip():  # a lone " " is the init message
                    await self.send_text(chunk)
            await self.end_input()

        async with aclosing(
            self.pump("elevenlabs", send_all, self.is_final)
        ) as messages:
            async for message in messages:
                if audio := self.audio_bytes(message):
                    yield audio

    @staticmethod
    def audio_bytes(message: Mapping[str, Any]) -> bytes | None:
        audio = message.get("audio")
        return base64.b64decode(audio) if audio else None

    @staticmethod
    def is_final(message: Mapping[str, Any]) -> bool:
        return bool(message.get("isFinal"))


@dataclass
class ElevenLabsRealtimeSTTClient(
    _ElevenLabsWsAuth, RealtimeClientBase["ElevenLabsSTTConnection"]
):
    """Realtime speech-to-text (Scribe) over a WebSocket.

    Manual commits by default; set `commit_strategy="vad"` to let the server commit on silence.
    https://elevenlabs.io/docs/api-reference/speech-to-text/v-1-speech-to-text-realtime
    """

    model: str = "scribe_v2_realtime"
    base_url: str = field(default=ELEVENLABS_WS_ENDPOINT, kw_only=True)
    audio_format: ElevenLabsRealtimeAudioFormat = "pcm_16000"
    commit_strategy: Literal["manual", "vad"] = "manual"
    language_code: str | None = None
    include_timestamps: bool = False
    keyterms: Sequence[str] | None = None
    vad_silence_threshold_secs: float | None = None
    vad_threshold: float | None = None
    min_speech_duration_ms: int | None = None
    min_silence_duration_ms: int | None = None

    def connect_params(self) -> list[tuple[str, str]]:
        params = [
            ("model_id", self.model),
            ("audio_format", self.audio_format),
            ("commit_strategy", self.commit_strategy),
        ]
        for key in (
            "language_code",
            "vad_silence_threshold_secs",
            "vad_threshold",
            "min_speech_duration_ms",
            "min_silence_duration_ms",
        ):
            if (value := getattr(self, key)) is not None:
                params.append((key, str(value)))
        if self.include_timestamps:
            params.append(("include_timestamps", "true"))
        params.extend(("keyterms", term) for term in self.keyterms or ())
        return params

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator["ElevenLabsSTTConnection"]:
        ext = await self._open_ws(
            f"{self.base_url}speech-to-text/realtime", self.connect_params()
        )
        sample_rate = int(self.audio_format.rsplit("_", 1)[1])
        conn = ElevenLabsSTTConnection(ext, sample_rate=sample_rate)
        try:
            await conn.wait_for(
                lambda m: m.get("message_type") == "session_started",
                timeout=self.timeout,
                provider="elevenlabs",
                what="session_started",
            )
            yield conn
        finally:
            await conn.close()


@dataclass
class ElevenLabsSTTConnection(WsConnection):
    """An open Scribe session; iterating it yields transcript messages and raises on error frames.

    Send audio in the client's `audio_format` with `append_audio`, then `commit` to finalize a segment.
    """

    sample_rate: int = 16_000

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        async for message in super().__aiter__():
            _raise_on_error(message)
            yield message

    async def append_audio(
        self, audio: bytes, *, previous_text: str | None = None
    ) -> None:
        """Stream an audio chunk; `previous_text` gives context and is only accepted on the first chunk."""
        await self._send_chunk(audio, commit=False, previous_text=previous_text)

    async def commit(self) -> None:
        """Finalize the buffered audio into a `committed_transcript` (manual strategy)."""
        await self._send_chunk(b"", commit=True)

    async def _send_chunk(
        self, audio: bytes, *, commit: bool, previous_text: str | None = None
    ) -> None:
        payload: _STTChunk = {
            "message_type": "input_audio_chunk",
            "audio_base_64": base64.b64encode(audio).decode("ascii"),
            "commit": commit,
            "sample_rate": self.sample_rate,
        }
        if previous_text is not None:
            payload["previous_text"] = previous_text
        await self.send_event(payload)

    @staticmethod
    def transcript(message: Mapping[str, Any]) -> str | None:
        """Text of a partial or committed transcript message."""
        if message.get("message_type") in _TRANSCRIPT_TYPES:
            return message.get("text")
        return None

    @staticmethod
    def is_committed(message: Mapping[str, Any]) -> bool:
        """Whether `message` is a committed transcript (with or without timestamps)."""
        return message.get("message_type") in (
            "committed_transcript",
            "committed_transcript_with_timestamps",
        )
