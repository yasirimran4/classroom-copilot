"""Prompt builder for concept simplification."""

from typing import Optional


def build_concept_prompt(topic: str, grade_level: Optional[str] = "6") -> str:
    """Build a structured prompt for classroom concept explanation."""
    return f"""
You are a helpful classroom teaching assistant for government school students.

Task:
- Explain the topic "{topic}" for Class {grade_level} students.
- Use simple Hinglish (Hindi + English mixed naturally).
- Keep language age-appropriate and engaging.
- Avoid hard technical words, or explain them in simple words.
- Keep explanation concise (120-180 words).

Output format:
1) Explanation text only.
2) End with 2 short recap bullet points.
""".strip()
