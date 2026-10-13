import dataclasses
import math
from collections.abc import Mapping
from dataclasses import field
from functools import partial
from typing import Any, ClassVar, Literal, cast, get_args

import niquests
from urllib3.exceptions import InvalidHeader
from urllib3.util.retry import Retry

from .._base import StandaloneClientMixin, env_api_key
from ..errors import LLMError, Provider, TooManyRequestsError, _error_message
from .models import JSONContent, Question, SystemOneResponse

TypeSafeModel = Literal["jev-latest", "jev-preview"]

TYPESAFE_MODELS: set[str] = set(get_args(TypeSafeModel))
TYPESAFE_ENDPOINT = "https://api.typesafe.ai/v1/"

__all__ = (
    "TYPESAFE_ENDPOINT",
    "TYPESAFE_MODELS",
    "TypeSafeClient",
    "TypeSafeModel",
)


def _validate_response(data: object) -> SystemOneResponse:
    if not isinstance(data, dict) or not {"model", "answers", "usage"} <= data.keys():
        raise LLMError("typesafe", "Malformed response body")
    return cast("SystemOneResponse", data)


def _check_resp(resp: niquests.Response) -> SystemOneResponse:
    try:
        resp.raise_for_status()
    except niquests.exceptions.HTTPError as error:
        try:
            data: Any = resp.json()
        except Exception:
            data = None
        body = data if isinstance(data, dict) else None
        message = _error_message(data)
        if resp.status_code == 429:
            raw_retry_after = resp.headers.get("retry-after")
            try:
                retry_delay = (
                    60
                    if raw_retry_after is None
                    else math.ceil(Retry().parse_retry_after(raw_retry_after))
                )
            except (InvalidHeader, OverflowError, ValueError):
                retry_delay = 60
            raise TooManyRequestsError(
                retry_delay=retry_delay,
                message=message or None,
                response=resp,
            ) from error
        raise LLMError(
            "typesafe", f"{resp.status_code} {message}".rstrip(), cause=error, body=body
        ) from error
    try:
        data = resp.json()
    except Exception as error:
        raise LLMError("typesafe", "Malformed response body", cause=error) from error
    return _validate_response(data)


@dataclasses.dataclass
class TypeSafeClient(StandaloneClientMixin):
    """Async client for TypeSafe's System One API."""

    provider: ClassVar[Provider] = "typesafe"
    model: str = "jev-latest"
    timeout: float = 60
    api_key: str | None = field(default=None, repr=False)
    base_url: str = TYPESAFE_ENDPOINT
    _retry: Retry = field(
        default_factory=partial(
            Retry,
            total=2,
            backoff_factor=0.5,
            status_forcelist=[408, 429, *range(500, 600)],
            allowed_methods=["POST"],
            respect_retry_after_header=True,
            raise_on_status=False,
        ),
        repr=False,
    )
    _api_key: str = field(init=False, repr=False)
    _session: niquests.AsyncSession | None = field(init=False, default=None, repr=False)

    def __post_init__(self) -> None:
        self._api_key = self.api_key or env_api_key(self.provider, "TYPESAFE_API_KEY")

    def _set_auth_headers(self, session: niquests.AsyncSession) -> None:
        session.headers["Authorization"] = f"Bearer {self._api_key}"
        session.headers["Accept"] = "application/json"

    async def system_one(
        self,
        state: JSONContent,
        questions: Mapping[str, Question],
        *,
        model: str | None = None,
    ) -> SystemOneResponse:
        """Evaluate typed questions against shared state; the API validates the payload."""
        body = {"state": state, "model": model or self.model, "questions": questions}
        resp = await self.session.post("systemone", json=body)
        return _check_resp(resp)
