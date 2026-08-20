"""
PETROVA Voice Interaction Package (TTS & STT).
"""
from petrova.voice.tts import speak, is_voice_enabled, set_voice_enabled, stop_speaking
from petrova.voice.stt import listen_and_transcribe

__all__ = [
    "speak",
    "listen_and_transcribe",
    "is_voice_enabled",
    "set_voice_enabled",
    "stop_speaking",
]
