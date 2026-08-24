"""
PETROVA Live Telemetry & Resource Monitoring Sidebar Widget.
Displays real-time hardware gauges, CPU thermals, RAM usage, Battery metrics, and active processes.
"""

from typing import Dict, Any, Tuple
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QFrame,
    QScrollArea,
    QPushButton,
)

from petrova.linux.stats import get_system_telemetry


class TelemetryDashboardWidget(QFrame):
    """
    Real-time system telemetry sidebar panel.
    """
    refresh_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TelemetryPanel")
        self.setMinimumWidth(290)
        self.setMaximumWidth(340)

        self._setup_ui()

        # Telemetry refresh timer (every 1.5 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(1500)

        # Initial populate
        self.update_telemetry()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(14, 14, 14, 14)
        main_layout.setSpacing(12)

        # Header Title
        header_layout = QHBoxLayout()
        title_lbl = QLabel("📊 SYSTEM TELEMETRY")
        title_lbl.setObjectName("SidebarTitle")
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(26, 26)
        self.refresh_btn.setToolTip("Refresh System Metrics")
        self.refresh_btn.clicked.connect(self.update_telemetry)

        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.refresh_btn)
        main_layout.addLayout(header_layout)

        # Scrollable container for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content_widget = QWidget()
        self.cards_layout = QVBoxLayout(content_widget)
        self.cards_layout.setContentsMargins(0, 0, 4, 0)
        self.cards_layout.setSpacing(10)

        # 1. CPU & Thermals Card
        cpu_card, cpu_layout = self._create_card("⚡ CPU & Thermals")
        self.cpu_temp_lbl = QLabel("Temperature: --°C")
        self.cpu_load_lbl = QLabel("Load Avg: --")
        cpu_layout.addWidget(self.cpu_temp_lbl)
        cpu_layout.addWidget(self.cpu_load_lbl)
        self.cards_layout.addWidget(cpu_card)

        # 2. RAM Usage Card
        ram_card, ram_layout = self._create_card("🧠 Memory (RAM)")
        self.ram_lbl = QLabel("RAM: 0.0 / 0.0 GB (0%)")
        self.ram_bar = QProgressBar()
        self.ram_bar.setObjectName("RamBar")
        self.ram_bar.setRange(0, 100)
        ram_layout.addWidget(self.ram_lbl)
        ram_layout.addWidget(self.ram_bar)
        self.cards_layout.addWidget(ram_card)

        # 3. Battery & Power Card
        bat_card, bat_layout = self._create_card("🔋 Battery & Power")
        self.bat_lbl = QLabel("Battery: Detecting...")
        self.bat_bar = QProgressBar()
        self.bat_bar.setObjectName("BatteryBar")
        self.bat_bar.setRange(0, 100)
        bat_layout.addWidget(self.bat_lbl)
        bat_layout.addWidget(self.bat_bar)
        self.cards_layout.addWidget(bat_card)

        # 4. Storage Card
        disk_card, disk_layout = self._create_card("💾 Storage (Root /)")
        self.disk_lbl = QLabel("Disk: 0 / 0 GB")
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        disk_layout.addWidget(self.disk_lbl)
        disk_layout.addWidget(self.disk_bar)
        self.cards_layout.addWidget(disk_card)

        # 5. OS & Kernel Card
        os_card, os_layout = self._create_card("🐧 OS & Kernel")
        self.os_distro_lbl = QLabel("Distro: Arch Linux")
        self.os_distro_lbl.setWordWrap(True)
        self.os_kernel_lbl = QLabel("Kernel: Linux")
        self.os_uptime_lbl = QLabel("Uptime: --")
        os_layout.addWidget(self.os_distro_lbl)
        os_layout.addWidget(self.os_kernel_lbl)
        os_layout.addWidget(self.os_uptime_lbl)
        self.cards_layout.addWidget(os_card)

        # 6. Active Top Processes Card
        proc_card, proc_layout = self._create_card("🔥 Top Active Processes")
        self.proc_lbl = QLabel("Loading processes...")
        self.proc_lbl.setStyleSheet("color: #94a3b8; font-size: 11px;")
        self.proc_lbl.setWordWrap(True)
        proc_layout.addWidget(self.proc_lbl)
        self.cards_layout.addWidget(proc_card)

        self.cards_layout.addStretch()
        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_card(self, title: str) -> Tuple[QFrame, QVBoxLayout]:
        card = QFrame()
        card.setObjectName("TelemetryCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(6)

        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #00f0ff; font-weight: 700; font-size: 12px;")
        layout.addWidget(title_lbl)

        return card, layout

    def update_telemetry(self):
        """Fetch real-time metrics and update UI elements."""
        try:
            data = get_system_telemetry()

            # CPU & Thermals
            temp = data.get("cpu_temp")
            if temp:
                temp_color = "#10b981" if temp < 70 else ("#f59e0b" if temp < 85 else "#ef4444")
                self.cpu_temp_lbl.setText(f"Temperature: <span style='color:{temp_color}; font-weight:bold;'>{temp}°C</span>")
            else:
                self.cpu_temp_lbl.setText("Temperature: N/A")

            self.cpu_load_lbl.setText(f"Load Average: {data.get('load_avg', 'N/A')}")

            # RAM
            ram = data.get("ram", {})
            used_gb = ram.get("used_gb", 0)
            total_gb = ram.get("total_gb", 0)
            pct = ram.get("pct", 0)
            self.ram_lbl.setText(f"RAM: <b>{used_gb} / {total_gb} GB</b> ({pct}%)")
            self.ram_bar.setValue(int(pct))

            # Battery
            bat = data.get("battery", {})
            if bat.get("present"):
                bat_pct = bat.get("percent", 0) or 0
                icon = bat.get("icon", "🔋")
                status = bat.get("status", "Unknown")
                time_str = bat.get("time_str", "")
                detail = f" • {time_str}" if time_str else ""
                self.bat_lbl.setText(f"{icon} <b>{bat_pct}%</b> ({status}{detail})")
                self.bat_bar.setValue(int(bat_pct))
                self.bat_bar.setVisible(True)
            else:
                self.bat_lbl.setText(f"🔌 {bat.get('status', 'AC Power Connected')}")
                self.bat_bar.setVisible(False)

            # Disk
            disk = data.get("disk", {})
            disk_used = disk.get("used_gb", 0)
            disk_total = disk.get("total_gb", 0)
            disk_pct = disk.get("pct", 0)
            disk_free = disk.get("free_gb", 0)
            self.disk_lbl.setText(f"Used: <b>{disk_used}/{disk_total} GB</b> ({disk_free} GB free)")
            self.disk_bar.setValue(int(disk_pct))

            # OS & Kernel
            distro = data.get("distro", {})
            self.os_distro_lbl.setText(f"OS: <b>{distro.get('pretty_name', 'Linux')}</b>")
            self.os_kernel_lbl.setText(f"Kernel: {data.get('kernel', 'Linux')}")
            self.os_uptime_lbl.setText(f"Uptime: {data.get('uptime', 'Unknown')}")

            # Top Processes
            procs = data.get("top_processes", "N/A")
            if procs and procs != "N/A":
                proc_items = [p.strip() for p in procs.split(",") if p.strip()]
                formatted = "<br>".join([f"• <code>{p}</code>" for p in proc_items])
                self.proc_lbl.setText(formatted)
            else:
                self.proc_lbl.setText("No high-usage processes detected.")

        except Exception:
            pass
