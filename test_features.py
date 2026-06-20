"""Backend feature tests for Classroom Copilot education engine."""

from services.gemini_service import GeminiService
from services.intent_classifier import (
    INTENT_ACTIVITY,
    INTENT_CONCEPT,
    INTENT_QUIZ,
    INTENT_TRANSLATION,
    classify_intent,
)


def test_concept(gemini_service: GeminiService) -> None:
    """Test concept simplification generation."""
    command = "Explain photosynthesis to class 6"
    intent = classify_intent(command)
    explanation = gemini_service.generate_explanation(topic="photosynthesis", grade_level="6")
    print("Test 1 - Concept Intent:", intent.intent, "| Expected:", INTENT_CONCEPT)
    print("Test 1 - Concept Explanation:", explanation)
    print("-" * 80)


def test_quiz(gemini_service: GeminiService) -> None:
    """Test quiz generation output."""
    command = "Create a quiz on photosynthesis"
    intent = classify_intent(command)
    quiz = gemini_service.generate_quiz(topic="photosynthesis")
    print("Test 2 - Quiz Intent:", intent.intent, "| Expected:", INTENT_QUIZ)
    print("Test 2 - Quiz Count:", len(quiz))
    print("Test 2 - Quiz JSON:", quiz)
    print("-" * 80)


def test_translation(gemini_service: GeminiService) -> None:
    """Test translation in both directions."""
    command = "Translate this paragraph"
    intent = classify_intent(command)
    en_to_hi = gemini_service.generate_translation(
        text="Plants need sunlight to make food.",
        direction="en_to_hi",
    )
    hi_to_en = gemini_service.generate_translation(
        text="Paudhe khana banane ke liye dhoop ka upyog karte hain.",
        direction="hi_to_en",
    )
    print("Test 3 - Translation Intent:", intent.intent, "| Expected:", INTENT_TRANSLATION)
    print("Test 3 - EN to HI:", en_to_hi)
    print("Test 3 - HI to EN:", hi_to_en)
    print("-" * 80)


def test_activity(gemini_service: GeminiService) -> None:
    """Test activity guide generation."""
    command = "Start a 3 minute group discussion activity"
    intent = classify_intent(command)
    activity = gemini_service.generate_activity(duration_minutes=3, topic="photosynthesis")
    print("Test 4 - Activity Intent:", intent.intent, "| Expected:", INTENT_ACTIVITY)
    print("Test 4 - Activity JSON:", activity)
    print("-" * 80)


def main() -> None:
    """Run all backend feature tests independently."""
    gemini_service = GeminiService()
    test_concept(gemini_service)
    test_quiz(gemini_service)
    test_translation(gemini_service)
    test_activity(gemini_service)


if __name__ == "__main__":
    main()
