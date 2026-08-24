"""
Speech-to-Text (STT) Voice Input Engine for PETROVA.
Captures user microphone audio via PipeWire/PulseAudio with volume normalization and multi-engine transcription.
"""

import os
import shutil
import tempfile
import subprocess
from typing import Optional
from rich.panel import Panel
from petrova.ui.console import console


def record_audio_clip(duration: int = 5) -> Optional[str]:
    """
    Record microphone audio from default Pulse/PipeWire stream with 16kHz mono and volume boost.
    """
    temp_wav = tempfile.mktemp(suffix=".wav")

    # 1. Primary: ffmpeg with pulse input and audio boost
    if shutil.which("ffmpeg"):
        cmd = [
            "ffmpeg", "-y",
            "-f", "pulse",
            "-i", "default",
            "-t", str(duration),
            "-ac", "1",
            "-ar", "16000",
            "-af", "volume=2.5",
            temp_wav
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=duration + 3)
            if res.returncode == 0 and os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 1500:
                return temp_wav
        except Exception:
            pass

    # 2. Fallback: arecord with pulse device
    if shutil.which("arecord"):
        cmd = [
            "arecord",
            "-D", "pulse",
            "-d", str(duration),
            "-f", "S16_LE",
            "-r", "16000",
            "-c", "1",
            "-t", "wav",
            "-q",
            temp_wav
        ]
        try:
            res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=duration + 3)
            if res.returncode == 0 and os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 1500:
                return temp_wav
        except Exception:
            pass

    # 3. Fallback: pw-record (PipeWire native)
    if shutil.which("pw-record"):
        cmd = ["pw-record", "--rate", "16000", "--channels", "1", temp_wav]
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import time
            time.sleep(duration)
            proc.terminate()
            proc.wait(timeout=2)
            if os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 1500:
                return temp_wav
        except Exception:
            pass

    return None


def listen_and_transcribe(duration: int = 5) -> Optional[str]:
    """
    Listen to user voice via microphone and transcribe to text.
    """
    wav_path = record_audio_clip(duration)
    if not wav_path:
        return None

    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        recognizer.energy_threshold = 150
        recognizer.dynamic_energy_threshold = False

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        text = recognizer.recognize_google(audio_data)
        if text and text.strip():
            return text.strip()

    except Exception:
        pass
    finally:
        try:
            if os.path.exists(wav_path):
                os.unlink(wav_path)
        except Exception:
            pass

    return None
