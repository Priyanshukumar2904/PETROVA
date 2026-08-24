"""
PETROVA GUI Application Runner.
Initializes QApplication, registers desktop integration, and launches PetrovaMainWindow.
"""

import sys
import os
from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QApplication

from petrova.memory.store import initialize as init_memory
from petrova.config.settings import get_config
from petrova.core.server import is_server_running, start_server
from petrova.gui.desktop import ensure_desktop_entry
from petrova.gui.window import PetrovaMainWindow


def launch_gui() -> int:
    """Launch PETROVA Desktop GUI Application."""
    # 1. Initialize persistent SQLite database
    init_memory()

    # 2. Automatically ensure .desktop launcher & icon exist in user's OS
    ensure_desktop_entry()

    # 3. Check and start local AI backend if needed
    config = get_config()
    if config.get("auto_start_server", True):
        host = config.get("server_host", "127.0.0.1")
        port = config.get("server_port", 8080)
        if not is_server_running(host, port):
            start_server()

    # 4. Initialize Qt Application
    # High-DPI scaling is enabled by default in Qt6
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    app.setApplicationName("PETROVA")
    app.setApplicationDisplayName("PETROVA — AI Operating Assistant")
    app.setDesktopFileName("petrova")

    # Set Window Icon from SVG if available
    icon_path = Path.home() / ".local" / "share" / "icons" / "hicolor" / "scalable" / "apps" / "petrova.svg"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = PetrovaMainWindow()
    window.show()

    return app.exec()


def main():
    """Main entrypoint for petrova-gui."""
    sys.exit(launch_gui())


if __name__ == "__main__":
    main()
