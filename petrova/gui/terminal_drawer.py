"""
PETROVA Interactive Embedded Terminal Drawer Widget.
Provides an integrated command console for shell execution and slash commands.
"""

import io
import contextlib
import subprocess
import threading
from typing import List
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

from petrova.tools.executor import execute_command
from petrova.core.router import route_command


class TerminalDrawerWidget(QFrame):
    """
    Collapsible interactive terminal console embedded at the bottom of the GUI.
    """
    command_executed = pyqtSignal(str, str, int)  # cmd, output, returncode

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TerminalDrawer")
        self.history: List[str] = []
        self.history_index: int = 0

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(6)

        # Header Bar
        header = QHBoxLayout()
        title = QLabel("💻 INTERACTIVE LINUX TERMINAL DRAWER")
        title.setStyleSheet("color: #00f59b; font-weight: 800; font-size: 11.5px; letter-spacing: 1px;")

        # Quick Action Chips
        chips_layout = QHBoxLayout()
        chips_layout.setSpacing(6)
        for label, cmd in [
            ("⚡ /stats", "/stats"),
            ("🧠 /memory", "/memory list"),
            ("🎯 /goal", "/goal check system updates"),
            ("💾 df -h", "df -h /"),
            ("🧹 Clear", "clear"),
        ]:
            btn = QPushButton(label)
            btn.setStyleSheet("padding: 3px 10px; font-size: 10.5px; border-radius: 6px; background: rgba(16,185,129,0.12); color: #34d399;")
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
        self.output.setMaximumBlockCount(1000)
        layout.addWidget(self.output)

        # Welcome message
        self.append_output("⚡ PETROVA Terminal Console Ready. Type shell commands or /slash commands below:\n")

        # Input Box
        input_layout = QHBoxLayout()
        prompt_prefix = QLabel("❯")
        prompt_prefix.setStyleSheet("color: #00f59b; font-weight: bold; font-size: 14px; margin-right: 4px;")
        
        self.input_field = QLineEdit()
        self.input_field.setObjectName("TerminalInput")
        self.input_field.setPlaceholderText("Enter command (e.g. uname -a, /goal, pacman -Qe, fastfetch)...")
        self.input_field.returnPressed.connect(self._on_submit)

        run_btn = QPushButton("Run")
        run_btn.setObjectName("PrimaryButton")
        run_btn.setStyleSheet("padding: 6px 14px; font-size: 11.5px; border-radius: 8px;")
        run_btn.clicked.connect(self._on_submit)

        input_layout.addWidget(prompt_prefix)
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(run_btn)
        layout.addLayout(input_layout)

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
        cmd = self.input_field.text().strip()
        if not cmd:
            return

        self.input_field.clear()
        self.history.append(cmd)
        self.history_index = len(self.history)

        if cmd == "clear":
            self.output.clear()
            return

        self.append_output(f"\n❯ {cmd}\n")

        # Run command in background thread
        threading.Thread(target=self._execute_async, args=(cmd,), daemon=True).start()

    def _execute_async(self, cmd: str):
        try:
            # Check if it's a built-in slash command
            if cmd.startswith("/"):
                code, stdout, stderr = execute_command(f"python3 -c 'from petrova.core.router import route_command; route_command(\"{cmd}\")'")
            else:
                code, stdout, stderr = execute_command(cmd)

            output = stdout if stdout else ""
            if stderr:
                output += f"\n[stderr]: {stderr}"
            if not output.strip():
                output = f"[Process exited with code {code}]\n"
            
            # Post back to main thread
            self.command_executed.emit(cmd, output, code)
        except Exception as e:
            self.command_executed.emit(cmd, f"Error: {str(e)}\n", 1)
