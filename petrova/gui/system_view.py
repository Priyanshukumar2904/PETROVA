"""
PETROVA System Intelligence View.
Displays live process table, memory distribution, thermal sensors, and Linux hardware topology.
"""

import subprocess
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
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
    QScrollArea,
)

from petrova.linux.stats import get_system_telemetry, get_cpu_temp, get_distro_info
from petrova.gui.styles import COLORS


class SystemViewWidget(QWidget):
    """
    Dedicated SYSTEM Intelligence and Process Monitor View.
    """
    execute_command_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(3000)

        self.refresh_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Header Bar
        hdr = QHBoxLayout()
        title = QLabel("SYSTEM & PROCESS INTELLIGENCE")
        title.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 14px; font-weight: 900; letter-spacing: 1px;")
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.setObjectName("MonochromePill")
        refresh_btn.clicked.connect(self.refresh_data)

        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(refresh_btn)
        layout.addLayout(hdr)

        # 1. Hardware Summary Card
        self.summary_card = QFrame()
        self.summary_card.setObjectName("LowerCard")
        sum_layout = QVBoxLayout(self.summary_card)
        sum_layout.setContentsMargins(14, 10, 14, 10)
        sum_layout.setSpacing(4)

        self.hw_label = QLabel("Loading hardware telemetry...")
        self.hw_label.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 12.5px; line-height: 1.4;")
        sum_layout.addWidget(self.hw_label)
        layout.addWidget(self.summary_card)

        # 2. Process Table Header
        proc_title = QLabel("ACTIVE PROCESS TABLE (Top CPU & Memory)")
        proc_title.setStyleSheet(f"color: {COLORS['muted']}; font-family: 'JetBrains Mono'; font-size: 11.5px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(proc_title)

        # 3. Process Table
        self.proc_table = QTableWidget()
        self.proc_table.setColumnCount(4)
        self.proc_table.setHorizontalHeaderLabels(["PID", "PROCESS", "CPU %", "MEM %"])
        self.proc_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.proc_table.setStyleSheet(f"""
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
        layout.addWidget(self.proc_table, 1)

        # Actions row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        
        scan_btn = QPushButton("[ Run Full Diagnostics ]")
        scan_btn.setObjectName("MonochromePill")
        scan_btn.clicked.connect(lambda: self.execute_command_requested.emit("journalctl -p 3 -xb -n 20"))
        
        top_btn = QPushButton("[ Open Top Monitor ]")
        top_btn.setObjectName("MonochromePill")
        top_btn.clicked.connect(lambda: self.execute_command_requested.emit("ps aux --sort=-%cpu | head -n 15"))

        btn_row.addWidget(scan_btn)
        btn_row.addWidget(top_btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)

    def refresh_data(self):
        # 1. Update Hardware info
        try:
            data = get_system_telemetry()
            cpu_info = data.get("cpu_info", {})
            distro = data.get("distro", {})
            ram = data.get("ram", {})
            disk = data.get("disk", {})
            temp = data.get("cpu_temp")
            temp_str = f"{temp:.1f}°C" if temp else "N/A"

            txt = (
                f"• OS: {distro.get('pretty_name', 'Linux')} ({data.get('kernel', '')}) | Pkg: {distro.get('package_manager')}\n"
                f"• CPU: {cpu_info.get('model', 'Processor')} ({cpu_info.get('cores', 4)} Cores @ {cpu_info.get('freq_ghz', 3.2)} GHz, Temp: {temp_str})\n"
                f"• RAM: {ram.get('used_gb', 0)} GB / {ram.get('total_gb', 0)} GB ({ram.get('pct', 0)}%) | Swap: {ram.get('swap_used_gb', 0)} GB\n"
                f"• Storage: {disk.get('used_gb', 0)} GB used / {disk.get('total_gb', 0)} GB total ({disk.get('free_gb', 0)} GB available)"
            )
            self.hw_label.setText(txt)
        except Exception:
            pass

        # 2. Update Process Table
        try:
            res = subprocess.run(
                ["ps", "-eo", "pid,comm,%cpu,%mem", "--sort=-%cpu"],
                capture_output=True,
                text=True,
                timeout=0.8,
            )
            if res.returncode == 0:
                lines = [l.strip() for l in res.stdout.strip().split("\n") if l.strip()][1:16]
                self.proc_table.setRowCount(len(lines))
                for row_idx, line in enumerate(lines):
                    parts = line.split(maxsplit=3)
                    if len(parts) >= 4:
                        pid, comm, cpu, mem = parts[0], parts[1], parts[2], parts[3]
                        self.proc_table.setItem(row_idx, 0, QTableWidgetItem(pid))
                        self.proc_table.setItem(row_idx, 1, QTableWidgetItem(comm))
                        self.proc_table.setItem(row_idx, 2, QTableWidgetItem(f"{cpu}%"))
                        self.proc_table.setItem(row_idx, 3, QTableWidgetItem(f"{mem}%"))
        except Exception:
            pass
