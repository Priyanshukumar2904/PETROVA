"""
PETROVA Chat Stream & Message Bubble Widget.
Renders conversational AI responses, syntax-highlighted code snippets, and executable command cards.
"""

import html
import re
from datetime import datetime
from typing import List, Optional
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QCursor
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
    QApplication,
)

from petrova.voice.tts import speak


class MessageCard(QFrame):
    """A single chat message card (User or Petrova)."""
    run_command_requested = pyqtSignal(str)

    def __init__(self, role: str, content: str = "", timestamp: str = "", parent=None):
        super().__init__(parent)
        self.role = role
        self.raw_content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Header (Role badge + Timestamp + Voice / Copy buttons)
        header = QHBoxLayout()
        header.setSpacing(8)

        if self.role == "user":
            self.setStyleSheet("""
                QFrame {
                    background-color: #142032;
                    border: 1px solid #1e3a5f;
                    border-radius: 12px;
                    margin-left: 60px;
                }
            """)
            role_lbl = QLabel("👤 You")
            role_lbl.setStyleSheet("color: #38bdf8; font-weight: 700; font-size: 12px;")
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #111827;
                    border: 1px solid #1f293d;
                    border-radius: 12px;
                    margin-right: 40px;
                }
            """)
            role_lbl = QLabel("🤖 PETROVA")
            role_lbl.setStyleSheet("color: #00f0ff; font-weight: 800; font-size: 12px; letter-spacing: 1px;")

        time_lbl = QLabel(self.timestamp)
        time_lbl.setStyleSheet("color: #64748b; font-size: 10px;")

        header.addWidget(role_lbl)
        header.addWidget(time_lbl)
        header.addStretch()

        if self.role == "assistant":
            # Speak Button
            self.speak_btn = QPushButton("🔊")
            self.speak_btn.setFixedSize(24, 24)
            self.speak_btn.setStyleSheet("padding: 0; font-size: 12px; background: transparent; border: none;")
            self.speak_btn.setToolTip("Read Response Aloud")
            self.speak_btn.clicked.connect(self._on_speak)
            header.addWidget(self.speak_btn)

        # Copy text button
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(24, 24)
        self.copy_btn.setStyleSheet("padding: 0; font-size: 11px; background: transparent; border: none;")
        self.copy_btn.setToolTip("Copy message to clipboard")
        self.copy_btn.clicked.connect(self._on_copy)
        header.addWidget(self.copy_btn)

        layout.addLayout(header)

        # Content Label
        self.content_lbl = QLabel()
        self.content_lbl.setWordWrap(True)
        self.content_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.content_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.content_lbl.setStyleSheet("color: #f1f5f9; font-size: 13px; line-height: 1.4;")
        layout.addWidget(self.content_lbl)

        # Container for interactive command action cards
        self.cmd_container = QVBoxLayout()
        self.cmd_container.setSpacing(6)
        layout.addLayout(self.cmd_container)

        self._render_text()

    def update_content(self, text: str):
        """Streaming update for assistant token generation."""
        self.raw_content = text
        self._render_text()

    def _render_text(self):
        """Format markdown, code snippets, and commands into rich HTML."""
        text = self.raw_content

        # Simple HTML escape
        escaped = html.escape(text)

        # Replace markdown code blocks ```bash ... ```
        code_block_pattern = re.compile(r"```([a-zA-Z0-9_\-]+)?\n(.*?)```", re.DOTALL)
        def replace_code_block(match):
            lang = match.group(1) or "code"
            code = match.group(2)
            return (
                f"<div style='background-color:#0b0f19; border:1px solid #1e293b; border-radius:6px; padding:8px; margin:6px 0;'>"
                f"<div style='color:#64748b; font-size:10px; font-weight:bold; margin-bottom:4px;'>{lang.upper()}</div>"
                f"<pre style='color:#38bdf8; font-family:monospace; font-size:12px; margin:0;'>{code}</pre>"
                f"</div>"
            )
        formatted = code_block_pattern.sub(replace_code_block, escaped)

        # Replace inline `code`
        inline_code_pattern = re.compile(r"`([^`]+)`")
        formatted = inline_code_pattern.sub(r"<code style='background-color:#1e293b; color:#00f0ff; padding:2px 5px; border-radius:4px; font-family:monospace; font-size:12px;'>\1</code>", formatted)

        # Bold **text**
        formatted = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", formatted)

        # Convert newlines to breaks
        formatted = formatted.replace("\n", "<br>")

        self.content_lbl.setText(formatted)

    def finalize(self):
        """Called when streaming finishes to extract and render proposed command cards."""
        if self.role != "assistant":
            return

        from petrova.brain.brain import extract_suggested_commands
        commands = extract_suggested_commands(self.raw_content)

        # Clear existing command widgets
        while self.cmd_container.count():
            item = self.cmd_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for cmd in commands[:2]:
            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #0b111e;
                    border: 1px solid #00f0ff;
                    border-radius: 8px;
                    padding: 8px;
                    margin-top: 6px;
                }
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(8, 6, 8, 6)
            c_layout.setSpacing(6)

            top = QHBoxLayout()
            c_title = QLabel("⚡ Proposed System Command:")
            c_title.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 11px;")
            top.addWidget(c_title)
            top.addStretch()
            c_layout.addLayout(top)

            cmd_text = QLabel(f"<code>{html.escape(cmd)}</code>")
            cmd_text.setStyleSheet("color: #00ffaf; font-family: monospace; font-size: 12px;")
            c_layout.addWidget(cmd_text)

            btn_row = QHBoxLayout()
            btn_row.addStretch()
            
            run_btn = QPushButton("⚡ Execute Command")
            run_btn.setObjectName("PrimaryButton")
            run_btn.setStyleSheet("padding: 4px 12px; font-size: 11px;")
            run_btn.clicked.connect(lambda checked, c=cmd: self.run_command_requested.emit(c))
            btn_row.addWidget(run_btn)

            c_layout.addLayout(btn_row)
            self.cmd_container.addWidget(card)

    def _on_speak(self):
        if self.raw_content:
            speak(self.raw_content)

    def _on_copy(self):
        if self.raw_content:
            QApplication.clipboard().setText(self.raw_content)


class ChatWidget(QWidget):
    """
    Scrollable chat history containing conversational bubbles.
    """
    run_command_signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.current_assistant_card: Optional[MessageCard] = None

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.scroll = QScrollArea()
        self.scroll.setObjectName("ChatScrollArea")
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.content_widget = QWidget()
        self.content_widget.setObjectName("ChatContentWidget")
        self.cards_layout = QVBoxLayout(self.content_widget)
        self.cards_layout.setContentsMargins(16, 16, 16, 16)
        self.cards_layout.setSpacing(12)
        self.cards_layout.addStretch()

        self.scroll.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll)

    def add_user_message(self, text: str):
        """Add user message card."""
        card = MessageCard(role="user", content=text)
        # Insert before stretch
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        self._scroll_to_bottom()

    def start_assistant_message(self) -> MessageCard:
        """Start a new streaming assistant card."""
        card = MessageCard(role="assistant", content="")
        card.run_command_requested.connect(self.run_command_signal.emit)
        self.current_assistant_card = card
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        self._scroll_to_bottom()
        return card

    def append_assistant_token(self, token: str):
        """Append token to active assistant card."""
        if self.current_assistant_card:
            new_text = self.current_assistant_card.raw_content + token
            self.current_assistant_card.update_content(new_text)
            self._scroll_to_bottom()

    def finish_assistant_message(self):
        """Finalize streaming on the current assistant card."""
        if self.current_assistant_card:
            self.current_assistant_card.finalize()
            self.current_assistant_card = None
            self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Scroll chat view smoothly to bottom."""
        QApplication.processEvents()
        scrollbar = self.scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
