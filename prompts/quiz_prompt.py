"""Prompt builder for quiz generation."""


def build_quiz_prompt(topic: str, grade_level: str = "6") -> str:
    """Build prompt for generating student-friendly MCQ quiz."""
    return f"""
Create a classroom quiz for topic "{topic}" for Class {grade_level} students.

Rules:
- Generate exactly 5 MCQs.
- Each MCQ must have exactly 4 options: A, B, C, D.
- Keep questions easy and student-friendly.
- Keep language clear and classroom appropriate.

Return strict JSON with this schema:
{{
  "quiz_title": "string",
  "questions": [
    {{
      "question": "string",
      "options": {{"A": "string", "B": "string", "C": "string", "D": "string"}},
      "correct_answer": "A|B|C|D"
    }}
  ]
}}
""".strip()
