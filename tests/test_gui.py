"""
Tests for PETROVA Desktop GUI Subsystem, Neural Visualizer, and Telemetry Widgets.
"""

import os
import unittest

# Ensure headless Qt rendering for tests
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt6.QtWidgets import QApplication
from petrova.gui.desktop import ensure_desktop_entry
from petrova.gui.neural_canvas import NeuralVisualizerWidget, NeuralState
from petrova.gui.telemetry_widget import TelemetryDashboardWidget
from petrova.gui.terminal_drawer import TerminalDrawerWidget
from petrova.gui.chat_widget import ChatWidget, MessageCard
from petrova.gui.window import PetrovaMainWindow


class TestPetrovaGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create single QApplication instance for tests
        cls.app = QApplication.instance() or QApplication([])

    def test_desktop_entry_creation(self):
        res = ensure_desktop_entry()
        self.assertTrue(res)

    def test_neural_canvas_states(self):
        canvas = NeuralVisualizerWidget()
        self.assertEqual(canvas.state, NeuralState.IDLE)
        self.assertGreater(len(canvas.nodes), 10)

        # Test state transitions
        canvas.set_state(NeuralState.THINKING, "Synthesizing Goal")
        self.assertEqual(canvas.state, NeuralState.THINKING)
        self.assertIn("Synthesizing Goal", canvas.status_text)

        canvas.set_state(NeuralState.LISTENING)
        self.assertEqual(canvas.state, NeuralState.LISTENING)

        canvas.set_state(NeuralState.SPEAKING)
        self.assertEqual(canvas.state, NeuralState.SPEAKING)

        canvas.set_audio_level(0.75)
        self.assertEqual(canvas.audio_level, 0.75)

    def test_telemetry_widget(self):
        telemetry = TelemetryDashboardWidget()
        self.assertIsNotNone(telemetry.cpu_temp_lbl)
        self.assertIsNotNone(telemetry.ram_lbl)
        self.assertIsNotNone(telemetry.bat_lbl)
        self.assertIsNotNone(telemetry.disk_lbl)
        telemetry.update_telemetry()

    def test_terminal_drawer(self):
        drawer = TerminalDrawerWidget()
        self.assertIsNotNone(drawer.output)
        self.assertIsNotNone(drawer.input_field)
        drawer.append_output("Test output line")
        self.assertIn("Test output line", drawer.output.toPlainText())

    def test_chat_widget_and_cards(self):
        chat = ChatWidget()
        chat.add_user_message("Hello PETROVA")

        card = chat.start_assistant_message()
        self.assertIsInstance(card, MessageCard)
        chat.append_assistant_token("Here is a command:\n```bash\necho 123\n```")
        chat.finish_assistant_message()
        self.assertIn("echo 123", card.raw_content)

    def test_main_window_init(self):
        window = PetrovaMainWindow()
        self.assertIsNotNone(window.neural_canvas)
        self.assertIsNotNone(window.chat_widget)
        self.assertIsNotNone(window.telemetry_sidebar)
        self.assertIsNotNone(window.terminal_drawer)
        self.assertEqual(window.windowTitle(), "PETROVA — AI Operating Assistant")


if __name__ == "__main__":
    unittest.main()
