"""
Tests for PETROVA Desktop GUI Subsystem, Navigation Views, System Monitor, and Notifications.
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
from petrova.gui.chat_widget import ChatWidget, MessageCard, SparklineStripWidget
from petrova.gui.nav_sidebar import NavSidebarWidget
from petrova.gui.system_view import SystemViewWidget
from petrova.gui.files_view import FilesViewWidget
from petrova.gui.tasks_view import TasksViewWidget
from petrova.gui.settings_view import SettingsViewWidget
from petrova.gui.notifications import NotificationManager, notify
from petrova.gui.window import PetrovaMainWindow


class TestPetrovaGUI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    def test_desktop_entry_creation(self):
        res = ensure_desktop_entry()
        self.assertTrue(res)

    def test_nav_sidebar(self):
        nav = NavSidebarWidget()
        self.assertEqual(nav.active_tab, "HOME")
        self.assertIn("AI_CHAT", nav.nav_buttons)
        nav._set_active_tab("AI_CHAT")
        self.assertEqual(nav.active_tab, "AI_CHAT")

    def test_sparkline_strip(self):
        strip = SparklineStripWidget()
        self.assertIsNotNone(strip.cpu_lbl)
        self.assertIsNotNone(strip.ram_lbl)
        self.assertIsNotNone(strip.temp_lbl)
        strip.update_metrics()

    def test_neural_canvas_states_and_tokens(self):
        canvas = NeuralVisualizerWidget()
        self.assertEqual(canvas.state, NeuralState.IDLE)
        self.assertGreater(len(canvas.nodes), 5)

        # Test state transitions
        canvas.set_state(NeuralState.THINKING, "Synthesizing Goal")
        self.assertEqual(canvas.state, NeuralState.THINKING)
        self.assertIn("Synthesizing Goal", canvas.status_sub)

        canvas.set_state(NeuralState.STREAMING)
        self.assertEqual(canvas.state, NeuralState.STREAMING)

        # Test real-time token firing
        canvas.fire_token_pulse()
        self.assertGreaterEqual(len(canvas.pulses), 1)

        canvas.set_state(NeuralState.SPEAKING)
        self.assertEqual(canvas.state, NeuralState.SPEAKING)

        canvas.set_audio_level(0.75)
        self.assertEqual(canvas.audio_level, 0.75)

    def test_telemetry_widget(self):
        telemetry = TelemetryDashboardWidget()
        self.assertIsNotNone(telemetry.cpu_temp_val)
        self.assertIsNotNone(telemetry.ram_val)
        self.assertIsNotNone(telemetry.disk_val)
        self.assertIsNotNone(telemetry.gpu_val)
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
        chat.finalize_assistant_message("Here is a command:\n```bash\necho 123\n```")
        self.assertIn("echo 123", card.raw_content)

    def test_system_view(self):
        sys_view = SystemViewWidget()
        self.assertIsNotNone(sys_view.proc_table)
        sys_view.refresh_data()

    def test_files_view(self):
        files_view = FilesViewWidget()
        self.assertIsNotNone(files_view.table)
        files_view.refresh_storage()
        if hasattr(files_view, "worker_thread") and files_view.worker_thread:
            files_view.worker_thread.wait(500)
        files_view.close()

    def test_tasks_view(self):
        tasks_view = TasksViewWidget()
        self.assertIsNotNone(tasks_view.table)
        self.assertGreaterEqual(len(tasks_view.tasks_list), 1)

    def test_settings_view(self):
        settings_view = SettingsViewWidget()
        self.assertIsNotNone(settings_view.name_input)

    def test_notifications_bus(self):
        bus = NotificationManager.get_instance()
        notify("Test notice 123", level="info")
        self.assertTrue(any("Test notice 123" in n["text"] for n in bus.history))

    def test_gui_slash_commands(self):
        from petrova.gui.slash_handler import execute_gui_slash_command
        is_slash, res = execute_gui_slash_command("/help")
        self.assertTrue(is_slash)
        self.assertIn("Slash Commands", res)

        is_slash, res = execute_gui_slash_command("/stats")
        self.assertTrue(is_slash)
        self.assertIn("Live System Hardware", res)

        is_slash, res = execute_gui_slash_command("/status")
        self.assertTrue(is_slash)
        self.assertIn("PETROVA System Status", res)

    def test_main_window_init(self):
        window = PetrovaMainWindow()
        self.assertIsNotNone(window.nav_sidebar)
        self.assertIsNotNone(window.chat_widget)
        self.assertIsNotNone(window.telemetry_sidebar)
        self.assertIsNotNone(window.terminal_drawer)
        self.assertIn("PETROVA", window.windowTitle())
        window.close()


if __name__ == "__main__":
    unittest.main()

