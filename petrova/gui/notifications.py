"""
PETROVA Notification and Event Bus for Desktop GUI.
Manages live system logs, operational notices, and task updates.
"""

from datetime import datetime
from typing import List, Dict, Callable
from PyQt6.QtCore import QObject, pyqtSignal


class NotificationManager(QObject):
    """Central event bus for real-time notifications."""
    notification_added = pyqtSignal(str, str, str)  # timestamp, text, level (info, success, warning, error)
    cleared = pyqtSignal()

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = NotificationManager()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.history: List[Dict[str, str]] = []
        # Initial greeting logs
        self.add_notice("PETROVA is now online.", level="success")
        self.add_notice("Local inference engine ready.", level="info")
        self.add_notice("System check completed.", level="info")

    def add_notice(self, text: str, level: str = "info"):
        now_str = datetime.now().strftime("%H:%M:%S")
        entry = {"time": now_str, "text": text, "level": level}
        self.history.append(entry)
        if len(self.history) > 50:
            self.history.pop(0)
        self.notification_added.emit(now_str, text, level)

    def clear(self):
        self.history.clear()
        self.cleared.emit()


def notify(text: str, level: str = "info"):
    NotificationManager.get_instance().add_notice(text, level)
