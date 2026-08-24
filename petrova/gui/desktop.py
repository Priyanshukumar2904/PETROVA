"""
PETROVA Desktop Application Integration.
Registers the .desktop entry and high-resolution icon in ~/.local/share/applications.
"""

import os
import sys
from pathlib import Path

APP_ICON_SVG = """<svg width="512" height="512" viewBox="0 0 512 512" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#090d16" />
      <stop offset="50%" stop-color="#0f172a" />
      <stop offset="100%" stop-color="#020617" />
    </linearGradient>
    <linearGradient id="cyanNeon" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00f2fe" />
      <stop offset="100%" stop-color="#4facfe" />
    </linearGradient>
    <linearGradient id="purpleNeon" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#b827fc" />
      <stop offset="100%" stop-color="#2c90fc" />
    </linearGradient>
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="10" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- Squircle Base -->
  <rect width="496" height="496" x="8" y="8" rx="110" fill="url(#bgGrad)" stroke="#1e293b" stroke-width="6" />

  <!-- Outer Cyber Circuit Rings -->
  <circle cx="256" cy="256" r="180" fill="none" stroke="#00f2fe" stroke-width="3" stroke-dasharray="8,12" opacity="0.4" />
  <circle cx="256" cy="256" r="140" fill="none" stroke="#b827fc" stroke-width="2" opacity="0.3" />

  <!-- Neural Synapse Nodes -->
  <g opacity="0.85">
    <line x1="256" y1="130" x2="150" y2="230" stroke="#00f2fe" stroke-width="3" />
    <line x1="256" y1="130" x2="362" y2="230" stroke="#00f2fe" stroke-width="3" />
    <line x1="150" y1="230" x2="200" y2="350" stroke="#00f2fe" stroke-width="3" />
    <line x1="362" y1="230" x2="312" y2="350" stroke="#00f2fe" stroke-width="3" />
    <line x1="200" y1="350" x2="312" y2="350" stroke="#00f2fe" stroke-width="3" />
    <line x1="150" y1="230" x2="362" y2="230" stroke="#b827fc" stroke-width="2" stroke-dasharray="6,6" />

    <circle cx="256" cy="130" r="14" fill="#00f2fe" filter="url(#glow)" />
    <circle cx="150" cy="230" r="12" fill="#00f2fe" filter="url(#glow)" />
    <circle cx="362" cy="230" r="12" fill="#00f2fe" filter="url(#glow)" />
    <circle cx="200" cy="350" r="12" fill="#00f2fe" filter="url(#glow)" />
    <circle cx="312" cy="350" r="12" fill="#00f2fe" filter="url(#glow)" />
  </g>

  <!-- Center Monogram 'P' Glowing Emblem -->
  <g transform="translate(190, 160)" filter="url(#glow)">
    <path d="M 0 0 L 70 0 C 105 0 125 18 125 48 C 125 78 105 96 70 96 L 36 96 L 36 170 L 0 170 Z M 36 32 L 36 64 L 66 64 C 82 64 90 56 90 48 C 90 40 82 32 66 32 Z" fill="url(#cyanNeon)" />
  </g>

  <!-- Core Pulsing Star -->
  <circle cx="256" cy="256" r="6" fill="#ffffff" filter="url(#glow)" />
</svg>
"""


def ensure_desktop_entry() -> bool:
    """
    Install the ~/.local/share/applications/petrova.desktop file and application icons.
    Allows the user to launch PETROVA directly from any desktop app launcher with 1 click.
    """
    try:
        home = Path.home()
        apps_dir = home / ".local" / "share" / "applications"
        icons_dir = home / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps"
        pixmaps_dir = home / ".local" / "share" / "pixmaps"

        apps_dir.mkdir(parents=True, exist_ok=True)
        icons_dir.mkdir(parents=True, exist_ok=True)
        pixmaps_dir.mkdir(parents=True, exist_ok=True)

        # 1. Save SVG Icon
        icon_path = icons_dir / "petrova.svg"
        icon_path.write_text(APP_ICON_SVG, encoding="utf-8")

        # Also place in pixmaps for X11 legacy fallbacks
        pixmap_path = pixmaps_dir / "petrova.svg"
        pixmap_path.write_text(APP_ICON_SVG, encoding="utf-8")

        # 2. Determine Python / Executable launcher path
        executable = sys.executable
        exec_cmd = f"{executable} -m petrova.gui"

        # Check if ~/.local/bin/petrova launcher exists
        bin_launcher = home / ".local" / "bin" / "petrova"
        if bin_launcher.exists() and os.access(bin_launcher, os.X_OK):
            exec_cmd = f"{bin_launcher} --gui"

        # 3. Create .desktop file
        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=PETROVA
GenericName=AI Operating Assistant
Comment=Privacy-First AI Operating Assistant & Interactive Linux Terminal
Exec={exec_cmd}
Icon=petrova
Terminal=false
Categories=Utility;System;Development;ArtificialIntelligence;
Keywords=ai;assistant;terminal;linux;petrova;llm;system;
StartupNotify=true
StartupWMClass=petrova-gui
"""

        desktop_file = apps_dir / "petrova.desktop"
        desktop_file.write_text(desktop_content, encoding="utf-8")
        desktop_file.chmod(0o755)

        return True
    except Exception:
        return False
