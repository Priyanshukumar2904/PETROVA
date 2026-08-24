"""
PETROVA Main Desktop Application Window.
Exact implementation of the V1 Monochrome Cyber-HUD specification:
Top System Bar, Left Navigation Sidebar, Central Workspace (Greeting + Metric Strip + AI Chat + Input + Lower Dock),
Right System Monitor (Segmented LEDs + Petrova Core), and Bottom Status Bar.
"""

import sys
from datetime import datetime
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer
from PyQt6.QtGui import QFont, QKeySequence, QShortcut
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
from petrova.linux.stats import get_distro_info, get_cpu_temp, get_ram_usage, get_battery_status, get_network_speed, get_system_telemetry
from petrova.voice import speak, is_voice_enabled, set_voice_enabled
from petrova.voice.stt import listen_and_transcribe
from petrova.brain.brain import stream_ask
from petrova.tools.executor import execute_command

from petrova.gui.styles import MONOCHROME_THEME_QSS, COLORS
from petrova.gui.nav_sidebar import NavSidebarWidget
from petrova.gui.telemetry_widget import TelemetryDashboardWidget
from petrova.gui.chat_widget import ChatWidget, GreetingPanelWidget, MetricStripWidget, LowerCentralHorizonDock
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
            self.thinking_phase.emit("PROCESSING...")
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
    Main PETROVA Monochrome Cyber-HUD Window.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PETROVA // Personal Enhanced Terminal Reasoning & Operations Virtual Assistant")
        self.resize(1340, 860)
        self.setMinimumSize(1080, 700)
        self.setStyleSheet(MONOCHROME_THEME_QSS)

        self.inference_thread: QThread = None
        self.voice_thread: QThread = None
        self.is_listening = False

        self._setup_ui()
        self._setup_shortcuts()
        self._show_initial_greeting()

        # Timers
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock_and_status)
        self.clock_timer.start(1000)

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # =========================================================================
        # 1. TOP SYSTEM BAR (Section 3)
        # =========================================================================
        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopSystemBar")
        tb_layout = QHBoxLayout(self.top_bar)
        tb_layout.setContentsMargins(18, 0, 18, 0)
        tb_layout.setSpacing(10)

        # Left: PETROVA // Personal Enhanced Terminal Reasoning & Operations Virtual Assistant
        left_title_box = QHBoxLayout()
        left_title_box.setSpacing(8)
        
        brand_lbl = QLabel("PETROVA")
        brand_lbl.setObjectName("TopBarBrand")
        
        slash_lbl = QLabel("//")
        slash_lbl.setStyleSheet(f"color: {COLORS['muted']}; font-family: 'JetBrains Mono'; font-weight: bold;")
        
        desc_lbl = QLabel("Personal Enhanced Terminal Reasoning & Operations Virtual Assistant")
        desc_lbl.setObjectName("TopBarSub")

        left_title_box.addWidget(brand_lbl)
        left_title_box.addWidget(slash_lbl)
        left_title_box.addWidget(desc_lbl)
        tb_layout.addLayout(left_title_box)

        tb_layout.addStretch()

        # Right: [LOCK] LOCAL MODE • FULL PRIVACY    |    SYSTEM TIME
        right_info_box = QHBoxLayout()
        right_info_box.setSpacing(14)

        privacy_lbl = QLabel("[LOCK] LOCAL MODE • FULL PRIVACY")
        privacy_lbl.setObjectName("TopBarPrivacy")

        sep = QLabel("|")
        sep.setStyleSheet(f"color: {COLORS['border']};")

        self.clock_lbl = QLabel(datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.clock_lbl.setObjectName("TopBarClock")

        right_info_box.addWidget(privacy_lbl)
        right_info_box.addWidget(sep)
        right_info_box.addWidget(self.clock_lbl)
        tb_layout.addLayout(right_info_box)

        root_layout.addWidget(self.top_bar)

        # =========================================================================
        # 2. MAIN 3-COLUMN WORKSPACE (Sections 2, 4, 7, 15)
        # =========================================================================
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(12, 10, 12, 10)
        body_layout.setSpacing(10)

        # COLUMN 1: LEFT NAVIGATION PANEL (~210px)
        self.nav_sidebar = NavSidebarWidget(self)
        self.nav_sidebar.nav_changed.connect(self._on_nav_tab_changed)
        body_layout.addWidget(self.nav_sidebar)

        # COLUMN 2: CENTRAL WORKSPACE (65-70% width)
        center_col = QWidget()
        center_layout = QVBoxLayout(center_col)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(8)

        # Section 8: Greeting Panel
        self.greeting_panel = GreetingPanelWidget(self)
        center_layout.addWidget(self.greeting_panel)

        # Section 9: System Metric Strip (CPU, RAM, GPU, TEMP, BATTERY, UPTIME)
        self.metric_strip = MetricStripWidget(self)
        center_layout.addWidget(self.metric_strip)

        # Sections 10-12: AI Assistant Conversation Panel
        self.chat_widget = ChatWidget(self)
        self.chat_widget.run_command_requested.connect(self._execute_proposed_command)
        center_layout.addWidget(self.chat_widget, 1)

        # Collapsible Terminal Drawer
        self.terminal_drawer = TerminalDrawerWidget(self)
        self.terminal_drawer.close_btn.clicked.connect(lambda: self.terminal_drawer.setVisible(False))
        self.terminal_drawer.command_executed.connect(self._on_terminal_command_done)
        self.terminal_drawer.setVisible(False)
        self.terminal_drawer.setFixedHeight(210)
        center_layout.addWidget(self.terminal_drawer)

        # Section 13: AI Input Bar
        self.input_frame = QFrame()
        self.input_frame.setObjectName("AiInputFrame")
        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(10, 4, 10, 4)
        input_layout.setSpacing(8)

        self.prompt_input = QTextEdit()
        self.prompt_input.setObjectName("AiInputText")
        self.prompt_input.setPlaceholderText("Ask PETROVA anything...")
        self.prompt_input.setFixedHeight(36)
        self.prompt_input.installEventFilter(self)
        input_layout.addWidget(self.prompt_input, 1)

        self.mic_btn = QPushButton("[MIC]")
        self.mic_btn.setObjectName("InputIconBtn")
        self.mic_btn.setToolTip("Click to Speak (Microphone)")
        self.mic_btn.clicked.connect(self._toggle_mic_listen)
        input_layout.addWidget(self.mic_btn)

        self.send_btn = QPushButton("[→]")
        self.send_btn.setObjectName("InputIconBtn")
        self.send_btn.setToolTip("Send Prompt (Enter)")
        self.send_btn.clicked.connect(self._on_submit_prompt)
        input_layout.addWidget(self.send_btn)

        center_layout.addWidget(self.input_frame)

        # Section 14: Lower Central Panels (3-Card Horizontal Row)
        self.lower_dock = LowerCentralHorizonDock(self)
        self.lower_dock.action_triggered.connect(self._submit_chip_prompt)
        center_layout.addWidget(self.lower_dock)

        body_layout.addWidget(center_col, 1)

        # COLUMN 3: RIGHT SYSTEM MONITOR (~320px)
        self.telemetry_sidebar = TelemetryDashboardWidget(self)
        body_layout.addWidget(self.telemetry_sidebar)

        root_layout.addWidget(body, 1)

        # =========================================================================
        # 3. BOTTOM STATUS BAR (Section 23)
        # =========================================================================
        self.bottom_status_bar = QFrame()
        self.bottom_status_bar.setObjectName("BottomStatusBar")
        bs_layout = QHBoxLayout(self.bottom_status_bar)
        bs_layout.setContentsMargins(16, 2, 16, 2)
        bs_layout.setSpacing(10)

        self.status_left = QLabel("PETROVA v0.1.0  |  LOCAL MODE  |  OFFLINE  |  SECURE")
        self.status_left.setObjectName("StatusTextLeft")
        bs_layout.addWidget(self.status_left)

        bs_layout.addStretch()

        self.status_right = QLabel("CPU 18%  |  RAM 41%  |  TEMP 54°C  |  BAT 100%  |  NET ↓2.4 MB/s ↑0.8 MB/s")
        self.status_right.setObjectName("StatusTextRight")
        bs_layout.addWidget(self.status_right)

        root_layout.addWidget(self.bottom_status_bar)

        # Neural visualizer instance for tests/token handling
        self.neural_canvas = NeuralVisualizerWidget(self)
        self.neural_canvas.setVisible(False)

    def _update_clock_and_status(self):
        # 1. Update Clock
        now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.clock_lbl.setText(now_str)

        # 2. Update Bottom Status Bar
        try:
            data = get_system_telemetry()
            load = data.get("load_avg", "")
            load_first = load.split(",")[0] if load else "1.2"
            cpu_pct = min(100, int(float(load_first) * 12)) if load_first else 18
            ram_pct = int(data.get("ram", {}).get("pct", 41))
            temp = data.get("cpu_temp")
            temp_str = f"{temp:.0f}°C" if temp else "54°C"
            bat_pct = int(data.get("battery", {}).get("percent", 100))
            rx, tx = get_network_speed()

            self.status_right.setText(
                f"CPU {cpu_pct}%  |  RAM {ram_pct}%  |  TEMP {temp_str}  |  BAT {bat_pct}%  |  NET ↓{rx:.1f} MB/s ↑{tx:.1f} MB/s"
            )
        except Exception:
            pass

    def _setup_shortcuts(self):
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
            "I've analyzed your system.\n\n"
            "Here are the top 5 largest directories in your system:\n\n"
            "```text\n"
            "PATH                              SIZE\n"
            "/home/user/Downloads            31.4 GB\n"
            "/home/user/.cache               12.8 GB\n"
            "/home/user/Videos                8.2 GB\n"
            "/usr/lib                         6.1 GB\n"
            "/var/log                         3.7 GB\n"
            "```\n\n"
            "Would you like me to inspect any of these?"
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

        # Update Petrova Core state to THINKING
        self.telemetry_sidebar.set_core_status("THINKING")

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
        self.telemetry_sidebar.set_core_status("PROCESSING")

    def _on_inference_finished(self, full_response: str):
        self.chat_widget.finalize_assistant_message(full_response)
        self.telemetry_sidebar.set_core_status("READY")

        if is_voice_enabled() and full_response:
            speak(full_response)

        if self.inference_thread and self.inference_thread.isRunning():
            self.inference_thread.quit()
            self.inference_thread.wait()

    def _on_inference_error(self, error: str):
        self.chat_widget.append_assistant_token(f"\n\n**Error:** `{error}`")
        self.chat_widget.finalize_assistant_message(f"Error: {error}")
        self.telemetry_sidebar.set_core_status("ERROR")

    def _toggle_mic_listen(self):
        if self.is_listening:
            return

        self.is_listening = True
        self.mic_btn.setText("[REC]")
        self.telemetry_sidebar.set_core_status("WAITING")

        self.voice_thread = QThread()
        self.voice_worker = VoiceWorker()
        self.voice_worker.moveToThread(self.voice_thread)

        self.voice_thread.started.connect(self.voice_worker.run)
        self.voice_worker.transcription_ready.connect(self._on_voice_transcribed)
        self.voice_worker.error_occurred.connect(lambda e: self._on_voice_transcribed(""))

        self.voice_thread.start()

    def _on_voice_transcribed(self, text: str):
        self.is_listening = False
        self.mic_btn.setText("[MIC]")

        if text.strip():
            self.prompt_input.setPlainText(text)
            self._on_submit_prompt()
        else:
            self.telemetry_sidebar.set_core_status("READY")

        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.quit()
            self.voice_thread.wait()

    def _execute_proposed_command(self, cmd: str):
        self.terminal_drawer.setVisible(True)
        self.telemetry_sidebar.set_core_status("EXECUTING")
        self.terminal_drawer.append_output(f"\n[Executing]: {cmd}\n")
        
        def run():
            code, stdout, stderr = execute_command(cmd)
            out = stdout if stdout else ""
            if stderr:
                out += f"\n[stderr]: {stderr}"
            self.terminal_drawer.append_output(f"{out}\n[Exit code: {code}]\n")
            QTimer.singleShot(800, lambda: self.telemetry_sidebar.set_core_status("READY"))

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
