"""
PETROVA Main Desktop Application Window.
Full implementation of the V1 Monochrome Cyber-HUD with multi-view navigation stack,
real-time streaming terminal drawer with interactive stdin piping (y/n confirmations),
active single-key shortcuts, secure sudo modal, and voice controls.
"""

import sys
import subprocess
from datetime import datetime
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QObject, QTimer, QEvent
from PyQt6.QtGui import QFont, QKeySequence, QShortcut, QKeyEvent
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QLineEdit,
    QInputDialog,
    QFrame,
    QStackedWidget,
    QApplication,
    QMessageBox,
)

from petrova.config.settings import get_config
from petrova.linux.stats import get_distro_info, get_cpu_temp, get_ram_usage, get_battery_status, get_network_speed, get_system_telemetry
from petrova.voice import speak, is_voice_enabled, set_voice_enabled
from petrova.voice.stt import listen_and_transcribe
from petrova.brain.brain import stream_ask
from petrova.tools.executor import get_execution_env, normalize_command

from petrova.gui.styles import MONOCHROME_THEME_QSS, COLORS
from petrova.gui.nav_sidebar import NavSidebarWidget
from petrova.gui.telemetry_widget import TelemetryDashboardWidget
from petrova.gui.chat_widget import ChatWidget, GreetingPanelWidget, MetricStripWidget, LowerCentralHorizonDock
from petrova.gui.system_view import SystemViewWidget
from petrova.gui.files_view import FilesViewWidget
from petrova.gui.tasks_view import TasksViewWidget
from petrova.gui.settings_view import SettingsViewWidget
from petrova.gui.terminal_drawer import TerminalDrawerWidget
from petrova.gui.memory_dialog import MemoryVaultDialog
from petrova.gui.notifications import notify
from petrova.gui.slash_handler import execute_gui_slash_command


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


class GoalWorker(QObject):
    """Worker for executing multi-step agentic goals."""
    finished = pyqtSignal(str)

    def __init__(self, objective: str):
        super().__init__()
        self.objective = objective

    def run(self):
        try:
            from petrova.brain.planner import plan_and_execute_goal
            res = plan_and_execute_goal(self.objective)
            self.finished.emit(res)
        except Exception as e:
            self.finished.emit(f"Goal execution error: {str(e)}")


class VoiceWorker(QObject):
    """Worker for microphone speech recognition."""
    transcription_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            text = listen_and_transcribe(duration=5)
            if text:
                self.transcription_ready.emit(text)
            else:
                self.transcription_ready.emit("")
        except Exception as e:
            self.error_occurred.emit(str(e))


class InteractiveCommandWorker(QObject):
    """
    Streaming command worker attached to a real Linux Pseudo-Terminal (PTY).
    Guarantees isatty(0) is True, streams output live, and supports interactive stdin writes (y/n, inputs).
    """
    output_line = pyqtSignal(str)
    finished = pyqtSignal(int)

    def __init__(self, cmd: str, sudo_password: str = None):
        super().__init__()
        self.raw_cmd = cmd
        self.sudo_password = sudo_password
        self.process: subprocess.Popen = None
        self.master_fd = None

    def run(self):
        import pty
        import os
        import select

        cmd = normalize_command(self.raw_cmd)
        env = get_execution_env()

        # If sudo password provided, pipe to sudo -S
        if self.sudo_password and "sudo " in cmd:
            cmd = cmd.replace("sudo ", f"echo '{self.sudo_password}' | sudo -S -p '' ")

        try:
            self.master_fd, slave_fd = pty.openpty()
            self.process = subprocess.Popen(
                cmd,
                shell=True,
                executable="/bin/bash",
                env=env,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True,
                start_new_session=True,
            )
            os.close(slave_fd)

            while True:
                if self.master_fd is None:
                    break
                r, _, _ = select.select([self.master_fd], [], [], 0.1)
                if r:
                    try:
                        data = os.read(self.master_fd, 2048)
                        if not data:
                            break
                        text = data.decode(errors="replace")
                        self.output_line.emit(text)
                    except OSError:
                        break

                if self.process.poll() is not None:
                    # Drain remaining buffer
                    try:
                        while self.master_fd is not None:
                            r, _, _ = select.select([self.master_fd], [], [], 0.05)
                            if not r:
                                break
                            data = os.read(self.master_fd, 2048)
                            if not data:
                                break
                            self.output_line.emit(data.decode(errors="replace"))
                    except Exception:
                        pass
                    break

            if self.master_fd is not None:
                try:
                    os.close(self.master_fd)
                except Exception:
                    pass
                self.master_fd = None

            self.process.wait()
            code = self.process.returncode
            self.finished.emit(code)
        except Exception as e:
            self.output_line.emit(f"\n[Execution error: {str(e)}]\n")
            self.finished.emit(1)

    def send_stdin(self, text: str):
        """Write user response into the real Linux PTY."""
        import os
        if self.master_fd is not None:
            try:
                os.write(self.master_fd, text.encode() + b"\n")
            except Exception:
                pass



class PetrovaMainWindow(QMainWindow):
    """
    Main PETROVA Monochrome Cyber-HUD Window.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PETROVA // Personal Enhanced Terminal Reasoning & Operations Virtual Assistant")
        self.resize(1360, 880)
        self.setMinimumSize(1100, 720)
        self.setStyleSheet(MONOCHROME_THEME_QSS)

        self.inference_thread: QThread = None
        self.voice_thread: QThread = None
        self.command_thread: QThread = None
        self.command_worker: InteractiveCommandWorker = None
        self.goal_thread: QThread = None
        self.is_listening = False
        self.cached_sudo_password: str = None

        self._setup_ui()
        self._setup_shortcuts()
        self._show_initial_greeting()

        # Dynamic clock & telemetry timer
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
        # 1. TOP SYSTEM BAR
        # =========================================================================
        self.top_bar = QFrame()
        self.top_bar.setObjectName("TopSystemBar")
        tb_layout = QHBoxLayout(self.top_bar)
        tb_layout.setContentsMargins(18, 0, 18, 0)
        tb_layout.setSpacing(12)

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

        right_info_box = QHBoxLayout()
        right_info_box.setSpacing(12)

        # Voice Output Toggle in Top Bar
        voice_on = is_voice_enabled()
        self.voice_toggle_top = QPushButton("🔊 Spoken Voice: ON" if voice_on else "🔇 Spoken Voice: OFF")
        self.voice_toggle_top.setObjectName("MonochromePill")
        self.voice_toggle_top.setToolTip("Toggle Spoken Audio Output")
        self.voice_toggle_top.clicked.connect(self._toggle_voice_output)
        right_info_box.addWidget(self.voice_toggle_top)

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
        # 2. MAIN 3-COLUMN WORKSPACE
        # =========================================================================
        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(12, 10, 12, 10)
        body_layout.setSpacing(10)

        # COLUMN 1: LEFT NAVIGATION PANEL (~210px)
        self.nav_sidebar = NavSidebarWidget(self)
        self.nav_sidebar.nav_changed.connect(self._on_nav_tab_changed)
        body_layout.addWidget(self.nav_sidebar)

        # COLUMN 2: CENTRAL WORKSPACE WITH STACKED VIEW
        self.central_stack = QStackedWidget()

        # VIEW 0: HOME (AI Command Center)
        home_view = QWidget()
        home_layout = QVBoxLayout(home_view)
        home_layout.setContentsMargins(0, 0, 0, 0)
        home_layout.setSpacing(8)

        self.greeting_panel = GreetingPanelWidget(self)
        home_layout.addWidget(self.greeting_panel)

        self.chat_widget = ChatWidget(self)
        self.chat_widget.run_command_requested.connect(self._execute_proposed_command)
        home_layout.addWidget(self.chat_widget, 1)

        # Collapsible Terminal Drawer with Interactive Stdin
        self.terminal_drawer = TerminalDrawerWidget(self)
        self.terminal_drawer.close_btn.clicked.connect(lambda: self.terminal_drawer.setVisible(False))
        self.terminal_drawer.command_submitted.connect(self._execute_proposed_command)
        self.terminal_drawer.stdin_submitted.connect(self._on_terminal_stdin_submitted)
        self.terminal_drawer.setVisible(False)
        self.terminal_drawer.setFixedHeight(210)
        home_layout.addWidget(self.terminal_drawer)

        # AI Input Bar
        self.input_frame = QFrame()
        self.input_frame.setObjectName("AiInputFrame")
        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(12, 6, 12, 6)
        input_layout.setSpacing(8)

        self.prompt_input = QTextEdit()
        self.prompt_input.setObjectName("AiInputText")
        self.prompt_input.setPlaceholderText("Ask PETROVA anything or enter command (e.g. /help, /stats, /goal)...")
        self.prompt_input.setFixedHeight(38)
        self.prompt_input.installEventFilter(self)
        input_layout.addWidget(self.prompt_input, 1)

        # Voice Output Toggle (Input bar)
        self.voice_toggle_bar = QPushButton("🔊 Voice: ON" if voice_on else "🔇 Voice: OFF")
        self.voice_toggle_bar.setObjectName("MonochromePill")
        self.voice_toggle_bar.setToolTip("Toggle Spoken Audio Feedback")
        self.voice_toggle_bar.clicked.connect(self._toggle_voice_output)
        input_layout.addWidget(self.voice_toggle_bar)

        # Microphone Button
        self.mic_btn = QPushButton("🎙️ Speak")
        self.mic_btn.setObjectName("MonochromePill")
        self.mic_btn.setToolTip("Click to Speak into Microphone")
        self.mic_btn.clicked.connect(self._toggle_mic_listen)
        input_layout.addWidget(self.mic_btn)

        # Send Button
        self.send_btn = QPushButton("➤ Send")
        self.send_btn.setObjectName("MonochromePill")
        self.send_btn.setToolTip("Send Prompt (Enter)")
        self.send_btn.clicked.connect(self._on_submit_prompt)
        input_layout.addWidget(self.send_btn)

        home_layout.addWidget(self.input_frame)

        # Lower Central Panels
        self.lower_dock = LowerCentralHorizonDock(self)
        self.lower_dock.action_triggered.connect(self._on_dock_action)
        home_layout.addWidget(self.lower_dock)

        self.central_stack.addWidget(home_view)  # Index 0: HOME

        # VIEW 1: SYSTEM Intelligence
        self.system_view = SystemViewWidget(self)
        self.system_view.execute_command_requested.connect(self._execute_proposed_command)
        self.central_stack.addWidget(self.system_view)  # Index 1: SYSTEM

        # VIEW 2: FILES & Storage Intelligence
        self.files_view = FilesViewWidget(self)
        self.files_view.execute_command_requested.connect(self._execute_proposed_command)
        self.central_stack.addWidget(self.files_view)  # Index 2: FILES

        # VIEW 3: TASKS & Goal Manager
        self.tasks_view = TasksViewWidget(self)
        self.tasks_view.execute_goal_requested.connect(self._submit_chip_prompt)
        self.central_stack.addWidget(self.tasks_view)  # Index 3: TASKS

        # VIEW 4: SETTINGS
        self.settings_view = SettingsViewWidget(self)
        self.settings_view.config_saved.connect(self._sync_voice_settings)
        self.central_stack.addWidget(self.settings_view)  # Index 4: SETTINGS

        body_layout.addWidget(self.central_stack, 1)

        # COLUMN 3: RIGHT SYSTEM MONITOR (~320px)
        self.telemetry_sidebar = TelemetryDashboardWidget(self)
        body_layout.addWidget(self.telemetry_sidebar)

        root_layout.addWidget(body, 1)

        # =========================================================================
        # 3. BOTTOM STATUS BAR
        # =========================================================================
        self.bottom_status_bar = QFrame()
        self.bottom_status_bar.setObjectName("BottomStatusBar")
        bs_layout = QHBoxLayout(self.bottom_status_bar)
        bs_layout.setContentsMargins(18, 2, 18, 2)
        bs_layout.setSpacing(10)

        self.status_left = QLabel("PETROVA v0.1.0  |  LOCAL MODE  |  OFFLINE  |  SECURE")
        self.status_left.setObjectName("StatusTextLeft")
        bs_layout.addWidget(self.status_left)

        bs_layout.addStretch()

        self.status_right = QLabel("CPU 18%  |  RAM 41%  |  TEMP 54°C  |  BAT 100%  |  NET ↓2.4 MB/s ↑0.8 MB/s")
        self.status_right.setObjectName("StatusTextRight")
        bs_layout.addWidget(self.status_right)

        root_layout.addWidget(self.bottom_status_bar)

    def _toggle_voice_output(self):
        new_state = not is_voice_enabled()
        set_voice_enabled(new_state)
        self._sync_voice_settings()
        msg = "Voice output ENABLED." if new_state else "Voice output MUTED."
        notify(msg, level="info")

    def _sync_voice_settings(self):
        state = is_voice_enabled()
        self.voice_toggle_top.setText("🔊 Spoken Voice: ON" if state else "🔇 Spoken Voice: OFF")
        self.voice_toggle_bar.setText("🔊 Voice: ON" if state else "🔇 Voice: OFF")

    def _update_clock_and_status(self):
        now_str = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        self.clock_lbl.setText(now_str)

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
        QShortcut(QKeySequence("Ctrl+H"), self, lambda: self.nav_sidebar._set_active_tab("HOME"))
        QShortcut(QKeySequence("Ctrl+A"), self, lambda: self.nav_sidebar._set_active_tab("AI_CHAT"))
        QShortcut(QKeySequence("Ctrl+S"), self, lambda: self.nav_sidebar._set_active_tab("SYSTEM"))
        QShortcut(QKeySequence("Ctrl+F"), self, lambda: self.nav_sidebar._set_active_tab("FILES"))
        QShortcut(QKeySequence("Ctrl+T"), self, lambda: self.nav_sidebar._set_active_tab("TASKS"))
        QShortcut(QKeySequence("Ctrl+G"), self, lambda: self.nav_sidebar._set_active_tab("SETTINGS"))
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)
        QShortcut(QKeySequence("Ctrl+`"), self, self._toggle_terminal_drawer)
        QShortcut(QKeySequence("Ctrl+M"), self, self._open_memory_vault)

    def keyPressEvent(self, event: QKeyEvent):
        focus_widget = QApplication.focusWidget()
        is_typing = isinstance(focus_widget, (QTextEdit, QLineEdit))

        if not is_typing:
            key = event.key()
            if key == Qt.Key.Key_H:
                self.nav_sidebar._set_active_tab("HOME")
                return
            elif key == Qt.Key.Key_A:
                self.nav_sidebar._set_active_tab("AI_CHAT")
                self.prompt_input.setFocus()
                return
            elif key == Qt.Key.Key_S:
                self.nav_sidebar._set_active_tab("SYSTEM")
                return
            elif key == Qt.Key.Key_F:
                self.nav_sidebar._set_active_tab("FILES")
                return
            elif key == Qt.Key.Key_T:
                self.nav_sidebar._set_active_tab("TASKS")
                return
            elif key == Qt.Key.Key_G:
                self.nav_sidebar._set_active_tab("SETTINGS")
                return
            elif key == Qt.Key.Key_Q:
                self.close()
                return
            elif key == Qt.Key.Key_Escape:
                if focus_widget:
                    focus_widget.clearFocus()
                return

        super().keyPressEvent(event)

    def _on_nav_tab_changed(self, tab: str):
        if tab in ("HOME", "AI_CHAT"):
            self.central_stack.setCurrentIndex(0)
            if tab == "AI_CHAT":
                self.prompt_input.setFocus()
        elif tab == "SYSTEM":
            self.system_view.refresh_data()
            self.central_stack.setCurrentIndex(1)
        elif tab == "FILES":
            self.files_view.refresh_storage()
            self.central_stack.setCurrentIndex(2)
        elif tab == "TASKS":
            self.central_stack.setCurrentIndex(3)
        elif tab == "SETTINGS":
            self.settings_view.load_settings()
            self.central_stack.setCurrentIndex(4)

    def _on_dock_action(self, action: str):
        if action == "__NAV_TASKS__":
            self.nav_sidebar._set_active_tab("TASKS")
        elif action.startswith("/"):
            self._submit_chip_prompt(action)
        else:
            self._execute_proposed_command(action)

    def _show_initial_greeting(self):
        config = get_config()
        user_name = config.user_name or "Cipher"
        welcome_msg = (
            f"**PETROVA Neural Core Online.** All telemetry streams, memory vaults, and terminal executors are ready.\n\n"
            f"How can I assist you today, **{user_name}**?\n"
            f"- Ask questions about your system or code\n"
            f"- Type `/help` to see built-in slash commands\n"
            f"- Click `🎙️ Speak` to give voice instructions"
        )
        self.chat_widget.add_assistant_message(welcome_msg)

    def _submit_chip_prompt(self, text: str):
        self.nav_sidebar._set_active_tab("HOME")
        self.prompt_input.setPlainText(text)
        self._on_submit_prompt()

    def eventFilter(self, obj, event):
        if obj == self.prompt_input and event.type() == event.Type.KeyPress:
            if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
                if not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                    self._on_submit_prompt()
                    return True
            elif event.key() == Qt.Key.Key_Escape:
                self.prompt_input.clearFocus()
                return True
        return super().eventFilter(obj, event)

    def _on_submit_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.prompt_input.clear()

        # If a background terminal command is currently running and asking for input:
        if self.command_worker and self.terminal_drawer.is_busy:
            self.terminal_drawer.append_output(f"{prompt}\n")
            self.command_worker.send_stdin(prompt)
            return

        self.chat_widget.add_user_message(prompt)

        # 1. Check if input is a built-in slash command
        is_slash, response_md = execute_gui_slash_command(prompt)
        if is_slash:
            if response_md == "__CLEAR_CHAT__":
                self.chat_widget.clear_chat()
                self.terminal_drawer.output.clear()
                return
            elif response_md == "__TRIGGER_MIC__":
                self._toggle_mic_listen()
                return
            elif response_md == "__EXIT_APP__":
                self.close()
                return
            elif response_md.startswith("__RUN_CMD__"):
                cmd = response_md.replace("__RUN_CMD__", "")
                self._execute_proposed_command(cmd)
                return
            elif response_md.startswith("__RUN_GOAL__"):
                objective = response_md.replace("__RUN_GOAL__", "")
                self._run_goal_planner(objective)
                return
            else:
                self.chat_widget.add_assistant_message(response_md)
                self._sync_voice_settings()
                if is_voice_enabled():
                    speak(response_md)
                return

        # 2. Standard LLM Inference
        notify(f"Processing query: {prompt[:30]}...", level="info")
        self.telemetry_sidebar.set_core_status("THINKING")

        self.chat_widget.start_assistant_message()

        self.inference_thread = QThread(self)
        self.inference_worker = InferenceWorker(prompt)
        self.inference_worker.moveToThread(self.inference_thread)

        self.inference_thread.started.connect(self.inference_worker.run)
        self.inference_worker.token_received.connect(self._on_token_received)
        self.inference_worker.finished.connect(self._on_inference_finished)
        self.inference_worker.error_occurred.connect(self._on_inference_error)

        self.inference_thread.start()

    def _run_goal_planner(self, objective: str):
        notify(f"Synthesizing autonomous goal: {objective[:30]}...", level="info")
        self.telemetry_sidebar.set_core_status("PLANNING")
        card = self.chat_widget.start_assistant_message()
        card.update_content(f"🎯 **Synthesizing Autonomous Goal:** `{objective}`\n\n*Planning subtasks and verifying dependencies...*")

        self.goal_thread = QThread(self)
        self.goal_worker = GoalWorker(objective)
        self.goal_worker.moveToThread(self.goal_thread)

        self.goal_thread.started.connect(self.goal_worker.run)
        self.goal_worker.finished.connect(self._on_goal_finished)
        self.goal_thread.start()

    def _on_goal_finished(self, result_text: str):
        self.chat_widget.finalize_assistant_message(result_text)
        notify("Goal execution plan ready.", level="success")
        self._reset_to_ready()

        if self.goal_thread and self.goal_thread.isRunning():
            self.goal_thread.quit()
            self.goal_thread.wait()

    def _on_token_received(self, token: str):
        self.chat_widget.append_assistant_token(token)
        self.telemetry_sidebar.set_core_status("PROCESSING")

    def _on_inference_finished(self, full_response: str):
        self.chat_widget.finalize_assistant_message(full_response)
        notify("Response generated.", level="success")

        if is_voice_enabled() and full_response:
            self.telemetry_sidebar.set_core_status("SPEAKING")
            speak(full_response)
            QTimer.singleShot(1800, self._reset_to_ready)
        else:
            self._reset_to_ready()

        if self.inference_thread and self.inference_thread.isRunning():
            self.inference_thread.quit()
            self.inference_thread.wait()

    def _on_inference_error(self, error: str):
        self.chat_widget.append_assistant_token(f"\n\n**Error:** `{error}`")
        self.chat_widget.finalize_assistant_message(f"Error: {error}")
        notify(f"Inference error: {error}", level="error")
        self.telemetry_sidebar.set_core_status("ERROR")
        self._reset_to_ready()

    def _reset_to_ready(self):
        self.telemetry_sidebar.set_core_status("READY")

    def _toggle_mic_listen(self):
        if self.is_listening:
            return

        self.is_listening = True
        self.mic_btn.setText("🔴 Recording (5s)...")
        self.prompt_input.setPlaceholderText("🔴 Recording... Speak into your microphone now.")
        self.telemetry_sidebar.set_core_status("LISTENING")
        notify("Listening to microphone (5s)... Speak now", level="info")

        self.voice_thread = QThread(self)
        self.voice_worker = VoiceWorker()
        self.voice_worker.moveToThread(self.voice_thread)

        self.voice_thread.started.connect(self.voice_worker.run)
        self.voice_worker.transcription_ready.connect(self._on_voice_transcribed)
        self.voice_worker.error_occurred.connect(lambda e: self._on_voice_transcribed(""))

        self.voice_thread.start()

    def _on_voice_transcribed(self, text: str):
        self.is_listening = False
        self.mic_btn.setText("🎙️ Speak")
        self.prompt_input.setPlaceholderText("Ask PETROVA anything or enter command (e.g. /help, /stats, /goal)...")

        if text and text.strip():
            notify(f"Voice recognized: \"{text}\"", level="success")
            self.prompt_input.setPlainText(text)
            self._on_submit_prompt()
        else:
            notify("No speech detected. Please check mic input volume.", level="warning")
            self.prompt_input.setPlaceholderText("No speech detected. Try speaking closer to mic.")
            self._reset_to_ready()

        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.quit()
            self.voice_thread.wait()

    def _execute_proposed_command(self, cmd: str):
        """Thread-safe interactive command execution with live streaming and stdin piping."""
        self.terminal_drawer.setVisible(True)
        self.telemetry_sidebar.set_core_status("EXECUTING")
        self.terminal_drawer.append_output(f"\n[Executing]: {cmd}\n")
        self.terminal_drawer.set_busy_state(True)
        notify(f"Executing: {cmd}", level="info")

        # Check if command requires sudo authentication
        sudo_pwd = None
        if "sudo " in cmd:
            res = subprocess.run("sudo -n true", shell=True, capture_output=True)
            if res.returncode != 0:
                if self.cached_sudo_password:
                    sudo_pwd = self.cached_sudo_password
                else:
                    pwd, ok = QInputDialog.getText(
                        self,
                        "Root Authentication Required",
                        f"Enter sudo password to execute:\n{cmd}",
                        QLineEdit.EchoMode.Password,
                    )
                    if ok and pwd:
                        sudo_pwd = pwd
                        self.cached_sudo_password = pwd
                    else:
                        self.terminal_drawer.append_output("[Authentication cancelled by user]\n")
                        self.terminal_drawer.set_busy_state(False)
                        notify("Execution cancelled (no sudo password).", level="warning")
                        self._reset_to_ready()
                        return

        if hasattr(self, "command_thread") and self.command_thread and self.command_thread.isRunning():
            self.command_thread.quit()
            self.command_thread.wait()

        self.command_thread = QThread(self)
        self.command_worker = InteractiveCommandWorker(cmd, sudo_password=sudo_pwd)
        self.command_worker.moveToThread(self.command_thread)

        self.command_thread.started.connect(self.command_worker.run)
        self.command_worker.output_line.connect(self.terminal_drawer.append_output)
        self.command_worker.finished.connect(self._on_command_finished)

        self.command_thread.start()

    def _on_terminal_stdin_submitted(self, text: str):
        """Handle user input into active process (y/n, prompt response)."""
        if self.command_worker:
            self.command_worker.send_stdin(text)

    def _on_command_finished(self, code: int):
        self.terminal_drawer.append_output(f"[Process finished with exit code {code}]\n")
        self.terminal_drawer.set_busy_state(False)
        
        if code == 0:
            notify("Command executed successfully.", level="success")
        else:
            notify(f"Command finished with exit code {code}", level="warning")

        self._reset_to_ready()

        if self.command_thread and self.command_thread.isRunning():
            self.command_thread.quit()
            self.command_thread.wait()

    def _toggle_terminal_drawer(self):
        visible = not self.terminal_drawer.isVisible()
        self.terminal_drawer.setVisible(visible)
        if visible:
            self.terminal_drawer.input_field.setFocus()

    def _open_memory_vault(self):
        dlg = MemoryVaultDialog(self)
        dlg.exec()
