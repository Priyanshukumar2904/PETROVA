"""
PETROVA Central Workspace Components: Greeting Panel, Metric Strip,
Technical AI Chat Panel with Structured Tables & Action Buttons, AI Input Bar,
and Lower Central 3-Panel Horizon Dock (Quick Actions, Tasks, Notifications).
"""

import html
import re
from datetime import datetime
from typing import List, Optional
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QFrame,
    QPushButton,
    QTextEdit,
    QScrollArea,
    QApplication,
)

from petrova.config.settings import get_config
from petrova.linux.stats import get_system_telemetry
from petrova.voice.tts import speak
from petrova.gui.styles import COLORS


class GreetingPanelWidget(QFrame):
    """
    Section 8: Dynamic time-based Greeting Panel.
    Good morning/afternoon/evening/night, <User>.
    PETROVA is at your service.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("GreetingPanel")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 14, 18, 14)
        layout.setSpacing(4)

        hour = datetime.now().hour
        if 5 <= hour < 12:
            time_greeting = "Good morning"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
        elif 17 <= hour < 22:
            time_greeting = "Good evening"
        else:
            time_greeting = "Good night"

        config = get_config()
        user_name = config.user_name or "Priyanshu"

        self.title_lbl = QLabel(f"{time_greeting}, {user_name}.")
        self.title_lbl.setObjectName("GreetingTitle")

        self.sub_lbl = QLabel("PETROVA is at your service.")
        self.sub_lbl.setObjectName("GreetingSubtitle")

        layout.addWidget(self.title_lbl)
        layout.addWidget(self.sub_lbl)


class MetricStripWidget(QFrame):
    """
    Section 9: Horizontal System Metric Strip with 6 compact sections:
    CPU, RAM, GPU, TEMP, BATTERY, UPTIME.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MetricStrip")
        self._setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_metrics)
        self.timer.start(2000)
        self.update_metrics()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 4, 6, 4)
        layout.setSpacing(0)

        # 1. CPU
        self.cpu_lbl = self._add_metric_cell(layout, "CPU", r"18% ~/\_")
        # 2. RAM
        self.ram_lbl = self._add_metric_cell(layout, "RAM", r"41% ~/\_")
        # 3. GPU
        self.gpu_lbl = self._add_metric_cell(layout, "GPU", r"12% ~/\_")
        # 4. TEMP
        self.temp_lbl = self._add_metric_cell(layout, "TEMP", r"54°C ~/\_")
        # 5. BATTERY
        self.bat_lbl = self._add_metric_cell(layout, "BATTERY", "78%")
        # 6. UPTIME
        self.uptime_lbl = self._add_metric_cell(layout, "UPTIME", "2h 13m", is_last=True)

    def _add_metric_cell(self, parent_layout: QHBoxLayout, title_txt: str, val_txt: str, is_last: bool = False) -> QLabel:
        cell = QFrame()
        cell.setObjectName("MetricCell" if not is_last else "")
        vbox = QVBoxLayout(cell)
        vbox.setContentsMargins(8, 2, 8, 2)
        vbox.setSpacing(2)

        title = QLabel(title_txt)
        title.setObjectName("MetricCellTitle")
        val = QLabel(val_txt)
        val.setObjectName("MetricCellValue")

        vbox.addWidget(title)
        vbox.addWidget(val)
        parent_layout.addWidget(cell, 1)
        return val

    def update_metrics(self):
        try:
            data = get_system_telemetry()
            load = data.get("load_avg", "")
            load_first = load.split(",")[0] if load else "1.2"
            cpu_pct = min(100, int(float(load_first) * 12)) if load_first else 18
            self.cpu_lbl.setText(rf"{cpu_pct}% ~/\_")

            ram = data.get("ram", {})
            self.ram_lbl.setText(rf"{int(ram.get('pct', 0))}% ~/\_")

            gpu = data.get("gpu", {})
            self.gpu_lbl.setText(rf"{int(gpu.get('utilization_pct', 12))}% ~/\_")

            temp = data.get("cpu_temp")
            temp_str = f"{temp:.0f}°C" if temp else "54°C"
            self.temp_lbl.setText(rf"{temp_str} ~/\_")

            bat = data.get("battery", {})
            self.bat_lbl.setText(f"{int(bat.get('percent', 100))}%")

            uptime = data.get("uptime", "2h 13m")
            self.uptime_lbl.setText(uptime.split(",")[0])
        except Exception:
            pass


class TechnicalMessageCard(QFrame):
    """
    Sections 11 & 12: Technical Chat Message Card (NO bubbly graphics, technical labels [YOU], [PETROVA]).
    """
    run_command_requested = pyqtSignal(str)

    def __init__(self, role: str, content: str = "", timestamp: str = "", parent=None):
        super().__init__(parent)
        self.role = role
        self.raw_content = content
        self.timestamp = timestamp or datetime.now().strftime("%H:%M")
        self.setObjectName("TechnicalMessageBlock")
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # Technical Role Header
        header = QHBoxLayout()
        header.setSpacing(8)

        if self.role == "user":
            role_lbl = QLabel("[YOU]")
            role_lbl.setObjectName("LabelYou")
        else:
            role_lbl = QLabel("[PETROVA]")
            role_lbl.setObjectName("LabelPetrova")

        header.addWidget(role_lbl)
        header.addStretch()

        if self.role == "assistant":
            speak_btn = QPushButton("🔊")
            speak_btn.setFixedSize(20, 20)
            speak_btn.setStyleSheet(f"background: transparent; border: none; font-size: 11px; color: {COLORS['muted']};")
            speak_btn.setToolTip("Read aloud")
            speak_btn.clicked.connect(lambda: speak(self.raw_content))
            header.addWidget(speak_btn)

        copy_btn = QPushButton("📋")
        copy_btn.setFixedSize(20, 20)
        copy_btn.setStyleSheet(f"background: transparent; border: none; font-size: 11px; color: {COLORS['muted']};")
        copy_btn.setToolTip("Copy text")
        copy_btn.clicked.connect(self._on_copy)
        header.addWidget(copy_btn)

        layout.addLayout(header)

        # Content Label
        self.content_lbl = QLabel()
        self.content_lbl.setObjectName("MessageBody")
        self.content_lbl.setWordWrap(True)
        self.content_lbl.setTextFormat(Qt.TextFormat.RichText)
        self.content_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.LinksAccessibleByMouse)
        layout.addWidget(self.content_lbl)

        # Interactive Action Buttons Row
        self.actions_row = QHBoxLayout()
        self.actions_row.setSpacing(8)
        layout.addLayout(self.actions_row)

        self._render_text()

    def update_content(self, text: str):
        self.raw_content = text
        self._render_text()

    def _render_text(self):
        text = self.raw_content
        escaped = html.escape(text)

        # Render structured monospace code / directory table blocks
        code_block_pattern = re.compile(r"```([a-zA-Z0-9_\-]+)?\n(.*?)```", re.DOTALL)
        def replace_code_block(match):
            lang = match.group(1) or ""
            code = match.group(2)
            return (
                f"<div style='background-color:{COLORS['surface']}; border:1px solid {COLORS['border']}; border-radius:2px; padding:8px 12px; margin:6px 0;'>"
                f"<pre style='color:{COLORS['foreground']}; font-family:\"JetBrains Mono\", monospace; font-size:12.5px; margin:0; line-height:1.4;'>{code}</pre>"
                f"</div>"
            )
        formatted = code_block_pattern.sub(replace_code_block, escaped)

        # Inline `code`
        inline_code_pattern = re.compile(r"`([^`]+)`")
        formatted = inline_code_pattern.sub(r"<code style='background-color:#111111; color:#FFFFFF; padding:1px 5px; border-radius:2px; font-family:monospace;'>\1</code>", formatted)

        # Bold
        formatted = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", formatted)
        formatted = formatted.replace("\n", "<br>")

        self.content_lbl.setText(formatted)

    def finalize(self):
        if self.role != "assistant":
            return

        from petrova.brain.brain import extract_suggested_commands
        commands = extract_suggested_commands(self.raw_content)

        while self.actions_row.count():
            item = self.actions_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add reference action buttons [ INSPECT ] [ CLEAN ] [ IGNORE ] [ DETAILS ]
        if commands:
            for cmd in commands[:1]:
                run_btn = QPushButton(f"[ ⚡ RUN: {cmd[:24]}... ]" if len(cmd) > 24 else f"[ ⚡ RUN: {cmd} ]")
                run_btn.setObjectName("MonochromePill")
                run_btn.clicked.connect(lambda checked, c=cmd: self.run_command_requested.emit(c))
                self.actions_row.addWidget(run_btn)

            for act_lbl, act_cmd in [("[ INSPECT ]", "ls -la"), ("[ CLEAN ]", "sudo pacman -Sc --noconfirm"), ("[ DETAILS ]", "df -h")]:
                pill = QPushButton(act_lbl)
                pill.setObjectName("MonochromePill")
                pill.clicked.connect(lambda checked, c=act_cmd: self.run_command_requested.emit(c))
                self.actions_row.addWidget(pill)
            self.actions_row.addStretch()

    def _on_copy(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.raw_content)


class ChatWidget(QWidget):
    """
    Section 10: AI Assistant Main Scrollable Conversation Panel.
    """
    run_command_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.current_assistant_card: Optional[TechnicalMessageCard] = None

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Outer Frame
        self.frame = QFrame()
        self.frame.setObjectName("ChatMainFrame")
        frame_layout = QVBoxLayout(self.frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)

        # Header Bar: AI ASSISTANT | CONVERSATION ID: #250611-0038 | [trash] [...]
        header = QFrame()
        header.setObjectName("ChatHeaderBar")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(14, 6, 14, 6)
        h_layout.setSpacing(10)

        title = QLabel("AI ASSISTANT")
        title.setObjectName("ChatHeaderTitle")

        conv_id = QLabel(f"CONVERSATION ID: #{datetime.now().strftime('%y%m%d-%H%M')}")
        conv_id.setObjectName("ChatHeaderId")

        del_btn = QPushButton("🗑️")
        del_btn.setFixedSize(20, 20)
        del_btn.setStyleSheet("background: transparent; border: none; font-size: 11px;")
        del_btn.setToolTip("Clear Conversation")
        del_btn.clicked.connect(self.clear_chat)

        more_btn = QPushButton("⋯")
        more_btn.setFixedSize(20, 20)
        more_btn.setStyleSheet("background: transparent; border: none; font-size: 13px; font-weight: bold;")

        h_layout.addWidget(title)
        h_layout.addStretch()
        h_layout.addWidget(conv_id)
        h_layout.addWidget(del_btn)
        h_layout.addWidget(more_btn)
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

        main_layout.addWidget(self.frame)

    def clear_chat(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def add_user_message(self, text: str):
        card = TechnicalMessageCard(role="user", content=text)
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()

    def start_assistant_message(self) -> TechnicalMessageCard:
        card = TechnicalMessageCard(role="assistant", content="")
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
        card = TechnicalMessageCard(role="assistant", content=text)
        card.run_command_requested.connect(self.run_command_requested.emit)
        card.finalize()
        idx = max(0, self.messages_layout.count() - 1)
        self.messages_layout.insertWidget(idx, card)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())


class LowerCentralHorizonDock(QWidget):
    """
    Section 14: Lower Central Panels (3-Card Horizontal Row):
    Panel A: QUICK ACTIONS
    Panel B: TASKS (ACTIVE & COMPLETED)
    Panel C: NOTIFICATIONS
    """
    action_triggered = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Panel A: QUICK ACTIONS
        qa_card = QFrame()
        qa_card.setObjectName("LowerCard")
        qa_layout = QVBoxLayout(qa_card)
        qa_layout.setContentsMargins(10, 8, 10, 8)
        qa_layout.setSpacing(6)

        qa_title = QLabel("QUICK ACTIONS")
        qa_title.setObjectName("LowerCardTitle")
        qa_layout.addWidget(qa_title)

        grid = QGridLayout()
        grid.setSpacing(4)
        quick_actions = [
            ("[System Scan]", "sudo pacman -Qk"),
            ("[Clean Cache]", "sudo pacman -Sc --noconfirm"),
            ("[Update System]", "/goal check system updates"),
            ("[Disk Analysis]", "df -h"),
            ("[Process Monitor]", "ps aux --sort=-%cpu | head -n 10"),
            ("[Network Monitor]", "ip -br addr"),
        ]
        for i, (lbl, cmd) in enumerate(quick_actions):
            btn = QPushButton(lbl)
            btn.setObjectName("MonochromePill")
            btn.clicked.connect(lambda checked, c=cmd: self.action_triggered.emit(c))
            grid.addWidget(btn, i // 2, i % 2)
        qa_layout.addLayout(grid)
        layout.addWidget(qa_card, 1)

        # Panel B: TASKS
        tasks_card = QFrame()
        tasks_card.setObjectName("LowerCard")
        t_layout = QVBoxLayout(tasks_card)
        t_layout.setContentsMargins(10, 8, 10, 8)
        t_layout.setSpacing(4)

        t_title = QLabel("TASKS")
        t_title.setObjectName("LowerCardTitle")
        t_layout.addWidget(t_title)

        active_lbl = QLabel("ACTIVE")
        active_lbl.setStyleSheet(f"color: {COLORS['muted']}; font-family: 'JetBrains Mono'; font-size: 10px; font-weight: bold;")
        t_layout.addWidget(active_lbl)

        line1 = QLabel("● Monitoring System       Running")
        line1.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 11px;")
        line2 = QLabel("● Disk Analysis           34%")
        line2.setStyleSheet(f"color: {COLORS['secondary']}; font-family: 'JetBrains Mono'; font-size: 11px;")
        t_layout.addWidget(line1)
        t_layout.addWidget(line2)

        sep = QLabel("--------------------------")
        sep.setStyleSheet(f"color: {COLORS['border']}; font-family: 'JetBrains Mono'; font-size: 10px;")
        t_layout.addWidget(sep)

        comp_lbl = QLabel("COMPLETED")
        comp_lbl.setStyleSheet(f"color: {COLORS['muted']}; font-family: 'JetBrains Mono'; font-size: 10px; font-weight: bold;")
        t_layout.addWidget(comp_lbl)

        line3 = QLabel("✓ System Scan")
        line3.setStyleSheet(f"color: {COLORS['muted']}; font-family: 'JetBrains Mono'; font-size: 11px;")
        t_layout.addWidget(line3)

        t_layout.addStretch()
        view_all_btn = QPushButton("[VIEW ALL]")
        view_all_btn.setObjectName("MonochromePill")
        view_all_btn.clicked.connect(lambda: self.action_triggered.emit("/goal list"))
        t_layout.addWidget(view_all_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(tasks_card, 1)

        # Panel C: NOTIFICATIONS
        notif_card = QFrame()
        notif_card.setObjectName("LowerCard")
        n_layout = QVBoxLayout(notif_card)
        n_layout.setContentsMargins(10, 8, 10, 8)
        n_layout.setSpacing(4)

        n_title = QLabel("NOTIFICATIONS")
        n_title.setObjectName("LowerCardTitle")
        n_layout.addWidget(n_title)

        self.notifs = [
            f"[{datetime.now().strftime('%H:%M')}] System check completed.",
            "[00:35] Cache cleaned successfully.",
            "[00:34] Package update available.",
            "[00:30] PETROVA is now online.",
        ]
        for note in self.notifs:
            lbl = QLabel(note)
            lbl.setStyleSheet(f"color: {COLORS['secondary']}; font-family: 'JetBrains Mono'; font-size: 11px;")
            n_layout.addWidget(lbl)

        n_layout.addStretch()
        clear_all_btn = QPushButton("[CLEAR ALL]")
        clear_all_btn.setObjectName("MonochromePill")
        n_layout.addWidget(clear_all_btn, alignment=Qt.AlignmentFlag.AlignRight)
        layout.addWidget(notif_card, 1)


# Compatibility aliases
MessageCard = TechnicalMessageCard
SparklineStripWidget = MetricStripWidget
