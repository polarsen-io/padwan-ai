# Python 3.15 defers provider components until first use.
__lazy_modules__ = frozenset({"padwan_ai.gradium.client", "padwan_ai.gradium.realtime"})

from .client import (
    GRADIUM_ENDPOINT,
    GradiumClient,
    GradiumInputFormat,
    GradiumKeywords,
    GradiumLanguage,
    GradiumOutputFormat,
    GradiumSegment,
    GradiumSpeech,
    GradiumSTTConfig,
    GradiumTranscription,
    GradiumTTSConfig,
    GradiumVoice,
    GradiumVoiceLanguage,
    GradiumVoiceTag,
)
from .realtime import (
    GRADIUM_WS_ENDPOINT,
    GradiumRealtimeInputFormat,
    GradiumRealtimeS2SClient,
    GradiumRealtimeSTTClient,
    GradiumRealtimeTTSClient,
    GradiumS2SConnection,
    GradiumSTTConnection,
    GradiumTTSConnection,
)

__all__ = (
    "GRADIUM_ENDPOINT",
    "GRADIUM_WS_ENDPOINT",
    "GradiumClient",
    "GradiumInputFormat",
    "GradiumKeywords",
    "GradiumLanguage",
    "GradiumOutputFormat",
    "GradiumRealtimeInputFormat",
    "GradiumRealtimeS2SClient",
    "GradiumRealtimeSTTClient",
    "GradiumRealtimeTTSClient",
    "GradiumS2SConnection",
    "GradiumSTTConfig",
    "GradiumSTTConnection",
    "GradiumSegment",
    "GradiumSpeech",
    "GradiumTTSConfig",
    "GradiumTTSConnection",
    "GradiumTranscription",
    "GradiumVoice",
    "GradiumVoiceLanguage",
    "GradiumVoiceTag",
)
