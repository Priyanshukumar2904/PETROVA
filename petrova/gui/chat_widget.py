"""
PETROVA Chat Stream & Message Bubble Widget.
Renders conversational AI responses with high-readability typography (15.5px+),
full-width responsive bubbles, syntax-highlighted code snippets, and executable command cards.
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
    """A single chat message card (User or Petrova) with translucent glass styling and comfortable typography."""
    run_command_requested = pyqtSignal(str)

    def __init__(self, role: str, content: str = "", timestamp: str = "", parent=None):
        super().__init__(parent)
        self.role = role
        self.raw_content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # Header (Role badge + Timestamp + Voice / Copy buttons)
        header = QHBoxLayout()
        header.setSpacing(10)

        if self.role == "user":
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(16, 185, 129, 0.12);
                    border: 1.5px solid rgba(52, 211, 153, 0.3);
                    border-radius: 16px;
                    margin-left: 80px;
                }
            """)
            role_lbl = QLabel("👤 You")
            role_lbl.setStyleSheet("color: #34d399; font-weight: 800; font-size: 14px;")
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: rgba(13, 20, 28, 0.9);
                    border: 1.5px solid rgba(16, 185, 129, 0.2);
                    border-radius: 16px;
                    margin-right: 40px;
                }
            """)
            role_lbl = QLabel("🤖 PETROVA")
            role_lbl.setStyleSheet("color: #00f59b; font-weight: 900; font-size: 14.5px; letter-spacing: 1.5px;")

        time_lbl = QLabel(self.timestamp)
        time_lbl.setStyleSheet("color: #64748b; font-size: 12px; font-weight: 600;")

        header.addWidget(role_lbl)
        header.addWidget(time_lbl)
        header.addStretch()

        if self.role == "assistant":
            # Speak Button
            self.speak_btn = QPushButton("🔊")
            self.speak_btn.setFixedSize(28, 28)
            self.speak_btn.setStyleSheet("padding: 0; font-size: 14px; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); border-radius: 14px; color: #34d399;")
            self.speak_btn.setToolTip("Read Response Aloud")
            self.speak_btn.clicked.connect(self._on_speak)
            header.addWidget(self.speak_btn)

        # Copy text button
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(28, 28)
        self.copy_btn.setStyleSheet("padding: 0; font-size: 13px; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); border-radius: 14px; color: #94a3b8;")
        self.copy_btn.setToolTip("Copy message to clipboard")
        self.copy_btn.clicked.connect(self._on_copy)
        header.addWidget(self.copy_btn)

        layout.addLayout(header)

        # Content Label with comfortable, large font
        self.content_lbl = QLabel()
        self.content_lbl.setWordWrap(True)
        self.content_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.content_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        self.content_lbl.setStyleSheet("color: #f8fafc; font-size: 15.5px; line-height: 1.6;")
        layout.addWidget(self.content_lbl)

        # Container for interactive command action cards
        self.cmd_container = QVBoxLayout()
        self.cmd_container.setSpacing(8)
        layout.addLayout(self.cmd_container)

        self._render_text()

    def update_content(self, text: str):
        """Streaming update for assistant token generation."""
        self.raw_content = text
        self._render_text()

    def _render_text(self):
        """Format markdown, code snippets, and commands into rich HTML with high-legibility fonts."""
        text = self.raw_content

        escaped = html.escape(text)

        # Replace markdown code blocks ```bash ... ```
        code_block_pattern = re.compile(r"```([a-zA-Z0-9_\-]+)?\n(.*?)```", re.DOTALL)
        def replace_code_block(match):
            lang = match.group(1) or "code"
            code = match.group(2)
            return (
                f"<div style='background-color:rgba(5,8,12,0.95); border:1.5px solid rgba(16,185,129,0.25); border-radius:10px; padding:12px 16px; margin:10px 0;'>"
                f"<div style='color:#34d399; font-size:11.5px; font-weight:bold; letter-spacing:1px; margin-bottom:6px;'>{lang.upper()}</div>"
                f"<pre style='color:#a7f3d0; font-family:\"JetBrains Mono\", monospace; font-size:14px; margin:0; line-height:1.5;'>{code}</pre>"
                f"</div>"
            )
        formatted = code_block_pattern.sub(replace_code_block, escaped)

        # Replace inline `code`
        inline_code_pattern = re.compile(r"`([^`]+)`")
        formatted = inline_code_pattern.sub(r"<code style='background-color:rgba(16,185,129,0.18); color:#00f59b; padding:3px 8px; border-radius:6px; font-family:monospace; font-size:14px;'>\1</code>", formatted)

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
                    background-color: rgba(7, 12, 18, 0.98);
                    border: 1.5px solid #10b981;
                    border-radius: 12px;
                    padding: 12px 16px;
                    margin-top: 10px;
                }
            """)
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(12, 10, 12, 10)
            c_layout.setSpacing(10)

            top = QHBoxLayout()
            c_title = QLabel("⚡ Proposed Linux System Command:")
            c_title.setStyleSheet("color: #00f59b; font-weight: 800; font-size: 13px;")
            top.addWidget(c_title)
            top.addStretch()
            c_layout.addLayout(top)

            cmd_text = QLabel(f"<code>{html.escape(cmd)}</code>")
            cmd_text.setStyleSheet("color: #fbbf24; font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: bold;")
            c_layout.addWidget(cmd_text)

            btn_row = QHBoxLayout()
            btn_row.addStretch()
            
            run_btn = QPushButton("⚡ Execute Command Now")
            run_btn.setObjectName("PrimaryButton")
            run_btn.setStyleSheet("padding: 8px 18px; font-size: 13px; border-radius: 10px;")
            run_btn.clicked.connect(lambda checked, c=cmd: self.run_command_requested.emit(c))
            btn_row.addWidget(run_btn)

            c_layout.addLayout(btn_row)
            self.cmd_container.addWidget(card)

    def _on_speak(self):
        speak(self.raw_content)

    def _on_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.raw_content)
        self.copy_btn.setText("✓")
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.copy_btn.setText("📋"))


class ChatWidget(QWidget):
    """
    Scrollable multi-turn chat stream container filling the workspace cleanly.
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
        self.messages_layout.setContentsMargins(24, 20, 24, 20)
        self.messages_layout.setSpacing(16)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)

    def add_user_message(self, text: str):
        card = MessageCard(role="user", content=text)
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()

    def start_assistant_message(self) -> MessageCard:
        card = MessageCard(role="assistant", content="")
        card.run_command_requested.connect(self.run_command_requested.emit)
        self.current_assistant_card = card
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()
        return card

    def append_assistant_token(self, token: str):
        if self.current_assistant_card:
            self.current_assistant_card.update_content(self.current_assistant_card.raw_content + token)
            self._scroll_to_bottom()

    def finalize_assistant_message(self, full_text: str):
        if self.current_assistant_card:
            self.current_assistant_card.update_content(full_text)
            self.current_assistant_card.finalize()
            self.current_assistant_card = None
            self._scroll_to_bottom()

    def add_assistant_message(self, text: str):
        card = MessageCard(role="assistant", content=text)
        card.run_command_requested.connect(self.run_command_requested.emit)
        card.finalize()
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
