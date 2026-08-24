"""
PETROVA Main Desktop Application Window.
Integrates Interactive Neural Cognitive Topology, Minimalist Resource Telemetry,
Translucent Glass Chat View, Terminal Drawer, and Asynchronous AI Streaming.
"""

import sys
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
    QSplitter,
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
from petrova.gui.neural_canvas import NeuralVisualizerWidget, NeuralState
from petrova.gui.telemetry_widget import TelemetryDashboardWidget
from petrova.gui.terminal_drawer import TerminalDrawerWidget
from petrova.gui.chat_widget import ChatWidget
from petrova.gui.memory_dialog import MemoryVaultDialog


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
            self.thinking_phase.emit("Evaluating Context & System Telemetry...")
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
    Main Modern Desktop Application Window for PETROVA.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PETROVA — AI Operating Assistant")
        self.resize(1180, 780)
        self.setMinimumSize(850, 580)
        self.setStyleSheet(SPARKLING_AMBER_GREEN_THEME)

        self.inference_thread: QThread = None
        self.voice_thread: QThread = None
        self.is_listening = False

        self._setup_ui()
        self._setup_shortcuts()
        self._show_initial_greeting()

    def _setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Header Bar (Frameless & Translucent)
        self.header_bar = QFrame()
        self.header_bar.setObjectName("HeaderBar")
        header_layout = QHBoxLayout(self.header_bar)
        header_layout.setContentsMargins(18, 10, 18, 10)
        header_layout.setSpacing(12)

        # Brand Title
        title_lbl = QLabel("PETROVA")
        title_lbl.setObjectName("AppTitle")
        
        # Distro Badge
        distro = get_distro_info()
        self.distro_badge = QLabel(f"🐧 {distro.get('pretty_name', 'Linux')}")
        self.distro_badge.setObjectName("DistroBadge")

        # Neural State Badge
        self.state_badge = QLabel("● IDLE")
        self.state_badge.setObjectName("StateBadge")

        header_layout.addWidget(title_lbl)
        header_layout.addWidget(self.distro_badge)
        header_layout.addWidget(self.state_badge)
        header_layout.addStretch()

        # Action Buttons in Header (Translucent icon chips)
        self.mem_btn = QPushButton("🧠 Memory Vault")
        self.mem_btn.clicked.connect(self._open_memory_vault)
        header_layout.addWidget(self.mem_btn)

        self.voice_toggle_btn = QPushButton("🔊 Voice: ON" if is_voice_enabled() else "🔇 Voice: OFF")
        self.voice_toggle_btn.clicked.connect(self._toggle_voice_output)
        header_layout.addWidget(self.voice_toggle_btn)

        self.term_toggle_btn = QPushButton("💻 Terminal Drawer")
        self.term_toggle_btn.clicked.connect(self._toggle_terminal_drawer)
        header_layout.addWidget(self.term_toggle_btn)

        self.telemetry_toggle_btn = QPushButton("⚡ Telemetry HUD")
        self.telemetry_toggle_btn.clicked.connect(self._toggle_telemetry_sidebar)
        header_layout.addWidget(self.telemetry_toggle_btn)

        main_layout.addWidget(self.header_bar)

        # 2. Main Splitter (Left: Neural Canvas + Chat + Drawer | Right: Minimalist Telemetry)
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.setHandleWidth(1)

        # Left Column Container
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        # Interactive Neural Cognitive Visualizer (Accurate Layered Topology)
        self.neural_canvas = NeuralVisualizerWidget(self)
        left_layout.addWidget(self.neural_canvas)

        # Translucent Chat Stream View
        self.chat_widget = ChatWidget(self)
        self.chat_widget.run_command_requested.connect(self._execute_proposed_command)
        left_layout.addWidget(self.chat_widget, 1)

        # Embedded Terminal Drawer (Slide-up)
        self.terminal_drawer = TerminalDrawerWidget(self)
        self.terminal_drawer.close_btn.clicked.connect(lambda: self.terminal_drawer.setVisible(False))
        self.terminal_drawer.command_executed.connect(self._on_terminal_command_done)
        self.terminal_drawer.setVisible(False)
        self.terminal_drawer.setFixedHeight(230)
        left_layout.addWidget(self.terminal_drawer)

        # Input Frame (Translucent glass floating bar)
        self.input_frame = QFrame()
        self.input_frame.setObjectName("InputFrame")
        input_layout = QHBoxLayout(self.input_frame)
        input_layout.setContentsMargins(18, 12, 18, 12)
        input_layout.setSpacing(10)

        # Voice Mic Button
        self.mic_btn = QPushButton("🎙️")
        self.mic_btn.setObjectName("VoiceButton")
        self.mic_btn.setToolTip("Click to Speak (Microphone Speech Recognition)")
        self.mic_btn.clicked.connect(self._toggle_mic_listen)
        input_layout.addWidget(self.mic_btn)

        # Text Input
        self.prompt_input = QTextEdit()
        self.prompt_input.setObjectName("PromptInput")
        self.prompt_input.setPlaceholderText("Type a question, system task, or /goal objective (Press Enter to Send)...")
        self.prompt_input.setFixedHeight(48)
        self.prompt_input.installEventFilter(self)
        input_layout.addWidget(self.prompt_input, 1)

        # Send Button
        self.send_btn = QPushButton("Send ❯")
        self.send_btn.setObjectName("PrimaryButton")
        self.send_btn.setFixedHeight(48)
        self.send_btn.clicked.connect(self._on_submit_prompt)
        input_layout.addWidget(self.send_btn)

        left_layout.addWidget(self.input_frame)

        self.main_splitter.addWidget(left_container)

        # Right Column: Minimalist Telemetry HUD
        self.telemetry_sidebar = TelemetryDashboardWidget(self)
        self.main_splitter.addWidget(self.telemetry_sidebar)

        # Initial splitter proportions
        self.main_splitter.setStretchFactor(0, 3)
        self.main_splitter.setStretchFactor(1, 1)

        main_layout.addWidget(self.main_splitter, 1)

    def _setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+T"), self, self._toggle_terminal_drawer)
        QShortcut(QKeySequence("Ctrl+M"), self, self._open_memory_vault)
        QShortcut(QKeySequence("Ctrl+Shift+V"), self, self._toggle_voice_output)

    def _show_initial_greeting(self):
        """Display initial proactive greeting card."""
        greeting_text = get_greeting()
        config = get_config()
        user_name = config.user_name

        welcome_msg = (
            f"### Welcome, {user_name}!\n\n"
            f"{greeting_text}\n\n"
            f"**PETROVA Synaptic Core** is running 100% locally on your machine with direct Linux kernel access. "
            f"You can ask me questions, execute automated tasks (`/goal`), speak via microphone, "
            f"or slide out the **Terminal Drawer** anytime (`Ctrl+T`)."
        )
        self.chat_widget.add_assistant_message(welcome_msg)

    def eventFilter(self, obj, event):
        # Enter submits, Shift+Enter makes newline
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

        # Set Neural Canvas state to Thinking
        self.neural_canvas.set_state(NeuralState.THINKING, "Analyzing Context & Synthesizing Response...")
        self.state_badge.setText("● THINKING")
        self.state_badge.setStyleSheet("background-color: rgba(251, 191, 36, 0.2); color: #fbbf24; border: 1px solid #f59e0b;")

        # Start streaming assistant bubble
        self.chat_widget.start_assistant_message()

        # Run AI query asynchronously in background thread
        self.inference_thread = QThread()
        self.inference_worker = InferenceWorker(prompt)
        self.inference_worker.moveToThread(self.inference_thread)

        self.inference_thread.started.connect(self.inference_worker.run)
        self.inference_worker.token_received.connect(self._on_token_received)
        self.inference_worker.thinking_phase.connect(lambda p: self.neural_canvas.set_state(NeuralState.THINKING, p))
        self.inference_worker.finished.connect(self._on_inference_finished)
        self.inference_worker.error_occurred.connect(self._on_inference_error)

        self.inference_thread.start()

    def _on_token_received(self, token: str):
        self.chat_widget.append_assistant_token(token)
        # Real-time token synaptic firing
        self.neural_canvas.fire_token_pulse()
        if self.neural_canvas.state != NeuralState.STREAMING:
            self.neural_canvas.set_state(NeuralState.STREAMING)
            self.state_badge.setText("● STREAMING")
            self.state_badge.setStyleSheet("background-color: rgba(0, 245, 155, 0.2); color: #00f59b; border: 1px solid #10b981;")

    def _on_inference_finished(self, full_response: str):
        self.chat_widget.finalize_assistant_message(full_response)

        if is_voice_enabled() and full_response:
            self.neural_canvas.set_state(NeuralState.SPEAKING)
            self.state_badge.setText("🔊 SPEAKING")
            self.state_badge.setStyleSheet("background-color: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid #0284c7;")
            speak(full_response)

        # Reset to IDLE after brief cooldown
        QTimer.singleShot(1400, self._reset_to_idle)

        if self.inference_thread and self.inference_thread.isRunning():
            self.inference_thread.quit()
            self.inference_thread.wait()

    def _on_inference_error(self, error: str):
        self.chat_widget.append_assistant_token(f"\n\n**Error during inference:** `{error}`")
        self.chat_widget.finalize_assistant_message(f"Error during inference: {error}")
        self._reset_to_idle()

    def _reset_to_idle(self):
        self.neural_canvas.set_state(NeuralState.IDLE)
        self.state_badge.setText("● IDLE")
        self.state_badge.setStyleSheet("background-color: rgba(52, 211, 153, 0.12); color: #34d399; border: 1px solid rgba(52, 211, 153, 0.3);")

    def _toggle_mic_listen(self):
        """Start or stop speech recognition from microphone."""
        if self.is_listening:
            return

        self.is_listening = True
        self.mic_btn.setProperty("listening", "true")
        self.mic_btn.style().polish(self.mic_btn)

        self.neural_canvas.set_state(NeuralState.INPUT_ACTIVE)
        self.state_badge.setText("🎙️ LISTENING")
        self.state_badge.setStyleSheet("background-color: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444;")

        self.voice_thread = QThread()
        self.voice_worker = VoiceWorker()
        self.voice_worker.moveToThread(self.voice_thread)

        self.voice_thread.started.connect(self.voice_worker.run)
        self.voice_worker.transcription_ready.connect(self._on_voice_transcribed)
        self.voice_worker.error_occurred.connect(lambda e: self._on_voice_transcribed(""))

        self.voice_thread.start()

    def _on_voice_transcribed(self, text: str):
        self.is_listening = False
        self.mic_btn.setProperty("listening", "false")
        self.mic_btn.style().polish(self.mic_btn)

        if text.strip():
            self.prompt_input.setPlainText(text)
            self._on_submit_prompt()
        else:
            self._reset_to_idle()

        if self.voice_thread and self.voice_thread.isRunning():
            self.voice_thread.quit()
            self.voice_thread.wait()

    def _execute_proposed_command(self, cmd: str):
        """Execute command from proposed card and show output in terminal drawer."""
        self.terminal_drawer.setVisible(True)
        self.neural_canvas.set_state(NeuralState.COMMAND_EXEC)
        self.terminal_drawer.append_output(f"\n[Executing Proposed Command]: {cmd}\n")
        
        def run():
            code, stdout, stderr = execute_command(cmd)
            out = stdout if stdout else ""
            if stderr:
                out += f"\n[stderr]: {stderr}"
            self.terminal_drawer.append_output(f"{out}\n[Exit code: {code}]\n")
            QTimer.singleShot(1000, self._reset_to_idle)

        import threading
        threading.Thread(target=run, daemon=True).start()

    def _on_terminal_command_done(self, cmd: str, output: str, code: int):
        self.terminal_drawer.append_output(f"{output}\n")

    def _toggle_terminal_drawer(self):
        visible = not self.terminal_drawer.isVisible()
        self.terminal_drawer.setVisible(visible)
        if visible:
            self.terminal_drawer.input_field.setFocus()

    def _toggle_telemetry_sidebar(self):
        visible = not self.telemetry_sidebar.isVisible()
        self.telemetry_sidebar.setVisible(visible)

    def _toggle_voice_output(self):
        new_state = not is_voice_enabled()
        set_voice_enabled(new_state)
        self.voice_toggle_btn.setText("🔊 Voice: ON" if new_state else "🔇 Voice: OFF")

    def _open_memory_vault(self):
        dlg = MemoryVaultDialog(self)
        dlg.exec()
