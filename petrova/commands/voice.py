"""
Voice Interaction & Control Commands (/voice, /listen, /speak).
"""

import sys
from rich.panel import Panel
from petrova.ui.console import console
from petrova.voice.tts import speak, is_voice_enabled, set_voice_enabled, stop_speaking
from petrova.voice.stt import listen_and_transcribe
from petrova.brain.brain import stream_ask
from petrova.config.settings import get_config


def voice_command(args: list[str] = None):
    """Handle /voice commands."""
    config = get_config()

    if not args:
        current = is_voice_enabled()
        new_state = not current
        set_voice_enabled(new_state)
        state_str = "[bold green]ENABLED (ON)[/bold green]" if new_state else "[bold yellow]DISABLED (OFF)[/bold yellow]"
        console.print(f"🎙️ Spoken voice output is now: {state_str}")
        if new_state:
            speak("Voice responses are now enabled.")
        return True

    action = args[0].lower()

    if action in ("on", "enable", "start"):
        set_voice_enabled(True)
        console.print("🎙️ Spoken voice output: [bold green]ENABLED[/bold green]")
        speak("Voice output is enabled.")

    elif action in ("off", "disable", "stop"):
        set_voice_enabled(False)
        stop_speaking()
        console.print("🎙️ Spoken voice output: [bold yellow]DISABLED[/bold yellow]")

    elif action in ("listen", "mic", "hear"):
        listen_command()

    elif action in ("speak", "say"):
        if len(args) > 1:
            phrase = " ".join(args[1:])
            console.print(f"[dim]Speaking: \"{phrase}\"...[/dim]")
            speak(phrase, blocking=True)
        else:
            console.print("[red]Usage: /voice speak <text>[/red]")

    elif action in ("loop", "interactive", "chat"):
        interactive_voice_loop()

    elif action in ("status", "info"):
        state_str = "[bold green]ON[/bold green]" if is_voice_enabled() else "[bold yellow]OFF[/bold yellow]"
        console.print(f"🎙️ Spoken Voice Output: {state_str}")

    else:
        console.print(f"[yellow]Unknown voice option '{action}'.[/yellow]")
        console.print("[dim]Options: /voice on, /voice off, /listen, /voice speak <text>, /voice loop[/dim]")

    return True


def listen_command(duration: int = 5):
    """Capture speech from microphone, process with PETROVA, and speak response."""
    user_speech = listen_and_transcribe(duration=duration)
    if not user_speech:
        return True

    console.print()
    console.print(f"[bold cyan]You (Voice):[/bold cyan] {user_speech}")
    console.print()
    console.print("[bold green]PETROVA[/bold green]")

    response_parts = []
    for token in stream_ask(user_speech):
        sys.stdout.write(token)
        sys.stdout.flush()
        response_parts.append(token)
    sys.stdout.write("\n")
    sys.stdout.flush()

    full_response = "".join(response_parts)
    # Always speak the answer when asked via microphone
    speak(full_response)
    return True


def interactive_voice_loop():
    """Hands-free continuous conversational voice session."""
    console.print(Panel(
        "[bold cyan]🎙️ PETROVA Interactive Hands-Free Voice Mode[/bold cyan]\n\n"
        "Speak naturally. Say '[bold red]goodbye[/bold red]' or press [bold]Ctrl+C[/bold] to exit back to terminal.",
        border_style="cyan"
    ))
    speak("Interactive voice mode started. I am listening.", blocking=True)

    while True:
        try:
            user_speech = listen_and_transcribe(duration=5)
            if not user_speech:
                continue

            if any(term in user_speech.lower() for term in ["goodbye", "exit", "quit voice", "stop listening"]):
                console.print("[bold green]Exiting voice mode.[/bold green]")
                speak("Goodbye for now.", blocking=True)
                break

            console.print()
            console.print(f"[bold cyan]You (Voice):[/bold cyan] {user_speech}")
            console.print("\n[bold green]PETROVA[/bold green]")

            response_parts = []
            for token in stream_ask(user_speech):
                sys.stdout.write(token)
                sys.stdout.flush()
                response_parts.append(token)
            sys.stdout.write("\n\n")
            sys.stdout.flush()

            full_response = "".join(response_parts)
            speak(full_response, blocking=True)

        except KeyboardInterrupt:
            console.print("\n[dim]Voice loop ended.[/dim]\n")
            break
        except Exception as e:
            console.print(f"[bold red]Voice error:[/bold red] {e}")
            break
