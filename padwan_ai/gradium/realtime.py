import asyncio
import base64
import re
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Iterable,
    Mapping,
)
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from typing import Any, ClassVar, Literal, NotRequired, TypedDict

import niquests

from .._base import RealtimeClientBase, env_api_key
from .._ws import WsConnection
from ..errors import LLMError, Provider
from .client import (
    GradiumLanguage,
    GradiumOutputFormat,
    GradiumSTTConfig,
    GradiumTTSConfig,
)

__all__ = (
    "GRADIUM_WS_ENDPOINT",
    "GradiumRealtimeInputFormat",
    "GradiumRealtimeS2SClient",
    "GradiumRealtimeSTTClient",
    "GradiumRealtimeTTSClient",
    "GradiumS2SConnection",
    "GradiumSTTConnection",
    "GradiumTTSConnection",
)

GRADIUM_WS_ENDPOINT = "wss://api.gradium.ai/api/"

GradiumRealtimeInputFormat = Literal[
    "pcm",
    "pcm_8000",
    "pcm_16000",
    "pcm_22050",
    "pcm_24000",
    "pcm_44100",
    "pcm_48000",
    "wav",
    "opus",
    "ulaw_8000",
    "mulaw_8000",
    "alaw_8000",
]


class _STTJsonConfig(GradiumSTTConfig, total=False):
    language: GradiumLanguage


class _S2SJsonConfig(TypedDict):
    target_language: str


class _TTSSetup(TypedDict):
    type: Literal["setup"]
    model_name: str
    voice_id: str
    output_format: GradiumOutputFormat
    json_config: NotRequired[GradiumTTSConfig]
    pronunciation_id: NotRequired[str]


class _STTSetup(TypedDict):
    type: Literal["setup"]
    model_name: str
    input_format: GradiumRealtimeInputFormat
    json_config: _STTJsonConfig


class _S2SSetup(TypedDict):
    type: Literal["setup"]
    model_name: str
    input_format: GradiumRealtimeInputFormat
    output_format: GradiumOutputFormat
    stt_model_name: str
    tts_model_name: str
    json_config: _S2SJsonConfig
    voice_id: NotRequired[str]


class _TextMessage(TypedDict):
    type: Literal["text"]
    text: str


class _AudioMessage(TypedDict):
    type: Literal["audio"]
    audio: str


class _FlushMessage(TypedDict):
    type: Literal["flush"]
    flush_id: int


_TRAILING_SPACE = re.compile(r"\s(?=\S*$)")


async def _word_chunks(
    texts: AsyncIterable[str] | Iterable[str],
) -> AsyncIterator[str]:
    """Regroup tokens on whitespace: the server joins consecutive text messages with a space."""
    if not isinstance(texts, AsyncIterable):
        texts = _aiter(texts)
    buffer = ""
    async for text in texts:
        buffer += text
        if match := _TRAILING_SPACE.search(buffer):
            if head := buffer[: match.start()].strip():
                yield head
            buffer = buffer[match.end() :]
    if tail := buffer.strip():
        yield tail


async def _aiter[T](items: Iterable[T]) -> AsyncIterator[T]:
    for item in items:
        yield item


class _GradiumWsAuth:
    """Plain mixin, so `_api_key` stays the base dataclass's init=False field."""

    provider: ClassVar[Provider] = "gradium"
    _api_key: str

    def _get_default_api_key(self) -> str:
        return env_api_key(self.provider, "GRADIUM_API_KEY")

    def _set_auth_headers(self, session: niquests.AsyncSession) -> None:
        session.headers["x-api-key"] = self._api_key


@dataclass
class _GradiumConnection(WsConnection):
    """Gradium stream: error frames raise `LLMError`; `ready` holds the server's ready message."""

    ready: dict[str, Any] = field(default_factory=dict)

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        async for message in super().__aiter__():
            if message.get("type") == "error":
                detail = message.get("message") or "unknown error"
                code = message.get("code")
                raise LLMError(
                    "gradium",
                    f"{code} {detail}" if code else detail,
                    body=dict(message),
                )
            yield message

    async def end_input(self) -> None:
        """Signal the end of the input; the server flushes its output, sends `end_of_stream` and closes."""
        await self.send_event({"type": "end_of_stream"})

    @staticmethod
    def is_final(message: Mapping[str, Any]) -> bool:
        return message.get("type") == "end_of_stream"

    @staticmethod
    def audio_bytes(message: Mapping[str, Any]) -> bytes | None:
        if message.get("type") != "audio":
            return None
        return base64.b64decode(message["audio"])

    @staticmethod
    def transcript(message: Mapping[str, Any]) -> str | None:
        """Text of a `text` message (spoken text for TTS, transcription for STT and S2S)."""
        return message.get("text") if message.get("type") == "text" else None

    async def _pump[T](
        self,
        inputs: AsyncIterable[T] | Iterable[T],
        send: Callable[[T], Awaitable[None]],
    ) -> AsyncIterator[dict[str, Any]]:
        """Send `inputs` in a background task while yielding messages until `end_of_stream`."""

        async def send_all() -> None:
            try:
                items = inputs if isinstance(inputs, AsyncIterable) else _aiter(inputs)
                async for item in items:
                    await send(item)
                await self.end_input()
            except BaseException:
                await self.close()
                raise

        sender = asyncio.create_task(send_all())
        try:
            async for message in self:
                if self.is_final(message):
                    break
                yield message
            await sender
        finally:
            sender.cancel()


@dataclass
class GradiumTTSConnection(_GradiumConnection):
    """An open TTS stream; iterating it yields `audio`, `text` and `end_of_stream` messages."""

    async def send_text(self, text: str) -> None:
        """Queue `text`; split on whitespace only, as the server adds a space between messages."""
        payload: _TextMessage = {"type": "text", "text": text}
        await self.send_event(payload)

    async def stream(
        self, texts: AsyncIterable[str] | Iterable[str]
    ) -> AsyncIterator[bytes]:
        """Send `texts` (regrouped on word boundaries) while yielding audio chunks."""
        async for message in self._pump(_word_chunks(texts), self.send_text):
            if audio := self.audio_bytes(message):
                yield audio


@dataclass
class _AudioInputConnection(_GradiumConnection):
    async def send_audio(self, audio: bytes) -> None:
        """Stream an audio chunk in the client's `input_format` (80 ms chunks are recommended)."""
        payload: _AudioMessage = {
            "type": "audio",
            "audio": base64.b64encode(audio).decode("ascii"),
        }
        await self.send_event(payload)

    async def stream(
        self, chunks: AsyncIterable[bytes] | Iterable[bytes]
    ) -> AsyncIterator[dict[str, Any]]:
        """Send audio `chunks` while yielding server messages until `end_of_stream`."""
        async for message in self._pump(chunks, self.send_audio):
            yield message


@dataclass
class GradiumSTTConnection(_AudioInputConnection):
    """An open STT stream; iterating it yields `text`, `end_text`, `step` (VAD) and `flushed` messages."""

    async def flush(self, flush_id: int = 0) -> None:
        """Ask for outstanding transcripts now; the server answers with `flushed`."""
        payload: _FlushMessage = {"type": "flush", "flush_id": flush_id}
        await self.send_event(payload)


@dataclass
class GradiumS2SConnection(_AudioInputConnection):
    """An open speech-to-speech stream; iterating it yields `audio` and `text` messages."""


async def _handshake[C: _GradiumConnection](
    client: RealtimeClientBase[Any],
    route: str,
    setup: Mapping[str, Any],
    conn_type: type[C],
) -> C:
    """Upgrade to a WebSocket, send `setup` and wait for `ready`."""
    resp = await client.session.get(f"{client.base_url}{route}", timeout=client.timeout)
    if resp.extension is None:
        raise LLMError(
            "gradium",
            f"handshake did not upgrade to a websocket (status {resp.status_code})",
        )
    conn = conn_type(resp.extension)
    try:
        await conn.send_event(setup)
        async for message in conn:
            if message.get("type") == "ready":
                conn.ready = message
                return conn
        raise LLMError("gradium", "stream closed before ready")
    except BaseException:
        await conn.close()
        raise


@dataclass
class GradiumRealtimeTTSClient(
    _GradiumWsAuth, RealtimeClientBase[GradiumTTSConnection]
):
    """Text-to-speech over a WebSocket: send text as it arrives (e.g. from an LLM stream), receive audio.

    https://docs.gradium.ai/api-reference/endpoint/tts-websocket
    """

    model: str = "default"
    voice_id: str = field(kw_only=True)
    base_url: str = field(default=GRADIUM_WS_ENDPOINT, kw_only=True)
    output_format: GradiumOutputFormat = "pcm"
    """`pcm` is 48 kHz s16le mono."""
    config: GradiumTTSConfig | None = None
    pronunciation_id: str | None = None

    def setup_payload(self) -> _TTSSetup:
        setup: _TTSSetup = {
            "type": "setup",
            "model_name": self.model,
            "voice_id": self.voice_id,
            "output_format": self.output_format,
        }
        if self.config:
            setup["json_config"] = self.config
        if self.pronunciation_id:
            setup["pronunciation_id"] = self.pronunciation_id
        return setup

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[GradiumTTSConnection]:
        conn = await _handshake(
            self, "speech/tts", self.setup_payload(), GradiumTTSConnection
        )
        try:
            yield conn
        finally:
            await conn.close()


@dataclass
class GradiumRealtimeSTTClient(
    _GradiumWsAuth, RealtimeClientBase[GradiumSTTConnection]
):
    """Realtime speech-to-text over a WebSocket, with voice activity (`step`) messages every 80 ms.

    https://docs.gradium.ai/api-reference/endpoint/stt-websocket
    """

    model: str = "default"
    base_url: str = field(default=GRADIUM_WS_ENDPOINT, kw_only=True)
    input_format: GradiumRealtimeInputFormat = "pcm"
    """`pcm` is 24 kHz s16le mono."""
    language: GradiumLanguage = "any"
    config: GradiumSTTConfig | None = None

    def setup_payload(self) -> _STTSetup:
        json_config: _STTJsonConfig = {**(self.config or {}), "language": self.language}
        return {
            "type": "setup",
            "model_name": self.model,
            "input_format": self.input_format,
            "json_config": json_config,
        }

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[GradiumSTTConnection]:
        conn = await _handshake(
            self, "speech/asr", self.setup_payload(), GradiumSTTConnection
        )
        try:
            yield conn
        finally:
            await conn.close()


@dataclass
class GradiumRealtimeS2SClient(
    _GradiumWsAuth, RealtimeClientBase[GradiumS2SConnection]
):
    """Speech-to-speech translation over a WebSocket: streamed audio comes back re-voiced in `target_language`.

    https://docs.gradium.ai/api-reference/endpoint/s2s-websocket
    """

    model: str = "s2s-translate"
    target_language: str = field(kw_only=True)
    voice_id: str | None = None
    base_url: str = field(default=GRADIUM_WS_ENDPOINT, kw_only=True)
    input_format: GradiumRealtimeInputFormat = "pcm"
    output_format: GradiumOutputFormat = "pcm"
    stt_model: str = "stt-translate"
    tts_model: str = "default"

    def setup_payload(self) -> _S2SSetup:
        setup: _S2SSetup = {
            "type": "setup",
            "model_name": self.model,
            "stt_model_name": self.stt_model,
            "tts_model_name": self.tts_model,
            "input_format": self.input_format,
            "output_format": self.output_format,
            "json_config": {"target_language": self.target_language},
        }
        if self.voice_id:
            setup["voice_id"] = self.voice_id
        return setup

    @asynccontextmanager
    async def _connect(self) -> AsyncIterator[GradiumS2SConnection]:
        conn = await _handshake(
            self, "speech/s2s", self.setup_payload(), GradiumS2SConnection
        )
        try:
            yield conn
        finally:
            await conn.close()
