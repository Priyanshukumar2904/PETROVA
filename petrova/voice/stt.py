"""
Speech-to-Text (STT) Voice Input Engine for PETROVA.
Captures user microphone audio on Linux and transcribes into text.
"""

import os
import shutil
import tempfile
import subprocess
from typing import Optional

from rich.panel import Panel
from rich.status import Status
from petrova.ui.console import console


def record_audio_clip(duration: int = 5) -> Optional[str]:
    """Record microphone audio using arecord, pw-record, or ffmpeg."""
    temp_wav = tempfile.mktemp(suffix=".wav")

    # Select available Linux recorder
    if shutil.which("arecord"):
        cmd = ["arecord", "-d", str(duration), "-f", "cd", "-t", "wav", "-q", temp_wav]
    elif shutil.which("pw-record"):
        cmd = ["pw-record", "--rate", "44100", "--channels", "1", temp_wav]
    elif shutil.which("ffmpeg"):
        cmd = ["ffmpeg", "-y", "-f", "pulse", "-i", "default", "-t", str(duration), temp_wav]
    else:
        console.print("[bold red]No Linux audio recorder (arecord, pw-record, ffmpeg) found in PATH.[/bold red]")
        return None

    try:
        if cmd[0] == "pw-record":
            # pw-record doesn't take -d flag, so spawn and terminate after duration
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            import time
            time.sleep(duration)
            proc.terminate()
            proc.wait()
        else:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=duration + 3)

        if os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 1000:
            return temp_wav
    except Exception as e:
        console.print(f"[bold red]Recording failed:[/bold red] {e}")

    return None


def listen_and_transcribe(duration: int = 5) -> Optional[str]:
    """
    Listen to user voice via microphone for duration seconds and transcribe to text.
    """
    console.print()
    with console.status(f"[bold cyan]🎙️ Listening for {duration} seconds... (Speak now)[/bold cyan]", spinner="dots"):
        wav_path = record_audio_clip(duration)

    if not wav_path:
        console.print("[yellow]Could not capture audio from microphone.[/yellow]")
        return None

    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        console.print("[dim]Transcribing speech...[/dim]")
        text = recognizer.recognize_google(audio_data)

        if text:
            console.print(f"[bold green]✓ Heard:[/bold green] \"{text}\"")
            return text.strip()

    except sr.UnknownValueError:
        console.print("[yellow]Could not understand audio (too quiet or unclear).[/yellow]")
    except Exception as e:
        console.print(f"[bold red]Speech recognition error:[/bold red] {e}")
    finally:
        try:
            if os.path.exists(wav_path):
                os.unlink(wav_path)
        except Exception:
            pass

    return None
