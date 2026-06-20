"""Application entrypoint for Classroom Copilot MVP."""

import os

import gradio as gr
from dotenv import load_dotenv

from services.gemini_service import GeminiService
from services.speech_to_text import SpeechToTextService
from services.text_to_speech import TextToSpeechService
from ui.gradio_ui import CopilotDependencies, build_interface


def create_app():
    """Create Gradio app with all required runtime dependencies."""
    load_dotenv()

    stt_model_size = os.getenv("WHISPER_MODEL_SIZE", "tiny")
    stt_device = os.getenv("WHISPER_DEVICE", "cpu")
    tts_voice = os.getenv("EDGE_TTS_VOICE", "en-IN-NeerjaNeural")

    stt_use_mock = os.getenv("STT_USE_MOCK", "false").lower() == "true"

    deps = CopilotDependencies(
        stt_service=SpeechToTextService(
            model_size=stt_model_size,
            device=stt_device,
            use_mock=stt_use_mock,
        ),
        tts_service=TextToSpeechService(output_dir="generated_audio", voice=tts_voice),
        gemini_service=GeminiService(model_name="gemini-2.5-flash"),
    )
    return build_interface(deps=deps)


if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        theme=gr.themes.Default(primary_hue="blue"),
    )
