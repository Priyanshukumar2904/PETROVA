"""
PETROVA Minimalist System Telemetry Widget.
Sleek, uncluttered hardware chips with simple symbols and smooth gauges.
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
    QScrollArea,
    QPushButton,
)

from petrova.linux.stats import get_system_telemetry


class TelemetryDashboardWidget(QFrame):
    """
    Minimalist system telemetry panel.
    Replaces scattered text with clean symbols, large numbers, and smooth gauges.
    """
    refresh_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TelemetryPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(300)

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
        title_lbl = QLabel("⚡ SYSTEM TELEMETRY")
        title_lbl.setObjectName("SidebarTitle")
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(26, 26)
        self.refresh_btn.setToolTip("Refresh System Metrics")
        self.refresh_btn.setStyleSheet("padding: 0; font-size: 14px; border-radius: 13px;")
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
        self.cards_layout.setContentsMargins(0, 0, 0, 0)
        self.cards_layout.setSpacing(10)

        # 1. CPU & Thermals Minimalist Chip
        cpu_card, self.cpu_temp_val, self.cpu_sub_val, self.cpu_bar = self._create_metric_chip(
            icon="⚡",
            title="CPU THERMALS",
            unit="°C",
            accent_color="#00f59b",
        )
        self.cards_layout.addWidget(cpu_card)

        # 2. RAM Memory Minimalist Chip
        ram_card, self.ram_val, self.ram_sub_val, self.ram_bar = self._create_metric_chip(
            icon="🧠",
            title="MEMORY (RAM)",
            unit="%",
            accent_color="#34d399",
        )
        self.cards_layout.addWidget(ram_card)

        # 3. Battery & Power Minimalist Chip
        bat_card, self.bat_val, self.bat_sub_val, self.bat_bar = self._create_metric_chip(
            icon="🔋",
            title="POWER & BATTERY",
            unit="%",
            accent_color="#fbbf24",
        )
        self.cards_layout.addWidget(bat_card)

        # 4. Storage Minimalist Chip
        disk_card, self.disk_val, self.disk_sub_val, self.disk_bar = self._create_metric_chip(
            icon="💾",
            title="STORAGE (ROOT)",
            unit="%",
            accent_color="#38bdf8",
        )
        self.cards_layout.addWidget(disk_card)

        # 5. OS Distro Badge Strip
        self.distro_strip = QFrame()
        self.distro_strip.setObjectName("TelemetryCard")
        distro_layout = QHBoxLayout(self.distro_strip)
        distro_layout.setContentsMargins(10, 8, 10, 8)
        
        self.distro_icon_lbl = QLabel("🐧")
        self.distro_icon_lbl.setStyleSheet("font-size: 16px;")
        self.distro_name_lbl = QLabel("Linux")
        self.distro_name_lbl.setStyleSheet("color: #94a3b8; font-weight: 600; font-size: 12px;")
        
        distro_layout.addWidget(self.distro_icon_lbl)
        distro_layout.addWidget(self.distro_name_lbl)
        distro_layout.addStretch()

        self.cards_layout.addWidget(self.distro_strip)
        self.cards_layout.addStretch()

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_metric_chip(self, icon: str, title: str, unit: str, accent_color: str):
        """Create a clean, minimalist metric card with large value and slim progress bar."""
        card = QFrame()
        card.setObjectName("TelemetryCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        # Top row: Icon + Title
        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet(f"font-size: 14px;")
        
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: #64748b; font-size: 11px; font-weight: 700; letter-spacing: 0.8px;")
        
        top_row.addWidget(icon_lbl)
        top_row.addWidget(title_lbl)
        top_row.addStretch()

        # Center row: Big primary metric value + sub value
        val_row = QHBoxLayout()
        val_lbl = QLabel("--")
        val_lbl.setStyleSheet(f"color: {accent_color}; font-size: 20px; font-weight: 800;")
        
        sub_lbl = QLabel("--")
        sub_lbl.setStyleSheet("color: #94a3b8; font-size: 11.5px;")
        
        val_row.addWidget(val_lbl)
        val_row.addStretch()
        val_row.addWidget(sub_lbl)

        # Bottom row: Slim progress bar
        bar = QProgressBar()
        bar.setRange(0, 100)
        bar.setValue(0)

        layout.addLayout(top_row)
        layout.addLayout(val_row)
        layout.addWidget(bar)

        return card, val_lbl, sub_lbl, bar

    def update_telemetry(self):
        """Fetch latest Linux metrics and update minimalist chips."""
        try:
            data = get_system_telemetry()
            
            # 1. CPU & Thermals
            temp = data.get("cpu_temp")
            if temp is not None:
                self.cpu_temp_val.setText(f"{temp:.1f}°C")
                self.cpu_bar.setValue(min(100, int((temp / 100.0) * 100)))
            else:
                self.cpu_temp_val.setText("Normal")
                self.cpu_bar.setValue(35)
            
            load = data.get("load_avg", "")
            self.cpu_sub_val.setText(f"Load: {load.split(',')[0]}" if load else "Active")

            # 2. RAM Memory
            ram = data.get("ram", {})
            ram_pct = int(ram.get("pct", 0))
            ram_used = ram.get("used_gb", 0.0)
            ram_tot = ram.get("total_gb", 0.0)
            self.ram_val.setText(f"{ram_pct}%")
            self.ram_sub_val.setText(f"{ram_used:.1f} / {ram_tot:.0f} GB")
            self.ram_bar.setValue(ram_pct)

            # 3. Battery & Power
            bat = data.get("battery", {})
            if bat.get("present"):
                bat_pct = int(bat.get("percent", 100))
                plugged = bat.get("plugged_in", True)
                status_icon = "⚡ AC" if plugged else "🔋 Bat"
                self.bat_val.setText(f"{bat_pct}%")
                self.bat_sub_val.setText(f"{status_icon} ({bat.get('status', 'OK')})")
                self.bat_bar.setValue(bat_pct)
            else:
                self.bat_val.setText("100%")
                self.bat_sub_val.setText("⚡ AC Connected")
                self.bat_bar.setValue(100)

            # 4. Storage
            disk = data.get("disk", {})
            disk_pct = int(disk.get("pct", 0))
            disk_free = disk.get("free_gb", 0.0)
            self.disk_val.setText(f"{disk_pct}%")
            self.disk_sub_val.setText(f"{disk_free:.0f} GB Free")
            self.disk_bar.setValue(disk_pct)

            # 5. Distro & Kernel
            distro = data.get("distro", {})
            distro_name = distro.get("pretty_name", "Linux")
            kernel = data.get("kernel", "")
            self.distro_name_lbl.setText(f"{distro_name} • {kernel.split()[0] if kernel else ''}")

        except Exception:
            pass
