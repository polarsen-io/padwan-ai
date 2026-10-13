import asyncio
from collections.abc import AsyncGenerator, AsyncIterator, Awaitable, Callable, Mapping
from dataclasses import dataclass
from typing import Any

import niquests

from ._json import dumps as _json_dumps, loads as _json_loads
from .errors import LLMError, Provider
from .logs import log

__all__ = ("WsConnection",)


@dataclass
class WsConnection:
    """JSON-over-WebSocket connection: send events, async-iterate parsed messages."""

    ext: Any
    _closed: bool = False

    async def send_event(self, event: Mapping[str, Any]) -> None:
        """Send a raw client event as a JSON text frame."""
        await self.ext.send_payload(_json_dumps(event))

    async def __aiter__(self) -> AsyncIterator[dict[str, Any]]:
        while not self._closed:
            try:
                payload = await self.ext.next_payload()
            except niquests.exceptions.ReadTimeout:
                continue
            if payload is None:
                break
            if isinstance(payload, (bytes, bytearray)):
                payload = bytes(payload).decode("utf-8", errors="replace")
            try:
                yield _json_loads(payload)
            except ValueError:
                log.debug("skipping non-JSON ws frame: %.100r", payload)

    async def pump(
        self,
        provider: Provider,
        send_all: Callable[[], Awaitable[None]],
        is_final: Callable[[Mapping[str, Any]], bool],
    ) -> AsyncGenerator[dict[str, Any]]:
        """Run `send_all` in a background task, yielding messages until the final one (not yielded).

        The sender is always cancelled and awaited on exit; a send error is re-raised, and a server
        close before the final message raises `LLMError`.
        """

        async def run() -> None:
            try:
                await send_all()
            except Exception:
                await self.close()  # unblock the reader
                raise

        sender = asyncio.create_task(run())
        final = False
        try:
            async for message in self:
                if is_final(message):
                    final = True
                    break
                yield message
        finally:
            sender.cancel()
            (outcome,) = await asyncio.gather(sender, return_exceptions=True)
        if isinstance(outcome, Exception):
            raise outcome
        if not final:
            raise LLMError(provider, "connection closed before the end of the stream")

    async def close(self) -> None:
        """Close the underlying websocket (idempotent)."""
        if self._closed:
            return
        self._closed = True
        try:
            await self.ext.close()
        except Exception:  # best effort — the socket may already be gone
            log.debug("error closing realtime websocket", exc_info=True)
