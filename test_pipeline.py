"""Minimal backend pipeline test script for Classroom Copilot.

Pipeline:
Speech/Text -> Intent Classification -> Gemini Explanation -> Text to Speech
"""

import re
from typing import Tuple

from services.gemini_service import GeminiService
from services.intent_classifier import classify_intent
from services.speech_to_text import SpeechToTextService
from services.text_to_speech import TextToSpeechService


def extract_topic_and_grade(command_text: str) -> Tuple[str, str]:
    """Extract topic and grade level from a command safely."""
    grade_match = re.search(r"class\s*(\d+)", command_text.lower())
    grade_level = grade_match.group(1) if grade_match else "6"

    cleaned = re.sub(r"(?i)^explain\s*", "", command_text).strip()
    cleaned = re.sub(r"(?i)\s*to\s*class\s*\d+.*$", "", cleaned).strip()
    topic = cleaned or "photosynthesis"
    return topic, grade_level


def main() -> None:
    """Run the required backend pipeline and print each step output."""
    sample_input_text = "Explain photosynthesis to class 6"
    stt_service = SpeechToTextService(use_mock=True)
    intent = classify_intent(stt_service.transcribe(text_input=sample_input_text))
    topic, grade_level = extract_topic_and_grade(sample_input_text)

    gemini_service = GeminiService()
    explanation = gemini_service.generate_explanation(topic=topic, grade_level=grade_level)

    tts_service = TextToSpeechService(output_dir="generated_audio")
    audio_path = tts_service.text_to_audio(explanation)

    print("Input Text:", sample_input_text)
    print("Detected Intent:", intent.intent)
    print("Intent Confidence:", intent.confidence)
    print("Topic:", topic)
    print("Grade Level:", grade_level)
    print("Gemini Explanation Output:", explanation)
    print("Generated Audio File Path:", audio_path)


if __name__ == "__main__":
    main()
