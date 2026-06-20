"""Text-to-speech service using Edge TTS."""

import asyncio
import hashlib
from pathlib import Path

try:
    import edge_tts
except Exception:  # pylint: disable=broad-except
    edge_tts = None  # type: ignore[assignment]


class TextToSpeechService:
    """Generate audio output files from text."""

    def __init__(self, output_dir: str = "generated_audio", voice: str = "en-IN-NeerjaNeural") -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.voice = voice

    async def _synthesize(self, text: str, output_path: Path) -> str:
        if edge_tts is None:
            output_path.write_bytes(b"")
            return str(output_path)
        communicate = edge_tts.Communicate(text=text, voice=self.voice)
        await communicate.save(str(output_path))
        return str(output_path)

    def text_to_audio(self, text: str) -> str:
        """Convert text into an MP3 file and return local path."""
        if not text.strip():
            raise ValueError("Cannot synthesize empty text.")

        digest = hashlib.sha1(text.encode("utf-8")).hexdigest()[:12]
        output_path = self.output_dir / f"tts_{digest}.mp3"
        try:
            return asyncio.run(self._synthesize(text=text, output_path=output_path))
        except RuntimeError:
            local_loop = asyncio.new_event_loop()
            try:
                return local_loop.run_until_complete(self._synthesize(text=text, output_path=output_path))
            finally:
                local_loop.close()
        except Exception as exc:  # pylint: disable=broad-except
            raise RuntimeError(f"Text-to-speech generation failed: {exc}") from exc
