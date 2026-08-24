"""
Voice Interaction & Control Commands (/voice, /listen, /speak).
Supports switching neural voice personalities, rate adjustment, and testing.
"""

import sys
from rich.panel import Panel
from rich.table import Table
from petrova.ui.console import console
from petrova.voice.tts import (
    speak,
    is_voice_enabled,
    set_voice_enabled,
    stop_speaking,
    VOICE_PROFILES,
    get_current_voice,
    set_current_voice,
    get_voice_speed,
    set_voice_speed,
)
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
        active_voice = get_current_voice()
        console.print(f"🎙️ Spoken voice output is now: {state_str} (Voice: [bold cyan]{active_voice.capitalize()}[/bold cyan])")
        if new_state:
            speak(f"Voice responses are now enabled using the {active_voice} voice profile.")
        return True

    subcmd = args[0].lower()

    if subcmd in ("on", "enable", "start"):
        set_voice_enabled(True)
        active_voice = get_current_voice()
        console.print(f"🎙️ Spoken voice output: [bold green]ENABLED[/bold green] (Profile: [cyan]{active_voice.capitalize()}[/cyan])")
        speak("Voice output is enabled.")

    elif subcmd in ("off", "disable", "stop"):
        set_voice_enabled(False)
        stop_speaking()
        console.print("🎙️ Spoken voice output: [bold yellow]DISABLED[/bold yellow]")

    elif subcmd in ("list", "voices", "catalog"):
        _show_voice_catalog()

    elif subcmd in ("set", "select", "voice", "use"):
        if len(args) > 1:
            chosen = args[1].lower().strip()
            if set_current_voice(chosen):
                info = VOICE_PROFILES[chosen]
                console.print(f"✓ Active voice set to: [bold green]{info['name']}[/bold green] ({info['desc']})")
                speak(f"Hello, I am now speaking with the {info['name']} voice profile.")
            else:
                valid = ", ".join(VOICE_PROFILES.keys())
                console.print(f"[yellow]Unknown voice '{chosen}'. Available options: {valid}[/yellow]")
        else:
            _show_voice_catalog()

    elif subcmd in ("speed", "rate"):
        if len(args) > 1:
            rate_val = args[1].lower().strip()
            if rate_val in ("normal", "default", "1x"):
                set_voice_speed("+0%")
                console.print("✓ Voice speed set to: [bold green]Normal (+0%)[/bold green]")
            elif rate_val in ("faster", "fast", "1.2x"):
                set_voice_speed("+15%")
                console.print("✓ Voice speed set to: [bold green]Fast (+15%)[/bold green]")
            elif rate_val in ("slower", "slow", "0.8x"):
                set_voice_speed("-15%")
                console.print("✓ Voice speed set to: [bold green]Slow (-15%)[/bold green]")
            elif "%" in rate_val or rate_val.startswith(("+", "-")):
                set_voice_speed(rate_val if rate_val.endswith("%") else f"{rate_val}%")
                console.print(f"✓ Voice speed set to: [bold green]{get_voice_speed()}[/bold green]")
            speak("Testing new voice speed adjustment.")
        else:
            console.print(f"Current voice speed: [cyan]{get_voice_speed()}[/cyan] (Options: normal, faster, slower, +10%, -10%)")

    elif subcmd in ("test", "preview"):
        active_voice = get_current_voice()
        info = VOICE_PROFILES.get(active_voice, VOICE_PROFILES["nova"])
        phrase = f"Greetings. This is a voice test of the {info['name']} neural voice profile in PETROVA."
        console.print(f"[dim]Previewing voice '[cyan]{info['name']}[/cyan]'...[/dim]")
        speak(phrase, blocking=True)

    elif subcmd in ("listen", "mic", "hear"):
        listen_command()

    elif subcmd in ("speak", "say"):
        if len(args) > 1:
            phrase = " ".join(args[1:])
            console.print(f"[dim]Speaking: \"{phrase}\"...[/dim]")
            speak(phrase, blocking=True)
        else:
            console.print("[red]Usage: /voice speak <text>[/red]")

    elif subcmd in ("loop", "interactive", "chat"):
        interactive_voice_loop()

    elif subcmd in ("status", "info"):
        state_str = "[bold green]ON[/bold green]" if is_voice_enabled() else "[bold yellow]OFF[/bold yellow]"
        active_voice = get_current_voice()
        speed = get_voice_speed()
        console.print(f"🎙️ Voice Output: {state_str} | Active Profile: [bold cyan]{active_voice.capitalize()}[/bold cyan] | Speed: [bold cyan]{speed}[/bold cyan]")

    else:
        console.print(f"[yellow]Unknown voice option '{subcmd}'.[/yellow]")
        console.print("[dim]Options: /voice on, /voice off, /voice list, /voice set <name>, /voice speed <speed>, /voice test, /listen, /voice loop[/dim]")

    return True


def _show_voice_catalog():
    """Display available neural voice profiles in a table."""
    current = get_current_voice()
    table = Table(title="🎙️ PETROVA High-Fidelity Voice Catalog", border_style="cyan", show_header=True)
    table.add_column("Profile", style="bold cyan", width=12)
    table.add_column("Gender / Accent", style="yellow", width=18)
    table.add_column("Description", style="white", width=44)
    table.add_column("Status", style="bold green", width=10)

    for key, info in VOICE_PROFILES.items():
        is_active = "● ACTIVE" if key == current else ""
        gender = "Female / US" if "Female" in info["desc"] and "British" not in info["desc"] and "Australian" not in info["desc"] else \
                 "Male / US" if "Male" in info["desc"] and "British" not in info["desc"] else \
                 "Female / UK" if "British (Female)" in info["desc"] or ("British" in info["desc"] and "Female" in info["desc"]) else \
                 "Male / UK" if "British (Male)" in info["desc"] or ("British" in info["desc"] and "Male" in info["desc"]) else \
                 "Female / AU" if "Australian" in info["desc"] else "Neural"
        
        status_styled = f"[bold green]{is_active}[/bold green]" if is_active else "[dim]available[/dim]"
        table.add_row(key, gender, info["desc"], status_styled)

    console.print(table)
    console.print("[dim]To switch voice, type: [bold cyan]/voice set <name>[/bold cyan] (e.g. [bold]/voice set echo[/bold])[/dim]\n")


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
