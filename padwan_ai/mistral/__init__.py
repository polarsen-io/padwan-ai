# Python 3.15 defers provider components until first use.
__lazy_modules__ = frozenset(
    {
        "padwan_ai.mistral.audio",
        "padwan_ai.mistral.client",
        "padwan_ai.mistral.vision",
    }
)

from .audio import AUDIO_FORMATS, supports_audio
from .client import (
    MISTRAL_ENDPOINT,
    MISTRAL_MODELS,
    MistralAudioModel,
    MistralClient,
    MistralEmbeddingModel,
    MistralModel,
    is_mistral_model,
)
from .vision import supports_vision

__all__ = (
    "AUDIO_FORMATS",
    "MISTRAL_ENDPOINT",
    "MISTRAL_MODELS",
    "MistralAudioModel",
    "MistralClient",
    "MistralEmbeddingModel",
    "MistralModel",
    "is_mistral_model",
    "supports_audio",
    "supports_vision",
)
