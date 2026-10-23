from __future__ import annotations

import dataclasses
import typing
from collections.abc import AsyncGenerator, AsyncIterator, Callable, Mapping, Sequence
from contextlib import aclosing
from dataclasses import field
from functools import partial
from http import HTTPStatus
from pathlib import Path
from typing import TYPE_CHECKING, ClassVar, Literal, cast, get_args

import niquests
from urllib3.util.retry import Retry

from .._base import (
    RETRY_AFTER_MAX,
    ChatStream,
    LLMClientBase,
    Provider,
    env_api_key_for_base_url,
    retry_after_delay,
)
from .._json import dumps as _json_dumps, loads as _json_loads
from ..content import _read_audio
from ..conversation import ChatMessage
from ..errors import LLMError, QuotaExceededError, TooManyRequestsError
from ..logs import log
from ..models import (
    ChatResponse,
    FinishReason,
    RequestHeaders,
    ToolCall,
    ToolCallFunction,
    ToolDefinition,
    UsageToken,
)
from .audio import Transcription
from .batch import BatchJob, BatchRequest, BatchResult
from .tools import OpenAIToolMixin
from .types import Batch, ListBatchesResponse, OpenAIFile

# Normalize provider-specific finish reasons to our FinishReason values.
# https://platform.openai.com/docs/api-reference/chat/object#chat/object-choices
_OPENAI_FINISH_REASON_MAP: dict[str, FinishReason] = {
    "stop": "stop",
    "length": "length",
    "tool_calls": "tool_calls",
    "content_filter": "content_filter",
    "function_call": "tool_calls",
    "model_length": "length",
    "error": "error",
}


def _extract_text_payload(payload: dict[str, typing.Any]) -> str | None:
    """Pull plain answer text out of a `delta` or `message` dict.

    Handles two shapes interchangeably: a plain string `content` (OpenAI,
    Grok), or Mistral's structured `content: list[ContentChunk]` where
    we keep only `type: "text"` chunks and concatenate them. `thinking`
    chunks are ignored here — they go through `_extract_thought_payload`.
    """
    content = payload.get("content")
    if isinstance(content, str):
        return content or None
    if isinstance(content, list):
        texts: list[str] = []
        for chunk in content:
            if isinstance(chunk, dict) and chunk.get("type") == "text":
                if t := chunk.get("text"):
                    texts.append(t)
        if texts:
            return "".join(texts)
    return None


def _extract_thought_payload(payload: dict[str, typing.Any]) -> str | None:
    """Reasoning text from `reasoning_content`, `reasoning` or Mistral thinking chunks."""
    if rc := payload.get("reasoning_content") or payload.get("reasoning"):
        return rc if isinstance(rc, str) else None
    content = payload.get("content")
    if isinstance(content, list):
        thoughts: list[str] = []
        for chunk in content:
            if not isinstance(chunk, dict) or chunk.get("type") != "thinking":
                continue
            for inner in chunk.get("thinking") or []:
                if isinstance(inner, dict) and inner.get("type") == "text":
                    if t := inner.get("text"):
                        thoughts.append(t)
        if thoughts:
            return "".join(thoughts)
    return None


if TYPE_CHECKING:
    from .types import (
        CompletionUsage,
        CreateChatCompletionRequest,
        CreateChatCompletionResponse,
        CreateChatCompletionStreamResponse,
        CreateEmbeddingRequest,
        CreateEmbeddingResponse,
    )

OpenAIModel = Literal[
    "gpt-4o",
    "gpt-4o-mini",
    "gpt-4-turbo",
    "gpt-4",
    "gpt-4.1",
    "gpt-4.1-mini",
    "gpt-4.1-nano",
    "gpt-5",
    "gpt-5-mini",
    "gpt-5-nano",
    "gpt-5.1",
    "gpt-5.1-mini",
    "gpt-5.1-codex",
    "gpt-5.2",
    "gpt-5.2-pro",
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gpt-5.5",
    "gpt-5.6-luna",
    "gpt-5.6-sol",
    "gpt-5.6-terra",
    "gpt-6-astra",
    "gpt-6-luna",
    "gpt-6-sol",
    "gpt-6.1-sol",
    "o1",
    "o1-mini",
    "o1-preview",
    "o3",
    "o3-mini",
    "o4-mini",
    "codex-mini-latest",
]

__all__ = (
    "OPENAI_CHAT_MODELS",
    "OPENAI_ENDPOINT",
    "OPENAI_MODELS",
    "OpenAIClient",
    "OpenAIEmbeddingModel",
    "OpenAIModel",
    "_OpenAIBase",
    "is_openai_model",
)


def _check_resp_status(resp: niquests.Response) -> niquests.Response:
    """Check HTTP status and raise appropriate errors without consuming the body."""
    try:
        return resp.raise_for_status()
    except niquests.exceptions.HTTPError as e:
        try:
            data = resp.json()
        except ValueError:  # not JSON; a read error propagates
            data = None
        _raise_http_error(resp, data, e)


async def _check_stream_status(resp: niquests.AsyncResponse) -> None:
    """`_check_resp_status` for a response opened with ``stream=True``: its body is read
    (awaited) only on a failure, to name the error."""
    try:
        resp.raise_for_status()
    except niquests.exceptions.HTTPError as e:
        try:
            data = await resp.json()
        except ValueError:  # not JSON; a read error propagates
            data = None
        _raise_http_error(resp, data, e)


def _raise_http_error(
    resp: niquests.Response, data: typing.Any, cause: niquests.exceptions.HTTPError
) -> typing.NoReturn:
    """Raise the padwan error for a failed response; `data` is its JSON body, or None if not JSON."""
    if resp.status_code == HTTPStatus.TOO_MANY_REQUESTS:
        raise TooManyRequestsError(
            retry_delay=retry_after_delay(resp.headers.get("retry-after")),
            response=resp,
        ) from cause
    if data is None:
        raise cause
    if resp.status_code == HTTPStatus.PAYMENT_REQUIRED:
        raise QuotaExceededError(body=data)
    error = data.get("error", "") if isinstance(data, dict) else data
    if isinstance(error, dict):
        msg = error.get("message", "")
    elif isinstance(data, dict) and data.get("message"):
        # some OpenAI-compatible backends use {"error": "...", "message": "..."}
        msg = f"{error} — {data['message']}" if error else str(data["message"])
    else:
        msg = str(error)
    raise LLMError("openai", f"{resp.status_code} {msg}", body=data) from cause


def _check_resp[T](
    resp: niquests.Response, *, decoder: Callable[[bytes], T] | None = None
) -> T:
    """Check OpenAI-compatible HTTP response and return the parsed JSON body,
    deserialized through `decoder` when provided (e.g. msgspec for typed validation)."""
    checked = _check_resp_status(resp)
    if decoder is None:
        return checked.json()
    if not (body := checked.content):
        raise LLMError("openai", "Empty response body")
    return decoder(body)


OpenAIEmbeddingModel = Literal[
    "text-embedding-3-small",
    "text-embedding-3-large",
    "text-embedding-ada-002",
]

_OPENAI_PREFIXES = (
    "gpt-",
    "o1",
    "o3",
    "o4",
    "chatgpt-",
    "codex-",
    "text-embedding-",
)


def is_openai_model(model_name: str | None) -> bool:
    """Check if the model name looks like an OpenAI model based on known prefixes."""
    if model_name is None:
        return False
    return model_name.startswith(_OPENAI_PREFIXES)


OPENAI_MODELS: set[str] = set(get_args(OpenAIModel))

# Models in OPENAI_MODELS that do not accept /v1/chat/completions requests:
#   - gpt-5.2-pro: reasoning/pro tier, exposed only via the /v1/responses API
#   - codex-mini-latest: legacy /v1/completions endpoint (text completion)
_OPENAI_NON_CHAT_MODELS: frozenset[str] = frozenset(
    {"gpt-5.2-pro", "codex-mini-latest"}
)

OPENAI_CHAT_MODELS: frozenset[str] = frozenset(OPENAI_MODELS - _OPENAI_NON_CHAT_MODELS)

OPENAI_ENDPOINT = "https://api.openai.com/v1/"


class _OpenAIAuth:
    """OpenAI provider identity, shared by the chat and realtime clients."""

    provider: ClassVar[Provider] = "openai"
    base_url: str

    def _get_default_api_key(self) -> str:
        # Never leak OPENAI_API_KEY to a third-party endpoint.
        return env_api_key_for_base_url(
            self.provider, "OPENAI_API_KEY", self.base_url, OPENAI_ENDPOINT
        )


@dataclasses.dataclass
class _OpenAIBase(_OpenAIAuth, LLMClientBase[Retry], OpenAIToolMixin):
    """OpenAI-compatible base client with chat and auth logic.

    Shared by OpenAIClient, GrokClient, and MistralClient. Does not include
    batch methods — those live on the concrete provider clients.
    """

    model: str | None = "gpt-4o"
    base_url: str = OPENAI_ENDPOINT
    _embedding_dimensions_key: ClassVar[str] = "dimensions"
    """Wire key for the requested embedding size; differs across OpenAI-compatible APIs."""
    _retry: Retry = field(
        default_factory=partial(
            Retry,
            total=3,
            backoff_factor=0.5,
            status_forcelist=[
                # Standard
                500,  # Internal Server Error
                502,  # Bad Gateway
                503,  # Service Unavailable
                504,  # Gateway Timeout
                # Cloudflare-proprietary
                520,  # Unknown Error
                522,  # Connection Timed Out
                524,  # A Timeout Occurred
            ],
            allowed_methods=["POST"],
            retry_after_max=RETRY_AFTER_MAX,
        )
    )

    def _set_auth_headers(self, session: niquests.AsyncSession) -> None:
        session.headers["Authorization"] = f"Bearer {self._api_key}"

    async def complete(
        self,
        body: CreateChatCompletionRequest,
        *,
        headers: RequestHeaders | None = None,
    ) -> tuple[CreateChatCompletionResponse, UsageToken]:
        """Fetch structured completion from an OpenAI-compatible endpoint.

        ``headers`` are sent with this request only, merged over the session's (a
        same-named key, ``Authorization`` included, wins).
        """
        resp = await self.session.post(
            "/chat/completions",
            json=body,
            headers=dict(headers) if headers else None,
        )
        data: CreateChatCompletionResponse = _check_resp(resp)

        usage: CompletionUsage | None = data.get("usage")
        if usage is None:
            raise LLMError(self.provider, "No usage in response")
        token: UsageToken = {
            "total": usage["total_tokens"],
            "input": usage["prompt_tokens"],
            "output": usage["completion_tokens"],
        }
        if details := usage.get("prompt_tokens_details"):
            if (cached := details.get("cached_tokens")) is not None:
                token["cached"] = cached
        if details := usage.get("completion_tokens_details"):
            if reasoning := details.get("reasoning_tokens"):
                token["reasoning"] = reasoning

        return data, token

    async def stream(
        self,
        body: CreateChatCompletionRequest,
        *,
        headers: RequestHeaders | None = None,
    ) -> AsyncIterator[CreateChatCompletionStreamResponse]:
        """Stream chat completions, yielding response chunks as they arrive via SSE.

        ``headers`` are sent with this request only, as in `complete`.
        """
        resp = await self.session.post(
            self._sse_url("/chat/completions"),
            json={**body, "stream": True},
            headers=dict(headers) if headers else None,
        )
        _check_resp_status(resp)
        async with aclosing(self._iter_sse(resp, done_sentinel="[DONE]")) as events:
            async for payload in events:
                yield cast("CreateChatCompletionStreamResponse", payload)

    async def stream_raw(
        self,
        body: CreateChatCompletionRequest,
        *,
        headers: RequestHeaders | None = None,
        chunk_size: int = -1,
    ) -> AsyncGenerator[bytes]:
        """Stream a chat completion as the provider's raw SSE bytes, for relaying unchanged.

        Errors raise before the first byte; ``chunk_size=-1`` yields bytes as they arrive.
        """
        resp = await self.session.post(
            "/chat/completions",
            json={**body, "stream": True},
            headers=dict(headers) if headers else None,
            stream=True,
        )
        try:
            await _check_stream_status(resp)
            async for chunk in await resp.iter_content(chunk_size):
                yield chunk
        finally:
            # Aborting an HTTP/2 stream can raise in urllib3-future, as in `_iter_sse`.
            try:
                await resp.close()
            except Exception as e:
                log.debug("stream_raw close failed: %s", e)

    def _prepare_messages(
        self, messages: Sequence[ChatMessage]
    ) -> Sequence[ChatMessage]:
        """Hook for providers whose message wire format diverges from OpenAI's."""
        return messages

    async def fetch_embeddings(
        self,
        input: str | list[str],
        model: str | None = None,
        *,
        dimensions: int | None = None,
        extra_params: dict[str, typing.Any] | None = None,
    ) -> CreateEmbeddingResponse:
        """Embed one text or a batch; ``model`` falls back to the client's default model.

        Match vectors to inputs by each item's ``index``: the API does not
        promise ``data`` order (see :func:`padwan_ai.embeddings.vectors`).
        ``dimensions`` requests a reduced vector size on models that support it.
        ``extra_params`` is merged into the request body for provider-only fields.
        """
        _model = model or self.model
        if not _model:
            raise LLMError(self.provider, "No model specified")
        body: CreateEmbeddingRequest = {"model": _model, "input": input}
        if dimensions is not None:
            body[self._embedding_dimensions_key] = dimensions  # pyright: ignore[reportGeneralTypeIssues]
        if extra_params:
            body.update(cast(typing.Any, extra_params))
        resp = await self.session.post("/embeddings", json=body)
        data: CreateEmbeddingResponse = _check_resp(resp)
        return data

    async def complete_chat(
        self,
        messages: Sequence[ChatMessage],
        tools: Sequence[ToolDefinition] | None = None,
        extra_params: dict[str, typing.Any] | None = None,
        *,
        headers: RequestHeaders | None = None,
    ) -> tuple[ChatResponse, UsageToken]:
        """Send a chat conversation and return the structured response; ``headers`` as in `complete`."""
        if not self.model:
            raise LLMError(self.provider, "No model specified")
        body: CreateChatCompletionRequest = {
            "model": self.model,
            "messages": cast(list, self._prepare_messages(messages)),
            "temperature": self.temperature,
        }
        if tools:
            body["tools"] = cast(list, self._tools_to_openai(tools))
        if extra_params:
            body.update(cast(typing.Any, extra_params))
        # Keep the one-arg call so `complete(body)` overrides keep working.
        data, token = await (
            self.complete(body, headers=headers) if headers else self.complete(body)
        )
        choice = data["choices"][0]
        message_dict = cast(dict[str, typing.Any], choice["message"])
        raw_reason = choice.get("finish_reason", "stop")
        # Forward any reasoning content to on_thought before unpacking the
        # answer text — keeps the final ChatResponse free of the model's
        # internal scratchpad. Same shape on both wire formats handled by
        # `_extract_thought_payload` (Grok `reasoning_content`, Mistral
        # `ThinkChunk` inside a structured content array).
        if self.on_thought and (thought := _extract_thought_payload(message_dict)):
            self.on_thought(thought)
        response: ChatResponse = {
            "content": _extract_text_payload(message_dict),
            "finish_reason": _OPENAI_FINISH_REASON_MAP.get(raw_reason, "other"),
        }
        if raw_tool_calls := message_dict.get("tool_calls"):
            response["tool_calls"] = self._extract_tool_calls(
                cast(list, raw_tool_calls)
            )
        return response, token

    def stream_chat(
        self,
        messages: Sequence[ChatMessage],
        tools: Sequence[ToolDefinition] | None = None,
        extra_params: dict[str, typing.Any] | None = None,
        *,
        headers: RequestHeaders | None = None,
    ) -> OpenAIChatStream:
        """Stream a chat conversation, yielding text chunks.

        Usage and tool_calls are available on the returned stream object after iteration.
        The optional ``extra_params`` dict is merged into the request body verbatim,
        so provider-specific fields (e.g. NVIDIA's ``chat_template_kwargs``) can be
        passed without modifying the client. ``headers`` are as in `complete`.
        """
        return OpenAIChatStream(
            self, messages, tools, extra_params=extra_params, headers=headers
        )


@dataclasses.dataclass
class OpenAIChatStream(ChatStream, OpenAIToolMixin):
    """ChatStream implementation for OpenAI-compatible APIs."""

    client: _OpenAIBase
    messages: Sequence[ChatMessage]
    tools: Sequence[ToolDefinition] | None = None
    extra_params: dict[str, typing.Any] | None = None
    headers: RequestHeaders | None = None
    usage: UsageToken | None = None
    tool_calls: list[ToolCall] | None = None
    finish_reason: str | None = None

    async def __aiter__(self) -> AsyncIterator[str]:
        if not self.client.model:
            raise LLMError(self.client.provider, "No model specified")
        body: CreateChatCompletionRequest = {
            "model": self.client.model,
            "messages": cast(list, self.client._prepare_messages(self.messages)),
            "temperature": self.client.temperature,
            "stream_options": {"include_usage": True},
        }
        if self.tools:
            body["tools"] = cast(list, self._tools_to_openai(self.tools))
        if self.extra_params:
            body.update(cast(typing.Any, self.extra_params))

        # Accumulate tool call deltas keyed by index
        pending: dict[int, dict[str, str]] = {}

        chunks = (
            self.client.stream(body, headers=self.headers)
            if self.headers
            else self.client.stream(body)
        )
        async for chunk in chunks:
            delta = self._delta(chunk)
            if delta is not None:
                if self.client.on_thought and (
                    thought := _extract_thought_payload(delta)
                ):
                    self.client.on_thought(thought)
                if text := _extract_text_payload(delta):
                    yield text
            if choices := chunk.get("choices"):
                if reason := choices[0].get("finish_reason"):
                    self.finish_reason = reason
            self._accumulate_tool_call_deltas(chunk, pending)
            if usage := self._extract_usage(chunk):
                self.usage = usage

        if pending:
            self.tool_calls = [
                ToolCall(
                    id=tc["id"],
                    type="function",
                    function=ToolCallFunction(
                        name=tc["name"], arguments=tc["arguments"]
                    ),
                )
                for tc in (pending[i] for i in sorted(pending))
            ]

    @staticmethod
    def _delta(
        chunk: CreateChatCompletionStreamResponse,
    ) -> dict[str, typing.Any] | None:
        """Return the first choice's `delta` dict, or None if absent."""
        if choices := chunk.get("choices"):
            if delta := choices[0].get("delta"):
                return cast(dict[str, typing.Any], delta)
        return None

    def _extract_text(self, chunk: CreateChatCompletionStreamResponse) -> str | None:
        """Extract text content from an OpenAI stream response chunk.

        Kept for backwards compatibility with subclasses that still call
        it. New code should go through `__aiter__`'s shared payload
        helpers (`_extract_text_payload`, `_extract_thought_payload`).
        """
        delta = self._delta(chunk)
        return _extract_text_payload(delta) if delta else None

    @staticmethod
    def _extract_usage(chunk: CreateChatCompletionStreamResponse) -> UsageToken | None:
        """Extract usage info from an OpenAI stream response chunk (final chunk)."""
        if usage := chunk.get("usage"):
            token: UsageToken = {
                "total": usage.get("total_tokens", 0),
                "input": usage.get("prompt_tokens", 0),
                "output": usage.get("completion_tokens", 0),
            }
            if details := usage.get("prompt_tokens_details"):
                if (cached := details.get("cached_tokens")) is not None:
                    token["cached"] = cached
            if details := usage.get("completion_tokens_details"):
                if reasoning := details.get("reasoning_tokens"):
                    token["reasoning"] = reasoning
            return token
        return None


_TRANSCRIBE_FIELDS = frozenset({"file", "model", "language", "prompt", "temperature"})
"""Form fields `transcribe` sets from its own arguments."""


@dataclasses.dataclass
class OpenAIClient(_OpenAIBase):
    """OpenAI API client with chat and batch support."""

    async def transcribe(
        self,
        *,
        file: str | Path | bytes,
        filename: str | None = None,
        content_type: str | None = None,
        model: str = "whisper-1",
        language: str | None = None,
        prompt: str | None = None,
        temperature: float | None = None,
        headers: RequestHeaders | None = None,
        extra_params: Mapping[str, str] | Sequence[tuple[str, str]] | None = None,
    ) -> Transcription:
        """Transcribe audio with ``POST /audio/transcriptions`` (multipart).

        ``file`` is a path or raw bytes. The provider reads the audio format from the
        file name's extension, so raw bytes need ``filename`` (e.g. ``"note.webm"``).
        ``prompt`` steers spelling and vocabulary; ``headers`` are sent with this
        request only, as in `complete`. ``extra_params`` adds form fields for
        provider-only parameters (e.g. a gateway's ``metadata``, as a JSON string);
        pass pairs to repeat a field (e.g. ``timestamp_granularities[]``). A field
        that has a named argument here raises ``ValueError``: use the argument.
        """
        if isinstance(file, bytes) and not filename:
            raise ValueError("filename is required with raw bytes")
        audio = await _read_audio(file, filename=filename, content_type=content_type)
        data: list[tuple[str, str]] = [("model", model)]
        if language is not None:
            data.append(("language", language))
        if prompt is not None:
            data.append(("prompt", prompt))
        if temperature is not None:
            data.append(("temperature", str(temperature)))
        if extra_params:
            extra = list(
                extra_params.items()
                if isinstance(extra_params, Mapping)
                else extra_params
            )
            if clash := _TRANSCRIBE_FIELDS & {name for name, _ in extra}:
                raise ValueError(
                    f"extra_params sets named arguments: {', '.join(sorted(clash))}"
                )
            data.extend(extra)
        resp = await self.session.post(
            "/audio/transcriptions",
            files=[("file", audio)],
            data=data,
            headers=dict(headers) if headers else None,
        )
        result: Transcription = _check_resp(resp)
        return result

    async def upload_batch_file(
        self,
        requests: list[BatchRequest],
        model: str | None = None,
    ) -> str:
        """Serialize batch requests to JSONL and upload via POST /files.

        Each line in the JSONL file is an OpenAI batch request object with
        `custom_id`, `method`, `url`, and `body` fields. Returns the file ID.
        """
        _model = model or self.model
        if not _model:
            raise LLMError(self.provider, "No model specified")
        lines: list[str] = []
        for idx, req in enumerate(requests):
            line = {
                "custom_id": req.custom_id or f"request-{idx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {**req.body, "model": _model},
            }
            lines.append(_json_dumps(line))
        content = "\n".join(lines)

        resp = await self.session.post(
            "/files",
            data={"purpose": "batch"},
            files={"file": ("batch.jsonl", content, "application/jsonl")},
        )
        data: OpenAIFile = _check_resp(resp)
        return data["id"]

    async def create_batch(
        self,
        requests: list[BatchRequest],
        model: str | None = None,
        metadata: dict[str, str] | None = None,
        completion_window: str = "24h",
    ) -> BatchJob:
        """Create an OpenAI batch from a list of requests.

        Uploads the requests as a JSONL file, then creates a batch
        referencing that file. The `completion_window` defaults to "24h"
        (currently the only value OpenAI supports).
        """
        file_id = await self.upload_batch_file(requests, model)
        payload: dict = {
            "input_file_id": file_id,
            "endpoint": "/v1/chat/completions",
            "completion_window": completion_window,
        }
        if metadata:
            payload["metadata"] = metadata
        resp = await self.session.post("/batches", json=payload)
        data: Batch = _check_resp(resp)
        return BatchJob.load(data)

    async def get_batch(self, batch_id: str) -> BatchJob:
        """Get the current status of a batch."""
        resp = await self.session.get(f"/batches/{batch_id}")
        data: Batch = _check_resp(resp)
        return BatchJob.load(data)

    async def list_batches(
        self,
        limit: int = 20,
        after: str | None = None,
    ) -> tuple[list[BatchJob], str | None]:
        """List batches with cursor-based pagination.

        Returns a tuple of (jobs, next_cursor). Pass `next_cursor` as `after`
        to fetch the next page.
        """
        params: dict[str, str] = {"limit": str(limit)}
        if after:
            params["after"] = after
        resp = await self.session.get("/batches", params=params)
        data: ListBatchesResponse = _check_resp(resp)
        jobs = [BatchJob.load(item) for item in data.get("data", [])]
        next_cursor: str | None = None
        if data.get("has_more"):
            next_cursor = data.get("last_id")
        return jobs, next_cursor

    async def cancel_batch(self, batch_id: str) -> BatchJob:
        """Cancel a batch that is in progress."""
        resp = await self.session.post(f"/batches/{batch_id}/cancel")
        data: Batch = _check_resp(resp)
        return BatchJob.load(data)

    async def get_batch_results(self, output_file_id: str) -> list[BatchResult]:
        """Download and parse the output JSONL file for a completed batch."""
        resp = await self.session.get(f"/files/{output_file_id}/content")
        _check_resp_status(resp)
        text = resp.text or ""
        results: list[BatchResult] = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            results.append(BatchResult.from_line(_json_loads(line)))
        return results
