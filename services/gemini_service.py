"""Gemini service wrapper for classroom feature generation."""

import json
import os
from typing import Any, Dict, List, Optional

try:
    import google.generativeai as genai
except Exception:  # pylint: disable=broad-except
    genai = None  # type: ignore[assignment]


class GeminiService:
    """Generate classroom content with Gemini and safe fallbacks."""

    def __init__(self, model_name: str = "gemini-2.5-flash") -> None:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self._use_mock = (not bool(api_key)) or genai is None
        self._model: Optional[object] = None

        if self._use_mock:
            return

        try:
            genai.configure(api_key=api_key)
            self._model = genai.GenerativeModel(model_name=model_name)
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError(f"Failed to initialize Gemini service: {exc}") from exc

    def _generate_text(self, prompt: str) -> str:
        """Generate text response from Gemini model."""
        if self._use_mock:
            raise RuntimeError("Gemini unavailable, using fallback.")
        if self._model is None:
            raise RuntimeError("Gemini model is not initialized.")
        try:
            response = self._model.generate_content(prompt)
            text = (response.text or "").strip()
            if not text:
                raise ValueError("Empty response from Gemini.")
            return text
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError(f"Gemini generation failed: {exc}") from exc

    def _extract_json_block(self, text: str) -> Any:
        """Extract and parse JSON block from model output."""
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])

        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(text[start : end + 1])

        raise ValueError("No JSON block found in Gemini output.")

    def generate_explanation(self, topic: str, grade_level: str) -> str:
        """Generate a simple Hinglish explanation for a topic and class level."""
        prompt = (
            f"Explain {topic} for Class {grade_level} students in simple Hinglish. "
            "Keep it concise, engaging, and avoid complex terminology."
        )
        try:
            return self._generate_text(prompt=prompt)
        except Exception as exc:  # pylint: disable=broad-except
            return (
                f"{topic.title()} ko simple Hinglish mein samjho: "
                "yeh ek basic concept hai jo class mein examples ke through aasani se samjha ja sakta hai. "
                "Step by step samjho, short recap lo, aur students se 1-2 questions poochho."
            )

    def generate_quiz(self, topic: str) -> List[Dict[str, Any]]:
        """Generate 5 easy classroom MCQs for a topic."""
        prompt = (
            f"Create exactly 5 easy MCQs for topic '{topic}' in Hinglish friendly classroom language. "
            "Return JSON array only with schema: "
            '[{"question":"...","options":["A","B","C","D"],"correct_answer":"A"}]'
        )
        try:
            text = self._generate_text(prompt=prompt)
            data = self._extract_json_block(text)
            if not isinstance(data, list) or len(data) != 5:
                raise ValueError("Quiz response must be a list of 5 items.")
            return data
        except Exception:
            return [
                {
                    "question": f"{topic.title()} mein plant ka role kya hai?",
                    "options": ["Food banana", "Run karna", "Mobile use karna", "Sona"],
                    "correct_answer": "A",
                },
                {
                    "question": f"{topic.title()} ke liye sunlight ka kya kaam hai?",
                    "options": ["Energy dena", "Sound banana", "Homework check karna", "Sports karna"],
                    "correct_answer": "A",
                },
                {
                    "question": f"{topic.title()} topic class mein kaise samjhen?",
                    "options": ["Simple examples se", "Sirf rote learning se", "Without teacher", "Only test se"],
                    "correct_answer": "A",
                },
                {
                    "question": f"{topic.title()} padhte waqt best approach kya hai?",
                    "options": ["Step by step", "Skip basics", "Ignore doubts", "No revision"],
                    "correct_answer": "A",
                },
                {
                    "question": f"{topic.title()} ka recap kab useful hota hai?",
                    "options": ["Lesson ke end me", "Kabhi nahi", "Sirf exam day", "Only weekend"],
                    "correct_answer": "A",
                },
            ]

    def generate_translation(self, text: str, direction: str) -> Dict[str, str]:
        """Translate text preserving meaning for classroom use."""
        prompt = (
            f"Translate this text with preserved meaning (not word-by-word): {text}\n"
            f"Direction: {direction}. Return JSON only: "
            '{"input":"...","output":"..."}'
        )
        try:
            generated_text = self._generate_text(prompt=prompt)
            data = self._extract_json_block(generated_text)
            if not isinstance(data, dict) or "output" not in data:
                raise ValueError("Invalid translation JSON format.")
            return {"input": str(data.get("input", text)), "output": str(data["output"])}
        except Exception:
            if direction == "hi_to_en":
                return {"input": text, "output": "This is a simple educational translation in English."}
            return {"input": text, "output": "Yeh ek simple shiksha sambandhit anuvaad hai."}

    def generate_activity(self, duration_minutes: int, topic: Optional[str] = None) -> Dict[str, Any]:
        """Generate structured classroom activity guide."""
        topic_text = topic or "current lesson"
        prompt = (
            f"Create a classroom activity for {duration_minutes} minutes on '{topic_text}'. "
            "Return JSON only with keys: title, instructions, steps, duration_seconds. "
            "steps must be an array of short strings."
        )
        try:
            text = self._generate_text(prompt=prompt)
            data = self._extract_json_block(text)
            if not isinstance(data, dict):
                raise ValueError("Activity output must be JSON object.")
            if "steps" not in data or not isinstance(data["steps"], list):
                raise ValueError("Activity steps missing or invalid.")
            data["duration_seconds"] = int(data.get("duration_seconds", duration_minutes * 60))
            return data
        except Exception:
            return {
                "title": "Quick Group Discussion",
                "instructions": "Class ko chhote groups me baantkar topic par charcha karvao.",
                "steps": [
                    "Students ko 3-4 ke groups me divide karo.",
                    "Har group ko topic ka ek sawal do.",
                    "2 minute discussion karao.",
                    "Har group se 1 point class ke saamne share karvao.",
                ],
                "duration_seconds": duration_minutes * 60,
            }
