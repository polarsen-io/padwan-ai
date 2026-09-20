# Python 3.15 defers provider components until first use.
__lazy_modules__ = frozenset({"padwan_ai.voyage.client"})

from .client import (
    VOYAGE_ENDPOINT,
    VOYAGE_MODELS,
    VoyageClient,
    VoyageModel,
    is_voyage_model,
)

__all__ = (
    "VOYAGE_ENDPOINT",
    "VOYAGE_MODELS",
    "VoyageClient",
    "VoyageModel",
    "is_voyage_model",
)
