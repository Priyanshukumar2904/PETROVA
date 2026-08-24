"""
PETROVA Center Chat View, Greeting Card, Sparkline HUD Strip, and Action Pill Cards.
Matches the exact reference mockup layout and design specifications.
"""

import html
import re
from datetime import datetime
from typing import List, Optional
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
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
from petrova.linux.stats import get_system_telemetry


class SparklineStripWidget(QFrame):
    """6-Metric horizontal quick sparkline strip from the reference mockup."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("SparklineBar")
        self._setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(2000)
        self.update_metrics()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(6)

        # 1. CPU
        self.cpu_lbl = self._add_chip(layout, "🖥️ CPU", r"18% ~/\_")
        # 2. RAM
        self.ram_lbl = self._add_chip(layout, "🧠 RAM", r"41% ~/\_")
        # 3. GPU
        self.gpu_lbl = self._add_chip(layout, "🎮 GPU", r"12% ~/\_")
        # 4. TEMP
        self.temp_lbl = self._add_chip(layout, "🌡️ TEMP", r"54°C ~/\_")
        # 5. BATTERY
        self.bat_lbl = self._add_chip(layout, "🔋 BATTERY", "100%")
        # 6. UPTIME
        self.uptime_lbl = self._add_chip(layout, "⏱️ UPTIME", "4h 52m", last=True)

    def _add_chip(self, parent_layout, label_txt: str, init_val: str, last: bool = False) -> QLabel:
        chip = QFrame()
        chip.setObjectName("SparklineChip" if not last else "")
        vbox = QVBoxLayout(chip)
        vbox.setContentsMargins(6, 2, 6, 2)
        vbox.setSpacing(1)

        lbl = QLabel(label_txt)
        lbl.setObjectName("SparkChipLabel")
        val = QLabel(init_val)
        val.setObjectName("SparkChipValue")

        vbox.addWidget(lbl)
        vbox.addWidget(val)
        parent_layout.addWidget(chip)
        return val

    def update_metrics(self):
        try:
            data = get_system_telemetry()
            
            # CPU
            load = data.get("load_avg", "")
            load_first = load.split(",")[0] if load else "1.2"
            cpu_pct = min(100, int(float(load_first) * 12)) if load_first else 18
            self.cpu_lbl.setText(f"{cpu_pct}% ∿")

            # RAM
            ram = data.get("ram", {})
            self.ram_lbl.setText(f"{int(ram.get('pct', 0))}% ∿")

            # TEMP
            temp = data.get("cpu_temp")
            temp_str = f"{temp:.0f}°C" if temp else "50°C"
            self.temp_lbl.setText(f"{temp_str} ∿")

            # BATTERY
            bat = data.get("battery", {})
            bat_pct = int(bat.get("percent", 100))
            self.bat_lbl.setText(f"{bat_pct}%")

            # UPTIME
            uptime = data.get("uptime", "5h 12m")
            self.uptime_lbl.setText(uptime.split(",")[0])
        except Exception:
            pass


class MessageCard(QFrame):
    """A single chat message card (User or Petrova) matching the reference mockup."""
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

        header = QHBoxLayout()
        header.setSpacing(8)

        if self.role == "user":
            self.setObjectName("UserCard")
            role_lbl = QLabel("YOU")
            role_lbl.setObjectName("RoleBadgeYou")
        else:
            self.setObjectName("AssistantCard")
            role_lbl = QLabel("PETROVA")
            role_lbl.setObjectName("RoleBadgePetrova")

        time_lbl = QLabel(self.timestamp)
        time_lbl.setStyleSheet("color: #64748b; font-family: 'JetBrains Mono', monospace; font-size: 11px;")

        header.addWidget(role_lbl)
        header.addWidget(time_lbl)
        header.addStretch()

        if self.role == "assistant":
            self.speak_btn = QPushButton("🔊")
            self.speak_btn.setFixedSize(22, 22)
            self.speak_btn.setStyleSheet("padding: 0; font-size: 11px; background: transparent; border: none; color: #64748b;")
            self.speak_btn.setToolTip("Read Response Aloud")
            self.speak_btn.clicked.connect(self._on_speak)
            header.addWidget(self.speak_btn)

        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(22, 22)
        self.copy_btn.setStyleSheet("padding: 0; font-size: 11px; background: transparent; border: none; color: #64748b;")
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

        # Container for interactive command action cards & action buttons
        self.actions_container = QHBoxLayout()
        self.actions_container.setSpacing(8)
        layout.addLayout(self.actions_container)

        self._render_text()

    def update_content(self, text: str):
        self.raw_content = text
        self._render_text()

    def _render_text(self):
        text = self.raw_content
        escaped = html.escape(text)

        # Replace markdown code blocks ```bash ... ```
        code_block_pattern = re.compile(r"```([a-zA-Z0-9_\-]+)?\n(.*?)```", re.DOTALL)
        def replace_code_block(match):
            lang = match.group(1) or "code"
            code = match.group(2)
            return (
                f"<div style='background-color:#05080c; border:1px solid #16202c; border-radius:6px; padding:10px; margin:8px 0;'>"
                f"<div style='color:#00f59b; font-family:monospace; font-size:10.5px; font-weight:bold; letter-spacing:1px; margin-bottom:4px;'>{lang.upper()}</div>"
                f"<pre style='color:#cbd5e1; font-family:\"JetBrains Mono\", monospace; font-size:13px; margin:0; line-height:1.4;'>{code}</pre>"
                f"</div>"
            )
        formatted = code_block_pattern.sub(replace_code_block, escaped)

        # Replace inline `code`
        inline_code_pattern = re.compile(r"`([^`]+)`")
        formatted = inline_code_pattern.sub(r"<code style='background-color:#0d151f; color:#00f59b; padding:2px 6px; border-radius:4px; font-family:monospace; font-size:13px;'>\1</code>", formatted)

        # Bold **text**
        formatted = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", formatted)

        # Convert newlines to breaks
        formatted = formatted.replace("\n", "<br>")

        self.content_lbl.setText(formatted)

    def finalize(self):
        if self.role != "assistant":
            return

        from petrova.brain.brain import extract_suggested_commands
        commands = extract_suggested_commands(self.raw_content)

        # Clear existing action pills
        while self.actions_container.count():
            item = self.actions_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add reference mockup action buttons: [ INSPECT ] [ CLEAN ] [ IGNORE ] [ DETAILS ]
        if commands:
            for cmd in commands[:1]:
                run_btn = QPushButton(f"[ ⚡ RUN: {cmd[:25]}... ]" if len(cmd) > 25 else f"[ ⚡ RUN: {cmd} ]")
                run_btn.setObjectName("ActionPill")
                run_btn.clicked.connect(lambda checked, c=cmd: self.run_command_requested.emit(c))
                self.actions_container.addWidget(run_btn)

            for act_lbl, act_cmd in [("[ INSPECT ]", "ls -la"), ("[ DETAILS ]", "df -h")]:
                pill = QPushButton(act_lbl)
                pill.setObjectName("ActionPill")
                pill.clicked.connect(lambda checked, c=act_cmd: self.run_command_requested.emit(c))
                self.actions_container.addWidget(pill)
            
            self.actions_container.addStretch()

    def _on_speak(self):
        speak(self.raw_content)

    def _on_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.raw_content)
        self.copy_btn.setText("✓")
        QTimer.singleShot(1500, lambda: self.copy_btn.setText("📋"))


class ChatWidget(QWidget):
    """
    Center AI Assistant container matching the reference mockup.
    """
    run_command_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.current_assistant_card: Optional[MessageCard] = None

    def _setup_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        # Outer Frame with Cyber Border
        self.chat_frame = QFrame()
        self.chat_frame.setObjectName("ChatOuterFrame")
        frame_layout = QVBoxLayout(self.chat_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Chat Header
        header = QFrame()
        header.setObjectName("ChatHeader")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(12, 6, 12, 6)
        h_layout.setSpacing(10)

        title = QLabel("AI ASSISTANT")
        title.setObjectName("ChatHeaderTitle")

        conv_id = QLabel(f"CONVERSATION ID: #{datetime.now().strftime('%y%m%d-%H%M')}")
        conv_id.setObjectName("ChatHeaderId")

        clear_btn = QPushButton("🗑️")
        clear_btn.setFixedSize(22, 22)
        clear_btn.setStyleSheet("background: transparent; border: none; font-size: 11px;")
        clear_btn.setToolTip("Clear conversation stream")
        clear_btn.clicked.connect(self.clear_chat)

        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(conv_id)
        h_layout.addWidget(clear_btn)
        frame_layout.addWidget(header)

        # Scroll Area
        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("ChatScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        self.chat_container = QWidget()
        self.chat_container.setObjectName("ChatContentWidget")
        self.messages_layout = QVBoxLayout(self.chat_container)
        self.messages_layout.setContentsMargins(14, 12, 14, 12)
        self.messages_layout.setSpacing(10)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.chat_container)
        frame_layout.addWidget(self.scroll_area, 1)

        outer_layout.addWidget(self.chat_frame)

    def clear_chat(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

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
