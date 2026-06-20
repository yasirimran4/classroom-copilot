"""Speech-to-text service with optional Whisper and mock-safe path."""

from pathlib import Path
from typing import Optional

try:
    from faster_whisper import WhisperModel
except Exception:  # pylint: disable=broad-except
    WhisperModel = None  # type: ignore[assignment]


class SpeechToTextService:
    """Convert audio to text, or safely accept direct text input."""

    def __init__(self, model_size: str = "tiny", device: str = "cpu", use_mock: bool = True) -> None:
        self.model_size = model_size
        self.device = device
        self.use_mock = use_mock
        self._model: Optional[WhisperModel] = None

    def _get_model(self) -> Optional[WhisperModel]:
        if self.use_mock or WhisperModel is None:
            return None
        try:
            if self._model is None:
                self._model = WhisperModel(self.model_size, device=self.device, compute_type="int8")
            return self._model
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError(f"Failed to initialize Faster Whisper model: {exc}") from exc

    def transcribe(self, audio_file_path: Optional[str] = None, text_input: Optional[str] = None) -> str:
        """Return transcribed text from audio, or direct text in mock mode."""
        if text_input and text_input.strip():
            return text_input.strip()

        if not audio_file_path:
            raise ValueError("Provide either text_input or audio_file_path.")

        path = Path(audio_file_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio input not found: {audio_file_path}")

        try:
            model = self._get_model()
            if model is None:
                return "Explain photosynthesis to class 6"
            segments, _ = model.transcribe(str(path), beam_size=3)
            text = " ".join(segment.text.strip() for segment in segments).strip()
            if not text:
                raise ValueError("Could not detect speech in audio.")
            return text
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError(f"Speech transcription failed: {exc}") from exc
