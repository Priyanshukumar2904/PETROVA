"""
PETROVA Main Desktop Application Window.
Precision Cyber-HUD & Linux Terminal Operating Assistant layout matching the reference mockup.
"""

import sys
from datetime import datetime
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QIcon, QFont, QKeySequence, QShortcut
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QFrame,
    QApplication,
    QMessageBox,
)

from petrova.config.settings import get_config
from petrova.linux.stats import get_distro_info, get_cpu_temp, get_ram_usage, get_battery_status
from petrova.ui.greeting import get_greeting
from petrova.voice import speak, is_voice_enabled, set_voice_enabled
from petrova.voice.stt import listen_and_transcribe
from petrova.brain.brain import stream_ask
from petrova.tools.executor import execute_command

from petrova.gui.styles import SPARKLING_AMBER_GREEN_THEME
from petrova.gui.nav_sidebar import NavSidebarWidget
from petrova.gui.telemetry_widget import TelemetryDashboardWidget
from petrova.gui.chat_widget import ChatWidget, SparklineStripWidget
from petrova.gui.terminal_drawer import TerminalDrawerWidget
from petrova.gui.memory_dialog import MemoryVaultDialog
from petrova.gui.neural_canvas import NeuralVisualizerWidget, NeuralState


class InferenceWorker(QObject):
    """Asynchronous worker for streaming LLM responses without freezing the GUI."""
    token_received = pyqtSignal(str)
    thinking_phase = pyqtSignal(str)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, prompt: str):
        super().__init__()
        self.prompt = prompt

    def run(self):
        try:
            self.thinking_phase.emit("Analyzing query context & system state...")
            full_response = []
            
            for token in stream_ask(self.prompt):
                full_response.append(token)
                self.token_received.emit(token)

            complete_text = "".join(full_response)
            self.finished.emit(complete_text)
        except Exception as e:
            self.error_occurred.emit(str(e))


class VoiceWorker(QObject):
    """Worker for microphone speech recognition."""
    transcription_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            text = listen_and_transcribe()
            if text:
                self.transcription_ready.emit(text)
            else:
                self.transcription_ready.emit("")
        except Exception as e:
            self.error_occurred.emit(str(e))


class PetrovaMainWindow(QMainWindow):
    """
    Main Modern Desktop Application Window matching the reference mockup.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PETROVA // Personal Enhanced Terminal Reasoning & Operations Virtual Assistant")
        self.resize(1280, 820)
        self.setMinimumSize(1000, 680)
        self.setStyleSheet(SPARKLING_AMBER_GREEN_THEME)

        self.inference_thread: QThread = None
        self.voice_thread: QThread = None
        self.is_listening = False

        self._setup_ui()
        self._setup_shortcuts()
        self._show_initial_greeting()

        # Real-time clock timer
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Title Bar
        self.title_bar = QFrame()
        self.title_bar.setObjectName("TitleBar")
        tb_layout = QHBoxLayout(self.title_bar)
        tb_layout.setContentsMargins(14, 6, 14, 6)
        tb_layout.setSpacing(12)

        # Window Dot Badges
        dots_row = QHBoxLayout()
        dots_row.setSpacing(6)
        for c in ["#ef4444", "#f59e0b", "#10b981"]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color: {c}; font-size: 11px;")
            dots_row.addWidget(dot)
        tb_layout.addLayout(dots_row)

        tb_title = QLabel("PETROVA // Personal Enhanced Terminal Reasoning & Operations Virtual Assistant")
        tb_title.setObjectName("TitleText")
        tb_layout.addWidget(tb_title)

        tb_layout.addStretch()

        sec_badge = QLabel("🔒 LOCAL MODE • FULL PRIVACY")
        sec_badge.setObjectName("SecurityBadge")
        tb_layout.addWidget(sec_badge)

        sep = QLabel("|")
        sep.setStyleSheet("color: #334155;")
        tb_layout.addWidget(sep)

        self.clock_lbl = QLabel(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.clock_lbl.setObjectName("ClockLabel")
        tb_layout.addWidget(self.clock_lbl)

        root_layout.addWidget(self.title_bar)

        # 2. Main 3-Column Body Layout
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(8, 8, 8, 8)
        body_layout.setSpacing(8)

        # Column 1: Left Navigation Sidebar
        self.nav_sidebar = NavSidebarWidget(self)
        self.nav_sidebar.nav_changed.connect(self._on_nav_tab_changed)
        body_layout.addWidget(self.nav_sidebar)

        # Column 2: Center Workspace (Greeting + Sparklines + AI Assistant + Dock)
        center_col = QWidget()
        center_layout = QVBoxLayout(center_col)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        # Top Greeting Card
        greeting_card = QFrame()
        greeting_card.setObjectName("GreetingCard")
        gc_layout = QVBoxLayout(greeting_card)
        gc_layout.setContentsMargins(14, 10, 14, 10)
        gc_layout.setSpacing(2)

        config = get_config()
        user_name = config.user_name or "Priyanshu"

        self.greeting_title = QLabel(f"Good evening, {user_name}.")
        self.greeting_title.setObjectName("GreetingTitle")
        
        greeting_sub = QLabel("PETROVA is at your service.")
        greeting_sub.setObjectName("GreetingSub")

        gc_layout.addWidget(self.greeting_title)
        gc_layout.addWidget(greeting_sub)
        center_layout.addWidget(greeting_card)

        # 6-Metric Sparkline Strip
        self.sparklines = SparklineStripWidget(self)
        center_layout.addWidget(self.sparklines)

        # Main AI Chat View
        self.chat_widget = ChatWidget(self)
        self.chat_widget.run_command_requested.connect(self._execute_proposed_command)
        center_layout.addWidget(self.chat_widget, 1)

        # Embedded Terminal Drawer (Slide-up)
        self.terminal_drawer = TerminalDrawerWidget(self)
        self.terminal_drawer.close_btn.clicked.connect(lambda: self.terminal_drawer.setVisible(False))
        self.terminal_drawer.command_executed.connect(self._on_terminal_command_done)
        self.terminal_drawer.setVisible(False)
        self.terminal_drawer.setFixedHeight(210)
        center_layout.addWidget(self.terminal_drawer)

        # Prompt Input Frame
        self.input_frame = QFrame()
        self.input_frame.setObjectName("InputFrame")
        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(10, 6, 10, 6)
        input_layout.setSpacing(8)

        self.prompt_input = QTextEdit()
        self.prompt_input.setObjectName("PromptInput")
        self.prompt_input.setPlaceholderText("Ask PETROVA anything...")
        self.prompt_input.setFixedHeight(38)
        self.prompt_input.installEventFilter(self)
        input_layout.addWidget(self.prompt_input, 1)

        self.mic_btn = QPushButton("🎙️")
        self.mic_btn.setObjectName("MicBtn")
        self.mic_btn.setToolTip("Click to Speak")
        self.mic_btn.clicked.connect(self._toggle_mic_listen)
        input_layout.addWidget(self.mic_btn)

        self.send_btn = QPushButton("➤")
        self.send_btn.setObjectName("SendBtn")
        self.send_btn.setToolTip("Send Prompt (Enter)")
        self.send_btn.clicked.connect(self._on_submit_prompt)
        input_layout.addWidget(self.send_btn)

        center_layout.addWidget(self.input_frame)

        # Bottom Horizon 3-Card Dock
        bottom_dock = QHBoxLayout()
        bottom_dock.setSpacing(8)

        # Card 1: Quick Actions
        qa_card = QFrame()
        qa_card.setObjectName("BottomDockCard")
        qa_layout = QVBoxLayout(qa_card)
        qa_layout.setContentsMargins(8, 6, 8, 6)
        qa_layout.setSpacing(4)
        qa_title = QLabel("QUICK ACTIONS")
        qa_title.setObjectName("BottomDockTitle")
        qa_layout.addWidget(qa_title)
        
        qa_btns = QHBoxLayout()
        qa_btns.setSpacing(4)
        for lbl, prompt_t in [("⚡ Thermals", "Check CPU temperature"), ("💾 Clean Cache", "sudo pacman -Sc --noconfirm"), ("🎯 Update", "/goal check system updates")]:
            btn = QPushButton(lbl)
            btn.setObjectName("ActionPill")
            btn.clicked.connect(lambda checked, p=prompt_t: self._submit_chip_prompt(p))
            qa_btns.addWidget(btn)
        qa_layout.addLayout(qa_btns)
        bottom_dock.addWidget(qa_card, 1)

        # Card 2: Tasks
        tasks_card = QFrame()
        tasks_card.setObjectName("BottomDockCard")
        t_layout = QVBoxLayout(tasks_card)
        t_layout.setContentsMargins(8, 6, 8, 6)
        t_layout.setSpacing(4)
        t_title = QLabel("TASKS")
        t_title.setObjectName("BottomDockTitle")
        t_layout.addWidget(t_title)
        t_status = QLabel("ACTIVE: 0 background tasks")
        t_status.setStyleSheet("color: #94a3b8; font-family: 'JetBrains Mono', monospace; font-size: 11px;")
        t_layout.addWidget(t_status)
        bottom_dock.addWidget(tasks_card, 1)

        # Card 3: Notifications
        notif_card = QFrame()
        notif_card.setObjectName("BottomDockCard")
        n_layout = QVBoxLayout(notif_card)
        n_layout.setContentsMargins(8, 6, 8, 6)
        n_layout.setSpacing(4)
        n_title = QLabel("NOTIFICATIONS")
        n_title.setObjectName("BottomDockTitle")
        n_layout.addWidget(n_title)
        n_status = QLabel(f"[{datetime.now().strftime('%H:%M')}] System check completed.")
        n_status.setStyleSheet("color: #00f59b; font-family: 'JetBrains Mono', monospace; font-size: 11px;")
        n_layout.addWidget(n_status)
        bottom_dock.addWidget(notif_card, 1)

        center_layout.addLayout(bottom_dock)

        body_layout.addWidget(center_col, 1)

        # Column 3: Right System Overview Sidebar
        self.telemetry_sidebar = TelemetryDashboardWidget(self)
        body_layout.addWidget(self.telemetry_sidebar)

        root_layout.addWidget(body, 1)

        # Neural visualizer instance for tests/token handling
        self.neural_canvas = NeuralVisualizerWidget(self)
        self.neural_canvas.setVisible(False)

    def _update_clock(self):
        self.clock_lbl.setText(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))

    def _setup_shortcuts(self):
        # Keyboard Shortcuts matching left panel
        QShortcut(QKeySequence("H"), self, lambda: self.nav_sidebar._set_active_tab("HOME"))
        QShortcut(QKeySequence("A"), self, lambda: self.nav_sidebar._set_active_tab("AI_CHAT"))
        QShortcut(QKeySequence("S"), self, lambda: self.nav_sidebar._set_active_tab("SYSTEM"))
        QShortcut(QKeySequence("F"), self, lambda: self.nav_sidebar._set_active_tab("FILES"))
        QShortcut(QKeySequence("T"), self, self._toggle_terminal_drawer)
        QShortcut(QKeySequence("G"), self, self._open_memory_vault)
        QShortcut(QKeySequence("Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+T"), self, self._toggle_terminal_drawer)
        QShortcut(QKeySequence("Ctrl+M"), self, self._open_memory_vault)

    def _on_nav_tab_changed(self, tab: str):
        if tab == "AI_CHAT":
            self.prompt_input.setFocus()
        elif tab == "SYSTEM":
            self.telemetry_sidebar.update_telemetry()
        elif tab == "FILES":
            self._submit_chip_prompt("What's using my storage? Show top 5 largest directories in tabular format.")
        elif tab == "TASKS":
            self._submit_chip_prompt("/goal show active tasks")
        elif tab == "SETTINGS":
            self._open_memory_vault()

    def _show_initial_greeting(self):
        welcome_msg = (
            "I've initialized the system environment and analyzed hardware telemetry.\n\n"
            "You can ask me questions, inspect disk storage, plan multi-step goals (`/goal`), "
            "or use the **Terminal Drawer** anytime (`Ctrl+T`)."
        )
        self.chat_widget.add_assistant_message(welcome_msg)

    def _submit_chip_prompt(self, text: str):
        self.prompt_input.setPlainText(text)
        self._on_submit_prompt()

    def eventFilter(self, obj, event):
        if obj == self.prompt_input and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                    self._on_submit_prompt()
                    return True
        return super().eventFilter(obj, event)

    def _on_submit_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.prompt_input.clear()
        self.chat_widget.add_user_message(prompt)

        # Start streaming assistant card
        self.chat_widget.start_assistant_message()

        self.inference_thread = QThread()
        self.inference_worker = InferenceWorker(prompt)
        self.inference_worker.moveToThread(self.inference_thread)

        self.inference_thread.started.connect(self.inference_worker.run)
        self.inference_worker.token_received.connect(self._on_token_received)
        self.inference_worker.finished.connect(self._on_inference_finished)
        self.inference_worker.error_occurred.connect(self._on_inference_error)

        self.inference_thread.start()

    def _on_token_received(self, token: str):
        self.chat_widget.append_assistant_token(token)
        self.neural_canvas.fire_token_pulse()

    def _on_inference_finished(self, full_response: str):
        self.chat_widget.finalize_assistant_message(full_response)

        if is_voice_enabled() and full_response:
            speak(full_response)

        if self.inference_thread and self.inference_thread.isRunning():
            self.inference_thread.quit()
            self.inference_thread.wait()

    def _on_inference_error(self, error: str):
        self.chat_widget.append_assistant_token(f"\n\n**Error:** `{error}`")
        self.chat_widget.finalize_assistant_message(f"Error: {error}")

    def _toggle_mic_listen(self):
        if self.is_listening:
            return

        self.is_listening = True
        self.mic_btn.setStyleSheet("color: #ef4444; border-color: #ef4444;")

        self.voice_thread = QThread()
        self.voice_worker = VoiceWorker()
        self.voice_worker.moveToThread(self.voice_thread)

        self.voice_thread.started.connect(self.voice_worker.run)
        self.voice_worker.transcription_ready.connect(self._on_voice_transcribed)
        self.voice_worker.error_occurred.connect(lambda e: self._on_voice_transcribed(""))

        self.voice_thread.start()

    def _on_voice_transcribed(self, text: str):
        self.is_listening = False
        self.mic_btn.setStyleSheet("")

        if text.strip():
            self.prompt_input.setPlainText(text)
            self._on_submit_prompt()

        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.quit()
            self.voice_thread.wait()

    def _execute_proposed_command(self, cmd: str):
        self.terminal_drawer.setVisible(True)
        self.terminal_drawer.append_output(f"\n[Executing]: {cmd}\n")
        
        def run():
            code, stdout, stderr = execute_command(cmd)
            out = stdout if stdout else ""
            if stderr:
                out += f"\n[stderr]: {stderr}"
            self.terminal_drawer.append_output(f"{out}\n[Exit code: {code}]\n")

        import threading
        threading.Thread(target=run, daemon=True).start()

    def _on_terminal_command_done(self, cmd: str, output: str, code: int):
        self.terminal_drawer.append_output(f"{output}\n")

    def _toggle_terminal_drawer(self):
        visible = not self.terminal_drawer.isVisible()
        self.terminal_drawer.setVisible(visible)
        if visible:
            self.terminal_drawer.input_field.setFocus()

    def _open_memory_vault(self):
        dlg = MemoryVaultDialog(self)
        dlg.exec()
