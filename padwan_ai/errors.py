from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    import niquests

Provider = Literal[
    "openai", "gemini", "mistral", "grok", "anthropic", "typesafe", "voyage"
]

__all__ = (
    "LLMError",
    "OutputError",
    "OutputFailure",
    "Provider",
    "QuotaExceededError",
    "TooManyRequestsError",
)


class LLMError(Exception):
    def __init__(
        self,
        provider: Provider,
        message: str,
        cause: Exception | None = None,
        body: dict | None = None,
    ):
        self.provider = provider
        self.cause = cause
        self.body = body
        super().__init__(f"[{provider}] {message}")


@dataclasses.dataclass
class TooManyRequestsError(Exception):
    retry_delay: int
    message: str | None = None
    response: niquests.Response | None = None


@dataclasses.dataclass
class QuotaExceededError(Exception):
    body: dict


OutputFailure = Literal["invalid_answer", "text_answer", "round_limit"]
"""Why a typed run failed: `submit` was called but never validated, the model
answered in text without calling it, or `max_tool_rounds` ran out first."""


class OutputError(Exception):
    """An `AgentSession` run with `output=` ended without a valid answer.

    `reason` says which failure it was, so callers can branch on it rather
    than on the message; it is `None` only on errors raised outside padwan.
    """

    def __init__(
        self,
        message: str,
        *,
        reason: OutputFailure | None = None,
        attempts: int = 0,
        details: str | None = None,
    ):
        self.reason = reason
        self.attempts = attempts
        self.details = details
        super().__init__(message)
