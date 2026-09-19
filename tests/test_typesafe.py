from contextlib import nullcontext
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import cast
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from urllib3.util.retry import Retry

from padwan_ai import TYPESAFE_MODELS, TypeSafeClient
from padwan_ai.errors import LLMError, TooManyRequestsError
from padwan_ai.typesafe.client import _check_resp

RESPONSE = {
    "model": "jev-1.13.0",
    "answers": {
        "billing": {"type": "noul", "noul": 0.98},
        "tone": {
            "type": "choice",
            "choice": "calm",
            "confidence": 0.8,
            "probabilities": {"calm": 0.9, "angry": 0.1},
        },
        "urgency": {
            "type": "score",
            "score": 1.7,
            "confidence": 0.7,
            "legend": {"0": "low", "1": "medium", "2": "high"},
            "probabilities": {"0": 0.0, "1": 0.3, "2": 0.7},
        },
    },
    "usage": {"input_tokens": 120, "output_tokens": 12},
}

QUESTIONS = {
    "billing": {"type": "noul", "instructions": "Is this about billing?"},
    "tone": {
        "type": "choice",
        "instructions": "What is the tone?",
        "criteria": {"calm": None, "angry": None},
    },
    "urgency": {
        "type": "score",
        "instructions": {"question": "How urgent is this?"},
        "criteria": ["low", "medium", "high"],
    },
}


@pytest.mark.parametrize(
    "model, expected",
    [
        pytest.param(None, "jev-latest", id="default"),
        pytest.param("jev-1.13.0", "jev-1.13.0", id="versioned-override"),
    ],
)
async def test_system_one(model, expected, make_resp):
    client = TypeSafeClient(api_key="secret")
    session = AsyncMock()
    session.post.return_value = make_resp(200, RESPONSE)
    client._session = session

    result = await client.system_one(
        {"ticket": "charged twice", "attempt": 2}, QUESTIONS, model=model
    )

    assert result == RESPONSE
    session.post.assert_awaited_once_with(
        "systemone",
        json={
            "state": {"ticket": "charged twice", "attempt": 2},
            "model": expected,
            "questions": QUESTIONS,
        },
    )


@pytest.mark.parametrize(
    "payload, ctx",
    [
        pytest.param(RESPONSE, nullcontext(), id="valid"),
        pytest.param(
            {}, pytest.raises(LLMError, match="Malformed"), id="missing-fields"
        ),
    ],
)
def test_response_validation(payload, ctx, make_resp):
    with ctx:
        assert _check_resp(make_resp(200, payload)) == RESPONSE


@pytest.mark.parametrize(
    "status, payload, message",
    [
        pytest.param(
            401, {"error": {"message": "bad key"}}, "401 bad key", id="nested-error"
        ),
        pytest.param(422, {"detail": "bad request"}, "422 bad request", id="detail"),
        pytest.param(
            422,
            {"detail": [{"loc": ["body", "questions"], "msg": "Field required"}]},
            "422 Field required",
            id="validation-detail",
        ),
        pytest.param(500, {}, "500", id="empty-error"),
    ],
)
def test_provider_errors(status, payload, message, make_resp):
    with pytest.raises(LLMError, match=message) as caught:
        _check_resp(make_resp(status, payload))
    assert caught.value.provider == "typesafe"
    assert caught.value.body == payload


@pytest.mark.parametrize(
    "retry_after, expected",
    [
        pytest.param("7", 7, id="seconds"),
        pytest.param(
            "Wed, 21 Oct 2999 07:28:00 GMT",
            Retry().retry_after_max,
            id="http-date-capped",
        ),
        pytest.param("invalid", 60, id="malformed-fallback"),
        pytest.param(None, 60, id="missing-fallback"),
    ],
)
def test_rate_limit_error(retry_after, expected, make_resp):
    headers = {} if retry_after is None else {"retry-after": retry_after}
    response = make_resp(429, {"error": {"message": "slow down"}}, headers)
    with pytest.raises(TooManyRequestsError) as caught:
        _check_resp(response)
    assert caught.value.retry_delay == expected
    assert caught.value.message == "slow down"
    assert caught.value.response is response


async def test_context_lifecycle() -> None:
    session = MagicMock()
    session.headers = {}
    session.close = AsyncMock()
    with patch(
        "padwan_ai.typesafe.client.niquests.AsyncSession", return_value=session
    ) as factory:
        client = TypeSafeClient(api_key="secret")
        async with client as opened:
            assert opened is client
            assert client.session is session
            assert session.headers["Authorization"] == "Bearer secret"
        assert client._session is None
        session.close.assert_awaited_once()
    assert factory.call_args.kwargs["timeout"] == 60


@pytest.mark.parametrize(
    "api_key, env_key, ctx",
    [
        pytest.param("explicit", None, nullcontext(), id="explicit"),
        pytest.param(None, "environment", nullcontext(), id="environment"),
        pytest.param(
            None, None, pytest.raises(LLMError, match="TYPESAFE_API_KEY"), id="missing"
        ),
    ],
)
def test_api_key_resolution(api_key, env_key, ctx, monkeypatch):
    if env_key is None:
        monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    else:
        monkeypatch.setenv("TYPESAFE_API_KEY", env_key)
    with ctx:
        client = TypeSafeClient(api_key=api_key)
        assert "explicit" not in repr(client)
        assert "environment" not in repr(client)


async def test_niquests_retries_twice_then_maps_rate_limit() -> None:
    class RateLimitHandler(BaseHTTPRequestHandler):
        attempts = 0

        def do_POST(self) -> None:
            type(self).attempts += 1
            self.send_response(429)
            self.send_header("content-type", "application/json")
            self.send_header("retry-after", "0")
            self.end_headers()
            self.wfile.write(b'{"error":{"message":"slow down"}}')

        def log_message(self, format: str, *args: object) -> None:
            return

    try:
        server = ThreadingHTTPServer(("127.0.0.1", 0), RateLimitHandler)
    except PermissionError:
        pytest.skip("loopback sockets are unavailable in this sandbox")
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        host, port = cast("tuple[str, int]", server.server_address)
        client = TypeSafeClient(api_key="test", base_url=f"http://{host}:{port}/")
        with pytest.raises(TooManyRequestsError) as caught:
            async with client:
                await client.system_one("ticket", QUESTIONS)
        assert caught.value.message == "slow down"
        assert RateLimitHandler.attempts == 3
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_public_models() -> None:
    assert TYPESAFE_MODELS == {"jev-latest", "jev-preview"}
