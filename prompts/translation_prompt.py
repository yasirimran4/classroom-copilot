"""Prompt builder for bilingual translation."""


def build_translation_prompt(text: str, target_language: str) -> str:
    """Build prompt for educational bilingual translation."""
    normalized_target = target_language.lower().strip()
    return f"""
Translate the following educational text to {normalized_target}.

Rules:
- Preserve educational meaning and context.
- Avoid literal word-by-word translation when unnatural.
- Keep sentence clarity for school students.

Source text:
\"\"\"{text}\"\"\"

Return strict JSON:
{{
  "source_text": "string",
  "translated_text": "string",
  "target_language": "{normalized_target}"
}}
""".strip()
