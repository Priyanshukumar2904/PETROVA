"""
PETROVA Autonomous Tasks & Goal Manager View.
Tracks background jobs, system maintenance scripts, and multi-step agentic goals.
"""

from datetime import datetime
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
)

from petrova.gui.styles import COLORS
from petrova.gui.notifications import notify


class TasksViewWidget(QWidget):
    """
    Dedicated TASKS & Autonomous Objective Manager View.
    """
    execute_goal_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks_list = [
            {"id": "T-101", "name": "System Health Monitor", "status": "RUNNING", "progress": "Active", "type": "Background"},
            {"id": "T-102", "name": "Telemetry Engine", "status": "RUNNING", "progress": "Active", "type": "Daemon"},
            {"id": "T-103", "name": "Package Cache Check", "status": "COMPLETED", "progress": "Done", "type": "System"},
            {"id": "T-104", "name": "Neural Synapse Init", "status": "COMPLETED", "progress": "Done", "type": "Core"},
        ]
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Header Bar
        hdr = QHBoxLayout()
        title = QLabel("AUTONOMOUS TASK & GOAL QUEUE")
        title.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 14px; font-weight: 900; letter-spacing: 1px;")
        
        hdr.addWidget(title)
        hdr.addStretch()
        layout.addLayout(hdr)

        # Goal Input Bar
        goal_box = QFrame()
        goal_box.setObjectName("LowerCard")
        gb_layout = QHBoxLayout(goal_box)
        gb_layout.setContentsMargins(10, 8, 10, 8)
        gb_layout.setSpacing(8)

        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("Enter new goal (e.g. 'audit system security' or 'backup ~/.config')...")
        self.goal_input.setStyleSheet(f"background: transparent; border: none; color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 13.5px;")
        self.goal_input.returnPressed.connect(self._on_submit_goal)

        add_btn = QPushButton("+ Plan Goal")
        add_btn.setObjectName("MonochromePill")
        add_btn.clicked.connect(self._on_submit_goal)

        gb_layout.addWidget(self.goal_input, 1)
        gb_layout.addWidget(add_btn)
        layout.addWidget(goal_box)

        # Tasks Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["TASK ID", "NAME / OBJECTIVE", "STATUS", "PROGRESS", "TYPE"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['foreground']};
                border: 1px solid {COLORS['border']};
                gridline-color: {COLORS['border']};
                font-family: 'JetBrains Mono', monospace;
                font-size: 12.5px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['background']};
                color: {COLORS['muted']};
                border: 1px solid {COLORS['border']};
                padding: 4px 8px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.table, 1)

        self._refresh_table()

    def _refresh_table(self):
        self.table.setRowCount(len(self.tasks_list))
        for row, t in enumerate(self.tasks_list):
            self.table.setItem(row, 0, QTableWidgetItem(t["id"]))
            self.table.setItem(row, 1, QTableWidgetItem(t["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(t["status"]))
            self.table.setItem(row, 3, QTableWidgetItem(t["progress"]))
            self.table.setItem(row, 4, QTableWidgetItem(t["type"]))

    def _on_submit_goal(self):
        text = self.goal_input.text().strip()
        if not text:
            return
        self.goal_input.clear()
        
        new_id = f"G-{len(self.tasks_list)+101}"
        self.tasks_list.insert(0, {
            "id": new_id,
            "name": text,
            "status": "QUEUED",
            "progress": "Planning",
            "type": "Agentic Goal",
        })
        self._refresh_table()
        notify(f"Scheduled new goal [{new_id}]: {text}", level="info")
        self.execute_goal_requested.emit(f"/goal {text}")
