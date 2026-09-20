from __future__ import annotations

import dataclasses
from typing import ClassVar, Literal, get_args

from .._base import Provider, env_api_key
from ..openai.client import _OpenAIBase

VoyageModel = Literal[
    "voyage-4-large",
    "voyage-4",
    "voyage-4-lite",
    "voyage-code-4",
    "voyage-finance-2",
    "voyage-law-2",
]

__all__ = (
    "VOYAGE_ENDPOINT",
    "VOYAGE_MODELS",
    "VoyageClient",
    "VoyageModel",
    "is_voyage_model",
)


def is_voyage_model(model_name: str | None) -> bool:
    """Check if the model name looks like a Voyage AI model based on its prefix."""
    if model_name is None:
        return False
    return model_name.startswith("voyage-")


VOYAGE_MODELS: set[str] = set(get_args(VoyageModel))

VOYAGE_ENDPOINT = "https://api.voyageai.com/v1/"


@dataclasses.dataclass
class VoyageClient(_OpenAIBase):
    """Voyage AI embeddings client (the provider Anthropic recommends for embeddings).

    https://docs.voyageai.com/reference/embeddings-api
    """

    # ponytail: only /embeddings exists upstream; the inherited chat methods 404.
    provider: ClassVar[Provider] = "voyage"
    model: str | None = "voyage-4"
    base_url: str = VOYAGE_ENDPOINT
    _embedding_dimensions_key: ClassVar[str] = "output_dimension"

    def _get_default_api_key(self) -> str:
        return env_api_key(self.provider, "VOYAGE_API_KEY")
