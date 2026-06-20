"""Rule-based intent classification for voice commands."""

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentResult:
    """Structured intent classification result."""

    intent: str
    confidence: float


INTENT_CONCEPT = "concept_simplification"
INTENT_QUIZ = "quiz_generation"
INTENT_TRANSLATION = "translation"
INTENT_ACTIVITY = "activity_guide"


def classify_intent(command_text: str) -> IntentResult:
    """Classify command text into one supported classroom intent."""
    text = command_text.lower().strip()

    if any(token in text for token in ("quiz", "mcq")):
        return IntentResult(intent=INTENT_QUIZ, confidence=0.95)

    if any(token in text for token in ("translate", "translation")):
        return IntentResult(intent=INTENT_TRANSLATION, confidence=0.95)

    if any(token in text for token in ("activity", "start", "group discussion", "discussion")):
        return IntentResult(intent=INTENT_ACTIVITY, confidence=0.85)

    return IntentResult(intent=INTENT_CONCEPT, confidence=0.7)
