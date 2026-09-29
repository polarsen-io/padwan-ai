from __future__ import annotations

import base64
import operator
import struct
from typing import TYPE_CHECKING, Literal, overload

if TYPE_CHECKING:
    from .gemini.models import EmbedContentsResponse
    from .openai.types import CreateEmbeddingResponse

__all__ = ("vectors",)

_INDEX = operator.itemgetter("index")

OpenAIShaped = Literal["openai", "mistral", "grok", "voyage"]


def _floats(embedding: list[float] | str) -> list[float]:
    """Decode an ``encoding_format="base64"`` embedding (little-endian float32)."""
    if isinstance(embedding, list):
        return embedding
    raw = base64.b64decode(embedding)
    return list(struct.unpack(f"<{len(raw) // 4}f", raw))


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
    ``index`` per item, so they are sorted by it; base64 items
    (``encoding_format="base64"``) are decoded to floats.
    """
    # The overloads tie payload type to provider; no runtime re-validation.
    if provider == "gemini":
        return [item["values"] for item in resp["embeddings"]]  # pyright: ignore[reportGeneralTypeIssues]
    return [_floats(item["embedding"]) for item in sorted(resp["data"], key=_INDEX)]  # pyright: ignore[reportGeneralTypeIssues]
