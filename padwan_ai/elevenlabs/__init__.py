# Python 3.15 defers provider components until first use.
__lazy_modules__ = frozenset(
    {"padwan_ai.elevenlabs.client", "padwan_ai.elevenlabs.realtime"}
)

from .client import (
    ELEVENLABS_ENDPOINT,
    ELEVENLABS_MODELS,
    ElevenLabsClient,
    ElevenLabsModel,
    ElevenLabsOutputFormat,
    ElevenLabsSpeech,
    ElevenLabsSTSModel,
    ElevenLabsSTTModel,
    ElevenLabsTranscription,
    ElevenLabsTTSModel,
    ElevenLabsVoice,
    ElevenLabsWord,
    SpeechOptions,
    SpeechToSpeechOptions,
    VoiceSettings,
)
from .realtime import (
    ELEVENLABS_WS_ENDPOINT,
    ElevenLabsRealtimeAudioFormat,
    ElevenLabsRealtimeSTTClient,
    ElevenLabsRealtimeTTSClient,
    ElevenLabsSTTConnection,
    ElevenLabsTTSConnection,
)

__all__ = (
    "ELEVENLABS_ENDPOINT",
    "ELEVENLABS_MODELS",
    "ELEVENLABS_WS_ENDPOINT",
    "ElevenLabsClient",
    "ElevenLabsModel",
    "ElevenLabsOutputFormat",
    "ElevenLabsRealtimeAudioFormat",
    "ElevenLabsRealtimeSTTClient",
    "ElevenLabsRealtimeTTSClient",
    "ElevenLabsSTTConnection",
    "ElevenLabsSTSModel",
    "ElevenLabsSTTModel",
    "ElevenLabsSpeech",
    "ElevenLabsTTSConnection",
    "ElevenLabsTTSModel",
    "ElevenLabsTranscription",
    "ElevenLabsVoice",
    "ElevenLabsWord",
    "SpeechOptions",
    "SpeechToSpeechOptions",
    "VoiceSettings",
)
