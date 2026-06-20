"""Prompt builder for classroom activity guidance."""


def build_activity_prompt(activity_request: str, duration_minutes: int) -> str:
    """Build prompt for hands-free classroom activity generation."""
    return f"""
Generate a classroom activity guide based on this teacher request:
"{activity_request}"

Duration required: {duration_minutes} minutes.

Rules:
- Output short activity title.
- Provide step-by-step instructions (3-6 steps).
- Keep instructions practical for classroom use.
- Use friendly Hinglish.

Return strict JSON:
{{
  "activity_title": "string",
  "duration_minutes": {duration_minutes},
  "instructions": ["step 1", "step 2", "step 3"]
}}
""".strip()
