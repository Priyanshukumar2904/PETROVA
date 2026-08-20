"""
Text-to-Speech (TTS) Voice Engine for PETROVA.
Converts PETROVA's responses into natural spoken voice.
"""

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

    # Cleanup temp audio
    try:
        if os.path.exists(audio_path):
            os.unlink(audio_path)
    except Exception:
        pass


def speak(text: str, blocking: bool = False):
    """
    Synthesize and speak text.
    If blocking=False, plays asynchronously in a background thread.
    """
    clean = clean_text_for_speech(text)
    if not clean:
        return

    def _worker():
        try:
            from gtts import gTTS
            tts = gTTS(text=clean[:500], lang="en", tld="com")
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                temp_path = f.name
                tts.save(temp_path)

            _play_audio_file(temp_path)

        except Exception:
            # Fallback to spd-say if gTTS fails
            if shutil.which("spd-say"):
                try:
                    subprocess.run(["spd-say", clean[:250]], check=False)
                except Exception:
                    pass

    if blocking:
        _worker()
    else:
        thread = threading.Thread(target=_worker, daemon=True)
        thread.start()
