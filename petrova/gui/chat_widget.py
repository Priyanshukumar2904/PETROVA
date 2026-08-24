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
    """A single chat message card (User or Petrova) with translucent glass styling."""
    run_command_requested = pyqtSignal(str)

    def __init__(self, role: str, content: str = "", timestamp: str = "", parent=None):
        super().__init__(parent)
        self.role = role
        self.raw_content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)

        # Header (Role badge + Timestamp + Voice / Copy buttons)
        header = QHBoxLayout()
        header.setSpacing(8)

        if self.role == "user":
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(16, 185, 129, 0.1);
                    border: 1px solid rgba(52, 211, 153, 0.25);
                    border-radius: 14px;
                    margin-left: 60px;
                }
            """)
            role_lbl = QLabel("👤 You")
            role_lbl.setStyleSheet("color: #34d399; font-weight: 700; font-size: 12.5px;")
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(12, 18, 26, 0.85);
                    border: 1px solid rgba(16, 185, 129, 0.15);
                    border-radius: 14px;
                    margin-right: 40px;
                }
            """)
            role_lbl = QLabel("🤖 PETROVA")
            role_lbl.setStyleSheet("color: #00f59b; font-weight: 900; font-size: 13px; letter-spacing: 1.5px;")

        time_lbl = QLabel(self.timestamp)
        time_lbl.setStyleSheet("color: #64748b; font-size: 11px;")

        header.addWidget(role_lbl)
        header.addWidget(time_lbl)
        header.addStretch()

        if self.role == "assistant":
            # Speak Button
            self.speak_btn = QPushButton("🔊")
            self.speak_btn.setFixedSize(26, 26)
            self.speak_btn.setStyleSheet("padding: 0; font-size: 12px; background: transparent; border: none; color: #94a3b8;")
            self.speak_btn.setToolTip("Read Response Aloud")
            self.speak_btn.clicked.connect(self._on_speak)
            header.addWidget(self.speak_btn)

        # Copy text button
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(26, 26)
        self.copy_btn.setStyleSheet("padding: 0; font-size: 11px; background: transparent; border: none; color: #94a3b8;")
        self.copy_btn.setToolTip("Copy message to clipboard")
        self.copy_btn.clicked.connect(self._on_copy)
        header.addWidget(self.copy_btn)

        layout.addLayout(header)

        # Content Label
        self.content_lbl = QLabel()
        self.content_lbl.setWordWrap(True)
        self.content_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.content_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.content_lbl.setStyleSheet("color: #f1f5f9; font-size: 13.5px; line-height: 1.5;")
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
                f"<div style='background-color:rgba(6,9,14,0.9); border:1px solid rgba(16,185,129,0.2); border-radius:8px; padding:10px; margin:8px 0;'>"
                f"<div style='color:#34d399; font-size:10.5px; font-weight:bold; letter-spacing:1px; margin-bottom:4px;'>{lang.upper()}</div>"
                f"<pre style='color:#a7f3d0; font-family:monospace; font-size:12.5px; margin:0; line-height:1.4;'>{code}</pre>"
                f"</div>"
            )
        formatted = code_block_pattern.sub(replace_code_block, escaped)

        # Replace inline `code`
        inline_code_pattern = re.compile(r"`([^`]+)`")
        formatted = inline_code_pattern.sub(r"<code style='background-color:rgba(16,185,129,0.15); color:#00f59b; padding:2px 6px; border-radius:4px; font-family:monospace; font-size:12.5px;'>\1</code>", formatted)

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
                    background-color: rgba(9, 14, 20, 0.95);
                    border: 1px solid #10b981;
                    border-radius: 10px;
                    padding: 10px;
                    margin-top: 8px;
                }
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(10, 8, 10, 8)
            c_layout.setSpacing(8)

            top = QHBoxLayout()
            c_title = QLabel("⚡ Proposed Linux Command:")
            c_title.setStyleSheet("color: #00f59b; font-weight: bold; font-size: 11.5px;")
            top.addWidget(c_title)
            top.addStretch()
            c_layout.addLayout(top)

            cmd_text = QLabel(f"<code>{html.escape(cmd)}</code>")
            cmd_text.setStyleSheet("color: #fbbf24; font-family: monospace; font-size: 12.5px; font-weight: bold;")
            c_layout.addWidget(cmd_text)

            btn_row = QHBoxLayout()
            btn_row.addStretch()
            
            run_btn = QPushButton("⚡ Run Command")
            run_btn.setObjectName("PrimaryButton")
            run_btn.setStyleSheet("padding: 5px 14px; font-size: 11.5px; border-radius: 8px;")
            run_btn.clicked.connect(lambda checked, c=cmd: self.run_command_requested.emit(c))
            btn_row.addWidget(run_btn)

            c_layout.addLayout(btn_row)
            self.cmd_container.addWidget(card)

    def _on_speak(self):
        """Read message aloud."""
        speak(self.raw_content)

    def _on_copy(self):
        """Copy message to system clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.raw_content)
        self.copy_btn.setText("✓")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.copy_btn.setText("📋"))


class ChatWidget(QWidget):
    """
    Scrollable multi-turn chat stream container.
    """
    run_command_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.current_assistant_card: Optional[MessageCard] = None

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("ChatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.chat_container = QWidget()
        self.chat_container.setObjectName("ChatContentWidget")
        self.messages_layout = QVBoxLayout(self.chat_container)
        self.messages_layout.setContentsMargins(20, 16, 20, 16)
        self.messages_layout.setSpacing(14)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)

    def add_user_message(self, text: str):
        """Append user question."""
        card = MessageCard(role="user", content=text)
        # Insert before stretch
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()

    def start_assistant_message(self) -> MessageCard:
        """Create new streaming message card for assistant."""
        card = MessageCard(role="assistant", content="")
        card.run_command_requested.connect(self.run_command_requested.emit)
        self.current_assistant_card = card
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()
        return card

    def append_assistant_token(self, token: str):
        """Append token to active assistant card."""
        if self.current_assistant_card:
            self.current_assistant_card.update_content(self.current_assistant_card.raw_content + token)
            self._scroll_to_bottom()

    def finalize_assistant_message(self, full_text: str):
        """Finalize assistant response and render command cards."""
        if self.current_assistant_card:
            self.current_assistant_card.update_content(full_text)
            self.current_assistant_card.finalize()
            self.current_assistant_card = None
            self._scroll_to_bottom()

    def add_assistant_message(self, text: str):
        """Directly append complete assistant message."""
        card = MessageCard(role="assistant", content=text)
        card.run_command_requested.connect(self.run_command_requested.emit)
        card.finalize()
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        """Smoothly scroll to latest message."""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
