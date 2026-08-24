"""
PETROVA Interactive Embedded Terminal Drawer Widget.
Provides an integrated command console for shell execution, live streaming, and interactive stdin piping.
"""

from typing import List, Optional
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QPlainTextEdit,
    QLineEdit,
    QPushButton,
    QLabel,
)


class TerminalDrawerWidget(QFrame):
    """
    Collapsible interactive terminal console embedded at the bottom of the GUI.
    Supports live real-time output streaming and user stdin interaction (y/n, inputs).
    """
    command_submitted = pyqtSignal(str)
    stdin_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TerminalDrawer")
        self.history: List[str] = []
        self.history_index: int = 0
        self.is_busy: bool = False

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Header Bar
        header = QHBoxLayout()
        title = QLabel("💻 INTERACTIVE LINUX TERMINAL DRAWER")
        title.setStyleSheet("color: #FFFFFF; font-weight: 800; font-size: 11.5px; letter-spacing: 1px;")

        # Quick Action Chips
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        for label, cmd in [
            ("⚡ /stats", "/stats"),
            ("🧠 /memory", "/memory list"),
            ("🔄 Update System", "sudo pacman -Syu --noconfirm"),
            ("💾 df -h", "df -h /"),
            ("🧹 Clear", "clear"),
        ]:
            btn = QPushButton(label)
            btn.setObjectName("MonochromePill")
            btn.clicked.connect(lambda checked, c=cmd: self.run_quick_command(c))
            chips_layout.addWidget(btn)

        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(22, 22)
        self.close_btn.setStyleSheet("padding: 0; font-weight: bold; border-radius: 11px;")
        self.close_btn.setToolTip("Close Terminal Drawer")

        header.addWidget(title)
        header.addStretch()
        header.addLayout(chips_layout)
        header.addWidget(self.close_btn)
        layout.addLayout(header)

        # Console Output
        self.output = QPlainTextEdit()
        self.output.setObjectName("TerminalOutput")
        self.output.setReadOnly(True)
        self.output.setMaximumBlockCount(2000)
        layout.addWidget(self.output)

        # Welcome message
        self.append_output("⚡ PETROVA Terminal Console Ready. Type shell commands or interactive responses below:\n")

        # Input Box
        input_layout = QHBoxLayout()
        self.prompt_prefix = QLabel("❯")
        self.prompt_prefix.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 14px; margin-right: 4px;")
        
        self.input_field = QLineEdit()
        self.input_field.setObjectName("TerminalInput")
        self.input_field.setPlaceholderText("Enter command or respond to prompts (e.g. y, n, pacman -Qe)...")
        self.input_field.returnPressed.connect(self._on_submit)

        self.run_btn = QPushButton("Run / Send")
        self.run_btn.setObjectName("MonochromePill")
        self.run_btn.clicked.connect(self._on_submit)

        input_layout.addWidget(self.prompt_prefix)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.run_btn)
        layout.addLayout(input_layout)

    def set_busy_state(self, busy: bool, prompt_text: str = ""):
        """Update terminal prompt indicator when a background process is active."""
        self.is_busy = busy
        if busy:
            self.prompt_prefix.setText("❯ (in)")
            self.input_field.setPlaceholderText(prompt_text or "Process running... Type response (y/n, text) and press Enter")
        else:
            self.prompt_prefix.setText("❯")
            self.input_field.setPlaceholderText("Enter command (e.g. uname -a, sudo pacman -Syu, fastfetch)...")

    def append_output(self, text: str):
        """Append text to output console."""
        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.output.insertPlainText(text)
        self.output.moveCursor(QTextCursor.MoveOperation.End)

    def run_quick_command(self, cmd: str):
        if cmd == "clear":
            self.output.clear()
            return
        self.input_field.setText(cmd)
        self._on_submit()

    def _on_submit(self):
        text = self.input_field.text().strip()
        if not text:
            return

        self.input_field.clear()

        if text == "clear" and not self.is_busy:
            self.output.clear()
            return

        # If a process is currently running and asking for input:
        if self.is_busy:
            self.append_output(f"{text}\n")
            self.stdin_submitted.emit(text)
        else:
            self.history.append(text)
            self.history_index = len(self.history)
            self.append_output(f"\n❯ {text}\n")
            self.command_submitted.emit(text)
