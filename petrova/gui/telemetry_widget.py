"""
PETROVA Dynamic Telemetry Ribbon & Capsule HUD.
Horizontal status capsules utilizing window width efficiently with clean symbols and prominent metrics.
"""

from typing import Dict, Any
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QFrame,
    QPushButton,
)

from petrova.linux.stats import get_system_telemetry


class TelemetryDashboardWidget(QFrame):
    """
    Modern Horizontal Telemetry HUD Ribbon.
    Displays CPU, RAM, Battery, and Storage as elegant status capsules.
    """
    refresh_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TelemetryHUD")
        self._setup_ui()

        # Telemetry refresh timer (every 1.5 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(1500)

        # Initial populate
        self.update_telemetry()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 6, 16, 6)
        main_layout.setSpacing(12)

        # 1. CPU & Thermals Capsule
        cpu_capsule, self.cpu_temp_val, self.cpu_sub_val = self._create_capsule(
            icon="⚡",
            label="CPU",
            accent_color="#00f59b",
        )
        main_layout.addWidget(cpu_capsule)

        # 2. RAM Memory Capsule
        ram_capsule, self.ram_val, self.ram_sub_val = self._create_capsule(
            icon="🧠",
            label="RAM",
            accent_color="#34d399",
        )
        main_layout.addWidget(ram_capsule)

        # 3. Battery & Power Capsule
        bat_capsule, self.bat_val, self.bat_sub_val = self._create_capsule(
            icon="🔋",
            label="POWER",
            accent_color="#fbbf24",
        )
        main_layout.addWidget(bat_capsule)

        # 4. Storage Capsule
        disk_capsule, self.disk_val, self.disk_sub_val = self._create_capsule(
            icon="💾",
            label="DISK",
            accent_color="#38bdf8",
        )
        main_layout.addWidget(disk_capsule)

        main_layout.addStretch()

        # Quick Refresh Button
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(28, 28)
        self.refresh_btn.setToolTip("Refresh Live System Telemetry")
        self.refresh_btn.setStyleSheet("padding: 0; font-size: 14px; border-radius: 14px;")
        self.refresh_btn.clicked.connect(self.update_telemetry)
        main_layout.addWidget(self.refresh_btn)

    def _create_capsule(self, icon: str, label: str, accent_color: str):
        """Create a sleek horizontal status capsule with icon, label, and high-visibility value."""
        capsule = QFrame()
        capsule.setObjectName("TelemetryCapsule")
        layout = QHBoxLayout(capsule)
        layout.setContentsMargins(10, 4, 10, 4)
        layout.setSpacing(8)

        icon_lbl = QLabel(icon)
        icon_lbl.setObjectName("CapsuleIcon")

        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        text_layout.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        
        lbl = QLabel(label)
        lbl.setObjectName("CapsuleLabel")

        val_lbl = QLabel("--")
        val_lbl.setObjectName("CapsuleValue")
        val_lbl.setStyleSheet(f"color: {accent_color}; font-size: 14px; font-weight: 800;")

        top_row.addWidget(lbl)
        top_row.addWidget(val_lbl)
        text_layout.addLayout(top_row)

        sub_lbl = QLabel("--")
        sub_lbl.setStyleSheet("color: #64748b; font-size: 11px;")
        text_layout.addWidget(sub_lbl)

        layout.addWidget(icon_lbl)
        layout.addLayout(text_layout)

        return capsule, val_lbl, sub_lbl

    def update_telemetry(self):
        """Fetch latest Linux metrics and update capsule displays."""
        try:
            data = get_system_telemetry()
            
            # 1. CPU & Thermals
            temp = data.get("cpu_temp")
            load = data.get("load_avg", "")
            load_first = load.split(",")[0] if load else "Active"
            if temp is not None:
                self.cpu_temp_val.setText(f"{temp:.1f}°C")
                self.cpu_sub_val.setText(f"Load {load_first}")
            else:
                self.cpu_temp_val.setText("Optimal")
                self.cpu_sub_val.setText(f"Load {load_first}")

            # 2. RAM Memory
            ram = data.get("ram", {})
            ram_pct = int(ram.get("pct", 0))
            ram_used = ram.get("used_gb", 0.0)
            ram_tot = ram.get("total_gb", 0.0)
            self.ram_val.setText(f"{ram_used:.1f} GB ({ram_pct}%)")
            self.ram_sub_val.setText(f"of {ram_tot:.0f} GB Total")

            # 3. Battery & Power
            bat = data.get("battery", {})
            if bat.get("present"):
                bat_pct = int(bat.get("percent", 100))
                plugged = bat.get("plugged_in", True)
                power_txt = "⚡ AC Connected" if plugged else f"🔋 {bat.get('time_str', 'Discharging')}"
                self.bat_val.setText(f"{bat_pct}%")
                self.bat_sub_val.setText(power_txt)
            else:
                self.bat_val.setText("100%")
                self.bat_sub_val.setText("⚡ AC Powered")

            # 4. Storage
            disk = data.get("disk", {})
            disk_pct = int(disk.get("pct", 0))
            disk_free = disk.get("free_gb", 0.0)
            self.disk_val.setText(f"{disk_free:.0f} GB Free")
            self.disk_sub_val.setText(f"{disk_pct}% Utilized")

        except Exception:
            pass
