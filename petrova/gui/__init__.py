"""
PETROVA Desktop GUI Subsystem.
"""

from petrova.gui.app import launch_gui, main
from petrova.gui.window import PetrovaMainWindow
from petrova.gui.neural_canvas import NeuralVisualizerWidget, NeuralState
from petrova.gui.telemetry_widget import TelemetryDashboardWidget
from petrova.gui.terminal_drawer import TerminalDrawerWidget

__all__ = [
    "launch_gui",
    "main",
    "PetrovaMainWindow",
    "NeuralVisualizerWidget",
    "NeuralState",
    "TelemetryDashboardWidget",
    "TerminalDrawerWidget",
]
