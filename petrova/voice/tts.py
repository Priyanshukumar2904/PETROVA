"""
Text-to-Speech (TTS) Voice Engine for PETROVA.
High-fidelity neural voice synthesis with multiple personality profiles,
speed controls, and offline fallbacks.
"""

import asyncio
import os
import re
import shutil
import tempfile
import threading
import subprocess
from typing import Optional

from petrova.config.settings import get_config
from petrova.ui.console import console

_current_player: Optional[subprocess.Popen] = None

# High-fidelity Voice Profiles Catalog
VOICE_PROFILES = {
    "nova": {
        "name": "Nova",
        "voice_id": "en-US-AriaNeural",
        "desc": "Smooth, articulate, intelligent AI assistant (Female)",
    },
    "echo": {
        "name": "Echo",
        "voice_id": "en-US-GuyNeural",
        "desc": "Warm, authoritative, deep and calm baritone (Male)",
    },
    "jenny": {
        "name": "Jenny",
        "voice_id": "en-US-JennyNeural",
        "desc": "Energetic, clear, melodic assistant tone (Female)",
    },
    "onyx": {
        "name": "Onyx",
        "voice_id": "en-US-ChristopherNeural",
        "desc": "Crisp, technical, confident developer persona (Male)",
    },
    "sonia": {
        "name": "Sonia",
        "voice_id": "en-GB-SoniaNeural",
        "desc": "Sophisticated, natural British English (Female)",
    },
    "ryan": {
        "name": "Ryan",
        "voice_id": "en-GB-RyanNeural",
        "desc": "Natural, calm British English baritone (Male)",
    },
    "nat": {
        "name": "Nat",
        "voice_id": "en-AU-NatNeural",
        "desc": "Friendly Australian English (Female)",
    },
}

DEFAULT_VOICE = "nova"


def clean_text_for_speech(text: str) -> str:
    """Strip markdown code blocks, links, and formatting to speak cleanly."""
    # Remove code blocks ```...```
    cleaned = re.sub(r"```.*?```", " (command proposed in terminal) ", text, flags=re.DOTALL)
    # Remove inline code `...`
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    # Remove URLs
    cleaned = re.sub(r"https?://\S+", " (link) ", cleaned)
    # Remove markdown headers and emphasis
    cleaned = re.sub(r"[#*_~>]+", "", cleaned)
    # Remove Rich markup tags [bold green]...[/bold green]
    cleaned = re.sub(r"\[/?(bold|dim|green|cyan|yellow|red|magenta|blue|italic)[^\]]*\]", "", cleaned)
    # Remove multiple spaces / newlines
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def is_voice_enabled() -> bool:
    """Check if voice output is active in user config."""
    config = get_config()
    return bool(config.get("voice_enabled", False))


def set_voice_enabled(enabled: bool):
    """Toggle voice output setting."""
    config = get_config()
    config.set("voice_enabled", enabled)


def get_current_voice() -> str:
    """Get active voice profile key."""
    config = get_config()
    voice = config.get("voice_profile", DEFAULT_VOICE).lower()
    return voice if voice in VOICE_PROFILES else DEFAULT_VOICE


def set_current_voice(voice_name: str) -> bool:
    """Set active voice profile."""
    voice_key = voice_name.lower().strip()
    if voice_key in VOICE_PROFILES:
        config = get_config()
        config.set("voice_profile", voice_key)
        return True
    return False


def get_voice_speed() -> str:
    """Get speech rate adjustment (e.g. '+0%', '+10%', '-10%')."""
    config = get_config()
    return config.get("voice_speed", "+0%")


def set_voice_speed(speed: str):
    """Set speech rate adjustment."""
    config = get_config()
    config.set("voice_speed", speed)


def stop_speaking():
    """Immediately stop active audio playback."""
    global _current_player
    if _current_player and _current_player.poll() is None:
        try:
            _current_player.kill()
        except Exception:
            pass
        _current_player = None


def _play_audio_file(audio_path: str):
    """Play audio file using available Linux audio players."""
    global _current_player
    stop_speaking()

    players = [
        ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", audio_path],
        ["mpv", "--no-video", "--really-quiet", audio_path],
        ["pw-play", audio_path],
        ["paplay", audio_path],
        ["aplay", "-q", audio_path],
    ]

    for cmd in players:
        if shutil.which(cmd[0]):
            try:
                _current_player = subprocess.Popen(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                _current_player.wait()
                break
            except Exception:
                continue

    # Cleanup temp audio file
    try:
        if os.path.exists(audio_path):
            os.unlink(audio_path)
    except Exception:
        pass


async def _synthesize_edge_tts(text: str, voice_id: str, rate: str, output_path: str):
    """Synthesize high-fidelity neural audio using edge-tts."""
    import edge_tts
    communicate = edge_tts.Communicate(text, voice_id, rate=rate)
    await communicate.save(output_path)


def speak(text: str, blocking: bool = False):
    """
    Synthesize and speak text with neural audio and multi-tier fallbacks.
    If blocking=False, plays asynchronously in a background thread.
    """
    clean = clean_text_for_speech(text)
    if not clean:
        return

    # Cap speech length to avoid infinite speech
    clean = clean[:600]

    def _worker():
        voice_key = get_current_voice()
        voice_info = VOICE_PROFILES.get(voice_key, VOICE_PROFILES[DEFAULT_VOICE])
        voice_id = voice_info["voice_id"]
        rate = get_voice_speed()

        temp_path = None
        success = False

        # Tier 1: Neural Edge TTS (Studio Quality)
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name

            asyncio.run(_synthesize_edge_tts(clean, voice_id, rate, temp_path))
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 500:
                _play_audio_file(temp_path)
                success = True
        except Exception:
            success = False

        # Tier 2: pyttsx3 (Offline Local System TTS)
        if not success:
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(clean)
                engine.runAndWait()
                success = True
            except Exception:
                success = False

        # Tier 3: gTTS (Google TTS Fallback)
        if not success:
            try:
                from gTTS import gTTS
                tts = gTTS(text=clean, lang="en", tld="com")
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                    temp_path = f.name
                    tts.save(temp_path)
                _play_audio_file(temp_path)
                success = True
            except Exception:
                success = False

        # Tier 4: Linux spd-say
        if not success and shutil.which("spd-say"):
            try:
                subprocess.run(["spd-say", clean[:250]], check=False)
            except Exception:
                pass

    if blocking:
        _worker()
    else:
        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
