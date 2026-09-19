# Python 3.15 defers provider components until first use.
__lazy_modules__ = frozenset({"padwan_ai.typesafe.client", "padwan_ai.typesafe.models"})

from .client import TYPESAFE_ENDPOINT, TYPESAFE_MODELS, TypeSafeClient, TypeSafeModel
from .models import (
    Answer,
    ChoiceAnswer,
    ChoiceQuestion,
    JSONContent,
    NoulAnswer,
    NoulCriteria,
    NoulQuestion,
    Question,
    ScoreAnswer,
    ScoreQuestion,
    SystemOneResponse,
    TypeSafeUsage,
)

__all__ = (
    "TYPESAFE_ENDPOINT",
    "TYPESAFE_MODELS",
    "Answer",
    "ChoiceAnswer",
    "ChoiceQuestion",
    "JSONContent",
    "NoulAnswer",
    "NoulCriteria",
    "NoulQuestion",
    "Question",
    "ScoreAnswer",
    "ScoreQuestion",
    "SystemOneResponse",
    "TypeSafeClient",
    "TypeSafeModel",
    "TypeSafeUsage",
)
