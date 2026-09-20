from __future__ import annotations

import operator
from typing import TYPE_CHECKING, Literal, overload

if TYPE_CHECKING:
    from .gemini.models import EmbedContentsResponse
    from .openai.types import CreateEmbeddingResponse

__all__ = ("vectors",)

_INDEX = operator.itemgetter("index")

OpenAIShaped = Literal["openai", "mistral", "grok", "voyage"]


@overload
def vectors(
    resp: EmbedContentsResponse, provider: Literal["gemini"]
) -> list[list[float]]: ...
@overload
def vectors(
    resp: CreateEmbeddingResponse, provider: OpenAIShaped = "openai"
) -> list[list[float]]: ...
def vectors(
    resp: EmbedContentsResponse | CreateEmbeddingResponse,
    provider: OpenAIShaped | Literal["gemini"] = "openai",
) -> list[list[float]]:
    """Extract embedding vectors, one per input text, from a `fetch_embeddings` payload.

    ``provider`` names the payload shape: Gemini responses are documented to
    follow input order and carry no index, so they are returned as-is. The
    OpenAI-shaped responses (OpenAI, Mistral, Grok, Voyage) promise only an
    ``index`` per item, so they are sorted by it.
    """
    # The overloads tie payload type to provider; no runtime re-validation.
    if provider == "gemini":
        return [item["values"] for item in resp["embeddings"]]  # pyright: ignore[reportGeneralTypeIssues]
    return [item["embedding"] for item in sorted(resp["data"], key=_INDEX)]  # pyright: ignore[reportGeneralTypeIssues]
