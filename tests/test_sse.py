import asyncio
from contextlib import nullcontext
from unittest.mock import MagicMock

import pytest
from niquests.packages.urllib3.contrib.webextensions._async import load_extension
from niquests.utils import merge_base_url

from padwan_ai._base import _SseExtension, to_sse_url


@pytest.mark.parametrize(
    "url",
    [
        pytest.param("https://api.example.com/v1/chat", id="https"),
        pytest.param("http://localhost:8080/v1/chat", id="http"),
    ],
)
def test_sse_url_survives_base_url_merge(url):
    sse_url = to_sse_url(url)
    assert merge_base_url("https://api.example.com/v1", sse_url) == sse_url


def test_sse_scheme_resolves_to_padwan_extension():
    assert load_extension("sse", "ai") is _SseExtension


@pytest.mark.parametrize(
    "cancel, leaked, expectation",
    [
        pytest.param(
            True, False, pytest.raises(asyncio.CancelledError), id="cancelled"
        ),
        pytest.param(False, False, nullcontext(), id="eof"),
        # urllib3-future's Timeout cancels the task without uncancel()
        pytest.param(False, True, nullcontext(), id="eof-after-leaked-cancel"),
    ],
)
async def test_sse_extension_propagates_cancellation(cancel, leaked, expectation):
    reading = asyncio.Event()

    async def stream():
        reading.set()
        if cancel:
            await asyncio.Future()
        return
        yield b""

    async def read():
        if leaked:
            asyncio.current_task().cancel()  # pyright: ignore[reportOptionalMemberAccess]
            try:
                await asyncio.sleep(0)
            except asyncio.CancelledError:
                pass
        return await ext.next_payload()

    ext = _SseExtension()
    ext._response = MagicMock()
    ext._stream = stream()
    task = asyncio.create_task(read())
    await reading.wait()
    if cancel:
        task.cancel()
    with expectation:
        assert await task is None
