"""Gradio UI and orchestration layer for Classroom Copilot."""

import html
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import gradio as gr

from services.diagram_generator import build_mermaid_diagram
from services.gemini_service import GeminiService
from services.intent_classifier import (
    INTENT_ACTIVITY,
    INTENT_CONCEPT,
    INTENT_QUIZ,
    INTENT_TRANSLATION,
    classify_intent,
)
from services.speech_to_text import SpeechToTextService
from services.text_to_speech import TextToSpeechService


UnifiedResponse = Dict[str, Any]

# Force readable colors so Gradio dark theme does not hide text in HTML blocks.
_PANEL_STYLE = "color:#000000;background:#ffffff;padding:16px;border-radius:10px;border:1px solid #cccccc;"
_CARD_STYLE = "color:#000000;background:#ffffff;margin:16px 0;padding:14px;border:1px solid #333333;border-radius:8px;"
_TEXT_STYLE = "color:#000000;"


@dataclass
class CopilotDependencies:
    """Runtime dependency container for UI orchestration."""

    stt_service: SpeechToTextService
    tts_service: TextToSpeechService
    gemini_service: GeminiService


def _base_response(intent: str) -> UnifiedResponse:
    """Create a unified response contract with all fields."""
    return {
        "intent": intent,
        "text": "",
        "speech": "",
        "diagram": None,
        "quiz": None,
        "translation": None,
        "activity": None,
    }


def _extract_topic(text: str) -> str:
    """Extract educational topic from teacher command."""
    lowered = text.lower().strip()
    inline_patterns = [
        r"(?:quiz on|quiz about|mcq on)\s+(.+)",
        r"explain\s+(.+?)(?:\s+to\s+class|\s+for\s+class|$)",
        r"activity(?:\s+on|\s+about|\s+for)?\s+(.+)",
        r"discussion(?:\s+on|\s+about)?\s+(.+)",
    ]
    for pattern in inline_patterns:
        match = re.search(pattern, lowered)
        if match:
            topic = match.group(1).strip(" .")
            topic = re.sub(r"\s+\d+\s*(minute|min).*$", "", topic).strip()
            if topic:
                return topic

    prefixes = ("explain ", "create a quiz on ", "create quiz on ", "quiz on ")
    for prefix in prefixes:
        if lowered.startswith(prefix):
            return text[len(prefix) :].strip(" .") or "general topic"
    return "general topic"


def _extract_grade(command_text: str) -> str:
    """Extract class grade level from text."""
    match = re.search(r"class\s*(\d+)", command_text.lower())
    return match.group(1) if match else "6"


def _extract_duration_minutes(command_text: str) -> int:
    """Extract activity duration in minutes."""
    match = re.search(r"(\d+)\s*(minute|min)", command_text.lower())
    if not match:
        return 3
    value = int(match.group(1))
    return value if value in {2, 3, 5, 10} else 3


def _extract_translation_direction(command_text: str) -> str:
    """Infer translation direction from command text."""
    lowered = command_text.lower()
    if "hindi to english" in lowered or "hi to en" in lowered:
        return "hi_to_en"
    return "en_to_hi"


def _extract_translation_text(command_text: str) -> str:
    """Extract text that needs translation."""
    lowered = command_text.lower()
    markers = ["translate this paragraph", "translate this", "translate"]
    for marker in markers:
        if marker in lowered:
            idx = lowered.find(marker) + len(marker)
            extracted = command_text[idx:].strip(" :.-")
            if extracted:
                return extracted
    return command_text


def route_and_generate(text: str, gemini_service: GeminiService) -> UnifiedResponse:
    """Route command by intent and produce unified response contract."""
    intent = classify_intent(text).intent
    response = _base_response(intent=intent)

    if intent == INTENT_CONCEPT:
        topic = _extract_topic(text)
        grade = _extract_grade(text)
        explanation = gemini_service.generate_explanation(topic=topic, grade_level=grade)
        response["text"] = explanation
        response["diagram"] = build_mermaid_diagram(topic=topic)
        return response

    if intent == INTENT_QUIZ:
        topic = _extract_topic(text)
        response["quiz"] = gemini_service.generate_quiz(topic=topic)
        response["text"] = f"Quiz generated for {topic}."
        return response

    if intent == INTENT_TRANSLATION:
        source = _extract_translation_text(text)
        direction = _extract_translation_direction(text)
        translation = gemini_service.generate_translation(text=source, direction=direction)
        response["translation"] = {
            "direction": direction,
            "input": translation.get("input", source),
            "output": translation.get("output", ""),
        }
        response["text"] = "Translation ready."
        return response

    duration_minutes = _extract_duration_minutes(text)
    topic = _extract_topic(text)
    activity = gemini_service.generate_activity(duration_minutes=duration_minutes, topic=topic)
    response["activity"] = activity
    response["text"] = activity.get("instructions", "Activity ready.")
    return response


def _sanitize_for_tts(text: str) -> str:
    """Strip markdown/symbols that Edge TTS misreads as 'asterisk' etc."""
    cleaned = text
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    cleaned = re.sub(r"^[\s\-*#]+", "", cleaned, flags=re.MULTILINE)
    cleaned = cleaned.replace("*", " ")
    cleaned = cleaned.replace("#", " ")
    cleaned = cleaned.replace("_", " ")
    cleaned = cleaned.replace("|", " ")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned[:1200]


def build_speech_text(response: UnifiedResponse) -> str:
    """Create clean TTS text from unified response."""
    intent = response["intent"]
    if intent == INTENT_CONCEPT:
        return _sanitize_for_tts(str(response["text"]))

    if intent == INTENT_QUIZ:
        quiz_items: List[Dict[str, Any]] = _normalize_quiz_data(response.get("quiz"))
        chunks: List[str] = []
        for idx, item in enumerate(quiz_items[:3], start=1):
            options = _normalize_options(item.get("options", []))
            option_lines = [f"Option {chr(ord('A') + i)} {opt}" for i, opt in enumerate(options[:4])]
            chunks.append(f"Question {idx}. {item.get('question', '')}. " + ". ".join(option_lines))
        return _sanitize_for_tts(" ".join(chunks) if chunks else "Quiz is ready. Please check the screen.")

    if intent == INTENT_TRANSLATION:
        translation = response.get("translation") or {}
        return _sanitize_for_tts(str(translation.get("output", "Translation is ready.")))

    if intent == INTENT_ACTIVITY:
        activity = response.get("activity") or {}
        steps = activity.get("steps", [])
        steps_summary = ". ".join(str(step) for step in steps[:3])
        combined = f"{activity.get('instructions', 'Activity is ready.')}. {steps_summary}"
        return _sanitize_for_tts(combined)

    return _sanitize_for_tts(str(response.get("text", "Response is ready.")))


def _normalize_quiz_data(quiz: Any) -> List[Dict[str, Any]]:
    """Normalize quiz payload from Gemini into a consistent list format."""
    if quiz is None:
        return []
    if isinstance(quiz, dict) and "questions" in quiz:
        quiz = quiz["questions"]
    if not isinstance(quiz, list):
        return []

    normalized: List[Dict[str, Any]] = []
    for item in quiz:
        if not isinstance(item, dict):
            continue
        question = (
            item.get("question")
            or item.get("Question")
            or item.get("q")
            or ""
        )
        options = item.get("options") or item.get("Options") or item.get("choices") or []
        correct = (
            item.get("correct_answer")
            or item.get("correctAnswer")
            or item.get("answer")
            or ""
        )
        normalized.append(
            {
                "question": str(question),
                "options": options,
                "correct_answer": str(correct),
            }
        )
    return normalized


def _normalize_options(options: Any) -> List[str]:
    """Normalize quiz options from list or dict format."""
    if isinstance(options, dict):
        return [str(options.get(key, "")) for key in ("A", "B", "C", "D")]
    if isinstance(options, list):
        return [str(opt) for opt in options]
    return []


def _format_explanation_html(text: str) -> str:
    """Render explanation as readable HTML."""
    if not text.strip():
        return f"<div style='{_PANEL_STYLE}'><p>No explanation yet.</p></div>"
    paragraphs = [p.strip() for p in re.split(r"\.\s+", text) if p.strip()]
    items = "".join(
        f"<li style='margin:8px 0;font-size:18px;{_TEXT_STYLE}'>{html.escape(p)}.</li>"
        for p in paragraphs
    )
    return (
        f"<div style='{_PANEL_STYLE}font-size:18px;line-height:1.6;'>"
        f"<h3 style='{_TEXT_STYLE}'>Explanation</h3><ul>{items}</ul></div>"
    )


def _format_quiz_html(quiz: Any, show_answers: bool) -> str:
    """Render quiz as HTML for reliable display."""
    quiz_items = _normalize_quiz_data(quiz)
    if not quiz_items:
        return (
            f"<div style='{_PANEL_STYLE}'>"
            "<p>Click <b>Generate Quiz</b> to create questions.</p></div>"
        )

    blocks: List[str] = [
        f"<div style='{_PANEL_STYLE}font-size:17px;line-height:1.5;'>"
        f"<h3 style='{_TEXT_STYLE}'>Quiz ({len(quiz_items)} MCQs)</h3>"
    ]
    for idx, item in enumerate(quiz_items, start=1):
        question = html.escape(str(item.get("question", "")))
        blocks.append(f"<div style='{_CARD_STYLE}'>")
        blocks.append(
            f"<p style='{_TEXT_STYLE}margin-bottom:8px;'><b>Q{idx}.</b> {question}</p>"
            "<ul style='list-style:none;padding-left:0;margin:0;'>"
        )
        for opt_idx, option in enumerate(_normalize_options(item.get("options", []))):
            label = chr(ord("A") + opt_idx)
            blocks.append(
                f"<li style='margin:6px 0;{_TEXT_STYLE}'><b>{label}.</b> {html.escape(option)}</li>"
            )
        if show_answers:
            answer = html.escape(str(item.get("correct_answer", "")))
            blocks.append(
                f"<li style='margin-top:8px;color:#006644;'><b>Correct Answer:</b> {answer}</li>"
            )
        blocks.append("</ul></div>")
    blocks.append("</div>")
    return "".join(blocks)


def _format_activity_html(activity: Optional[Dict[str, Any]]) -> str:
    """Render activity guide as HTML."""
    if not activity:
        return f"<div style='{_PANEL_STYLE}'><p>Activity details will appear here after generation.</p></div>"
    steps = activity.get("steps", [])
    step_items = "".join(
        f"<li style='margin:8px 0;font-size:17px;{_TEXT_STYLE}'>{html.escape(str(step))}</li>"
        for step in steps
    )
    duration_min = int(activity.get("duration_seconds", 180) / 60)
    title = html.escape(str(activity.get("title", "Classroom Activity")))
    instructions = html.escape(str(activity.get("instructions", "")))
    return (
        f"<div style='{_PANEL_STYLE}font-size:17px;line-height:1.6;'>"
        f"<h3 style='{_TEXT_STYLE}'>{title}</h3>"
        f"<p style='{_TEXT_STYLE}'><b>Duration:</b> {duration_min} minutes</p>"
        f"<p style='{_TEXT_STYLE}'><b>Instructions:</b> {instructions}</p>"
        f"<p style='{_TEXT_STYLE}'><b>Steps:</b></p><ol>{step_items}</ol></div>"
    )


def _format_translation_blocks(translation: Optional[Dict[str, str]]) -> Tuple[str, str]:
    """Return side-by-side translation text values."""
    if not translation:
        return "", ""
    direction = translation.get("direction", "en_to_hi")
    source = translation.get("input", "")
    output = translation.get("output", "")
    if direction == "hi_to_en":
        return output, source
    return source, output


def _format_diagram_html(diagram: Optional[str]) -> str:
    """Render diagram as black text on white boxes (readable on smart boards)."""
    if not diagram:
        return f"<div style='{_PANEL_STYLE}'><p style='{_TEXT_STYLE}'>No diagram for this response.</p></div>"

    labels = re.findall(r'\["([^"]+)"\]', diagram)
    if not labels:
        labels = re.findall(r"\[([^\]]+)\]", diagram)
    if not labels:
        return f"<div style='{_PANEL_STYLE}'><p style='{_TEXT_STYLE}'>Diagram unavailable.</p></div>"

    seen: List[str] = []
    for label in labels:
        if label not in seen:
            seen.append(label)

    box_style = (
        "background:#ffffff;color:#000000;border:2px solid #333;"
        "padding:14px 20px;margin:8px auto;border-radius:8px;"
        "font-size:18px;font-weight:600;text-align:center;max-width:420px;"
    )
    arrow = "<div style='text-align:center;font-size:24px;color:#000000;margin:4px 0;'>&darr;</div>"
    boxes = [f"<div style='{box_style}'>{html.escape(label)}</div>" for label in seen]
    body = arrow.join(boxes)
    return f"<div style='{_PANEL_STYLE}'>{body}</div>"


def _resolve_input_text(audio_input: Optional[str], text_input: str, stt: SpeechToTextService) -> str:
    """Prefer fresh microphone audio over typed text when both exist."""
    if audio_input:
        return stt.transcribe(audio_file_path=audio_input)
    if text_input.strip():
        return stt.transcribe(text_input=text_input)
    raise ValueError("Please record a voice command or type your request, then click Generate.")


def build_interface(deps: CopilotDependencies) -> gr.Blocks:
    """Build single-page classroom UI with unified orchestration."""
    last_quiz: Dict[str, Any] = {"data": None}

    def process_input(
        audio_input: Optional[str],
        text_input: str,
        show_answers: bool,
    ) -> Tuple[str, str, str, str, str, str, str, Optional[str], str]:
        """Run full pipeline and return per-block UI outputs."""
        stored_quiz = last_quiz["data"]
        try:
            if not audio_input and not text_input.strip():
                return "", "", "", _format_quiz_html(stored_quiz, show_answers), "", "", "", None, "Waiting for input"

            recognized_text = _resolve_input_text(audio_input, text_input, deps.stt_service)
            response = route_and_generate(text=recognized_text, gemini_service=deps.gemini_service)
            response["speech"] = build_speech_text(response)

            audio_path: Optional[str] = None
            try:
                audio_path = deps.tts_service.text_to_audio(response["speech"])
            except Exception:  # pylint: disable=broad-except
                audio_path = None

            explanation_html = _format_explanation_html(response["text"]) if response["intent"] == INTENT_CONCEPT else ""
            diagram_html = _format_diagram_html(response["diagram"]) if response["intent"] == INTENT_CONCEPT else ""

            quiz_data = _normalize_quiz_data(response["quiz"]) if response["intent"] == INTENT_QUIZ else stored_quiz
            if response["intent"] == INTENT_QUIZ:
                last_quiz["data"] = quiz_data
            quiz_html = _format_quiz_html(quiz_data, show_answers) if quiz_data else _format_quiz_html(None, False)

            english_text, hindi_text = _format_translation_blocks(response["translation"])
            if response["intent"] != INTENT_TRANSLATION:
                english_text, hindi_text = "", ""

            activity_html = _format_activity_html(response["activity"]) if response["intent"] == INTENT_ACTIVITY else ""
            status = f"Intent detected: {response['intent']}"

            return (
                recognized_text,
                explanation_html,
                diagram_html,
                quiz_html,
                english_text,
                hindi_text,
                activity_html,
                audio_path,
                status,
            )
        except Exception as exc:  # pylint: disable=broad-except
            message = f"<div style='{_PANEL_STYLE}'><p style='color:#b00000;'>Unable to process request. {html.escape(str(exc))}</p></div>"
            return "", message, "", _format_quiz_html(stored_quiz, show_answers), "", "", "", None, "Error"

    def generate_quiz_on_demand(topic_input: str, command_text: str, show_answers: bool) -> Tuple[str, str, Optional[str]]:
        """Generate quiz and answers on demand from topic field or last command."""
        try:
            topic = topic_input.strip() or _extract_topic(command_text.strip()) or "general topic"
            quiz = _normalize_quiz_data(deps.gemini_service.generate_quiz(topic=topic))
            if not quiz:
                raise ValueError("Quiz generation returned no questions.")
            last_quiz["data"] = quiz
            quiz_html = _format_quiz_html(quiz, show_answers)
            speech = build_speech_text({"intent": INTENT_QUIZ, "text": "", "quiz": quiz})
            audio_path = deps.tts_service.text_to_audio(speech)
            return quiz_html, f"Quiz generated for: {topic}", audio_path
        except Exception as exc:  # pylint: disable=broad-except
            error_html = f"<div style='{_PANEL_STYLE}'><p style='color:#b00000;'>Quiz generation failed: {html.escape(str(exc))}</p></div>"
            return error_html, "Quiz error", None

    def toggle_quiz_answers(show_answers: bool) -> str:
        """Re-render quiz with or without answer key."""
        return _format_quiz_html(last_quiz["data"], show_answers)

    with gr.Blocks(title="Classroom Copilot") as demo:
        gr.Markdown("# Classroom Copilot")
        gr.Markdown(
            "**How to use:** Click the microphone, speak your command, click **Stop**, "
            "then click **Generate Classroom Response**. You can also type instead."
        )

        status_output = gr.Textbox(label="Status", interactive=False, lines=1)

        with gr.Row():
            with gr.Column(scale=1):
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="Voice Input (click mic, speak, then stop)",
                    interactive=True,
                )
                text_input = gr.Textbox(
                    label="Text Input (alternative to voice)",
                    placeholder="Explain photosynthesis to class 6",
                    lines=3,
                )
                submit_button = gr.Button("Generate Classroom Response", variant="primary", size="lg")

            with gr.Column(scale=2):
                recognized_text = gr.Textbox(label="Recognized Speech Text", lines=2)
                audio_output = gr.Audio(label="Audio Feedback", type="filepath", autoplay=True)

        gr.Markdown("## Explanation")
        explanation_output = gr.HTML(value="")

        gr.Markdown("## Diagram")
        diagram_output = gr.HTML(value="")

        gr.Markdown("## Quiz")
        with gr.Row():
            quiz_topic_input = gr.Textbox(label="Quiz Topic", placeholder="photosynthesis", scale=3)
            generate_quiz_btn = gr.Button("Generate Quiz", variant="secondary", scale=1)
            show_answers = gr.Checkbox(label="Show Answers", value=False)
        quiz_output = gr.HTML(value=_format_quiz_html(None, False))

        gr.Markdown("## Translation (English | Hindi)")
        with gr.Row():
            english_output = gr.Textbox(label="English", lines=6)
            hindi_output = gr.Textbox(label="Hindi", lines=6)

        gr.Markdown("## Activity Guide")
        activity_output = gr.HTML(value="")

        submit_button.click(
            fn=process_input,
            inputs=[audio_input, text_input, show_answers],
            outputs=[
                recognized_text,
                explanation_output,
                diagram_output,
                quiz_output,
                english_output,
                hindi_output,
                activity_output,
                audio_output,
                status_output,
            ],
        )

        if hasattr(audio_input, "stop_recording"):
            audio_input.stop_recording(
                fn=process_input,
                inputs=[audio_input, text_input, show_answers],
                outputs=[
                    recognized_text,
                    explanation_output,
                    diagram_output,
                    quiz_output,
                    english_output,
                    hindi_output,
                    activity_output,
                    audio_output,
                    status_output,
                ],
            )

        generate_quiz_btn.click(
            fn=generate_quiz_on_demand,
            inputs=[quiz_topic_input, text_input, show_answers],
            outputs=[quiz_output, status_output, audio_output],
        )

        show_answers.change(
            fn=toggle_quiz_answers,
            inputs=[show_answers],
            outputs=[quiz_output],
        )

    return demo
