# Python 3.15 defers provider components until first use.
__lazy_modules__ = frozenset({"padwan_ai.elevenlabs.client"})

from .client import (
    ELEVENLABS_ENDPOINT,
    ELEVENLABS_MODELS,
    ElevenLabsClient,
    ElevenLabsModel,
    ElevenLabsOutputFormat,
    ElevenLabsSpeech,
    ElevenLabsSTTModel,
    ElevenLabsTranscription,
    ElevenLabsTTSModel,
    ElevenLabsWord,
    VoiceSettings,
)

__all__ = (
    "ELEVENLABS_ENDPOINT",
    "ELEVENLABS_MODELS",
    "ElevenLabsClient",
    "ElevenLabsModel",
    "ElevenLabsOutputFormat",
    "ElevenLabsSTTModel",
    "ElevenLabsSpeech",
    "ElevenLabsTTSModel",
    "ElevenLabsTranscription",
    "ElevenLabsWord",
    "VoiceSettings",
)
