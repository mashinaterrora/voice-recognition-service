import os
import subprocess
import tempfile
from typing import Optional

from faster_whisper import WhisperModel

from app.infrastructure.asr.base import BaseASRProvider


class FasterWhisperASRProvider(BaseASRProvider):
    def __init__(self, model_name_or_path: str = "base", compute_type: str = "int8") -> None:
        self._model = WhisperModel(model_name_or_path, device="auto", compute_type=compute_type)

    async def transcribe_from_url(self, url: str, language: Optional[str] = None) -> str:
        raise NotImplementedError("Use transcribe_from_bytes for downloaded audio data")

    async def transcribe_from_bytes(self, data: bytes, language: Optional[str] = None) -> str:
        with tempfile.TemporaryDirectory() as td:
            input_path = os.path.join(td, "input.ogg")
            wav_path = os.path.join(td, "converted.wav")
            with open(input_path, "wb") as f:
                f.write(data)

            command = [
                "ffmpeg",
                "-y",
                "-i",
                input_path,
                "-ac",
                "1",
                "-ar",
                "16000",
                wav_path,
            ]
            subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            segments, _info = self._model.transcribe(
                wav_path,
                task="transcribe",
                vad_filter=True,
                language=language,
            )
            parts = []
            for seg in segments:
                if seg and getattr(seg, "text", None):
                    parts.append(seg.text.strip())
            return " ".join(t for t in parts if t).strip()






