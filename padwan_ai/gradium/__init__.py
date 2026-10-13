# Python 3.15 defers provider components until first use.
__lazy_modules__ = frozenset({"padwan_ai.gradium.client"})

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
)

__all__ = (
    "GRADIUM_ENDPOINT",
    "GradiumClient",
    "GradiumInputFormat",
    "GradiumKeywords",
    "GradiumLanguage",
    "GradiumOutputFormat",
    "GradiumSTTConfig",
    "GradiumSegment",
    "GradiumSpeech",
    "GradiumTTSConfig",
    "GradiumTranscription",
)
