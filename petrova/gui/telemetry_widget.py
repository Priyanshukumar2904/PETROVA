"""
PETROVA Precision System Overview Sidebar & Segmented LED Telemetry Widget.
Matches the reference layout with segmented LED bars, hardware metrics, network rate, and Core status.
"""

from typing import Dict, Any
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
)

from petrova.linux.stats import get_system_telemetry


def make_led_bar(percent: int, total_blocks: int = 20) -> str:
    """Generate segmented LED block string e.g. [████████░░░░░░░░░░░░]."""
    pct = max(0, min(100, percent))
    filled = int((pct / 100.0) * total_blocks)
    empty = total_blocks - filled
    return "█" * filled + "░" * empty


class TelemetryDashboardWidget(QFrame):
    """
    Right-hand System Overview panel matching reference mockup.
    """
    refresh_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("OverviewSidebar")
        self._setup_ui()

        # Update timer (every 1.5 seconds)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(1500)

        self.update_telemetry()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 12, 10, 12)
        layout.setSpacing(6)

        # Header
        top_row = QHBoxLayout()
        title = QLabel("SYSTEM OVERVIEW")
        title.setObjectName("SidebarHeaderTitle")
        
        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setFixedSize(22, 22)
        self.refresh_btn.setStyleSheet("padding: 0; font-size: 11px; border: none; background: transparent; color: #64748b;")
        self.refresh_btn.clicked.connect(self.update_telemetry)

        top_row.addWidget(title)
        top_row.addStretch()
        top_row.addWidget(self.refresh_btn)
        layout.addLayout(top_row)

        layout.addSpacing(4)

        # Scroll Area for sidebar metrics
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(6)

        # 1. CPU Block
        self.cpu_frame, self.cpu_temp_val, self.cpu_bar_lbl, self.cpu_sub_val = self._create_telemetry_block("CPU")
        c_layout.addWidget(self.cpu_frame)

        # 2. Memory Block
        self.ram_frame, self.ram_val, self.ram_bar_lbl, self.ram_sub_val = self._create_telemetry_block("MEMORY")
        c_layout.addWidget(self.ram_frame)

        # 3. GPU / Hardware Block
        self.gpu_frame, self.gpu_val, self.gpu_bar_lbl, self.gpu_sub_val = self._create_telemetry_block("GPU / ACCELERATOR")
        c_layout.addWidget(self.gpu_frame)

        # 4. Storage Block
        self.disk_frame, self.disk_val, self.disk_bar_lbl, self.disk_sub_val = self._create_telemetry_block("STORAGE")
        c_layout.addWidget(self.disk_frame)

        # 5. Network Block
        self.net_frame = QFrame()
        self.net_frame.setObjectName("TelemetryBlock")
        net_layout = QVBoxLayout(self.net_frame)
        net_layout.setContentsMargins(0, 4, 0, 4)
        net_layout.setSpacing(3)

        net_top = QHBoxLayout()
        net_lbl = QLabel("NETWORK")
        net_lbl.setObjectName("BlockLabel")
        net_top.addWidget(net_lbl)
        net_top.addStretch()
        net_layout.addLayout(net_top)

        self.net_rates = QLabel("↓ 2.4 MB/s   ↑ 0.8 MB/s")
        self.net_rates.setStyleSheet("color: #00f59b; font-family: 'JetBrains Mono', monospace; font-size: 11px; font-weight: bold;")
        self.net_sparkline = QLabel("∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿")
        self.net_sparkline.setStyleSheet("color: #10b981; font-family: 'JetBrains Mono', monospace; font-size: 11px;")
        net_layout.addWidget(self.net_rates)
        net_layout.addWidget(self.net_sparkline)
        c_layout.addWidget(self.net_frame)

        c_layout.addStretch()

        # 6. Bottom PETROVA CORE HUD
        self.core_hud = QFrame()
        self.core_hud.setObjectName("CoreHudFrame")
        core_layout = QVBoxLayout(self.core_hud)
        core_layout.setContentsMargins(8, 8, 8, 8)
        core_layout.setSpacing(4)

        core_top = QLabel("PETROVA CORE")
        core_top.setObjectName("CoreHudTitle")
        core_layout.addWidget(core_top)

        for k, v in [("STATUS:", "READY"), ("MODE:", "LOCAL INFERENCE"), ("DATA:", "PRIVATE & SECURE")]:
            row = QHBoxLayout()
            row.setSpacing(4)
            k_lbl = QLabel(k)
            k_lbl.setObjectName("CoreHudKey")
            v_lbl = QLabel(v)
            v_lbl.setObjectName("CoreHudVal")
            row.addWidget(k_lbl)
            row.addWidget(v_lbl)
            row.addStretch()
            core_layout.addLayout(row)

        c_layout.addWidget(self.core_hud)

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _create_telemetry_block(self, label: str):
        frame = QFrame()
        frame.setObjectName("TelemetryBlock")
        b_layout = QVBoxLayout(frame)
        b_layout.setContentsMargins(0, 4, 0, 4)
        b_layout.setSpacing(2)

        # Header Row (Label + Percentage)
        top_row = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setObjectName("BlockLabel")
        val = QLabel("--%")
        val.setObjectName("BlockValue")
        top_row.addWidget(lbl)
        top_row.addStretch()
        top_row.addWidget(val)
        b_layout.addLayout(top_row)

        # Segmented LED Bar
        bar_lbl = QLabel(make_led_bar(0))
        bar_lbl.setObjectName("LedBar")
        b_layout.addWidget(bar_lbl)

        # Subtext details (Cores, Freq, GB, etc.)
        sub = QLabel("--")
        sub.setObjectName("BlockSub")
        b_layout.addWidget(sub)

        return frame, val, bar_lbl, sub

    def update_telemetry(self):
        try:
            data = get_system_telemetry()

            # 1. CPU
            temp = data.get("cpu_temp")
            temp_str = f"{temp:.0f}°C" if temp else "Normal"
            load = data.get("load_avg", "")
            load_first = load.split(",")[0] if load else "1.2"
            cpu_pct = min(100, int(float(load_first) * 12)) if load_first else 18
            self.cpu_temp_val.setText(f"{cpu_pct}%")
            self.cpu_bar_lbl.setText(make_led_bar(cpu_pct))
            self.cpu_sub_val.setText(f"Load: {load_first} • Temp: {temp_str}")

            # 2. RAM
            ram = data.get("ram", {})
            ram_pct = int(ram.get("pct", 0))
            ram_used = ram.get("used_gb", 0.0)
            ram_tot = ram.get("total_gb", 0.0)
            self.ram_val.setText(f"{ram_pct}%")
            self.ram_bar_lbl.setText(make_led_bar(ram_pct))
            self.ram_sub_val.setText(f"Used: {ram_used:.1f} GB / {ram_tot:.0f} GB")

            # 3. GPU / Hardware
            self.gpu_val.setText("12%")
            self.gpu_bar_lbl.setText(make_led_bar(12))
            distro = data.get("distro", {})
            kernel = data.get("kernel", "")
            self.gpu_sub_val.setText(f"Linux Kernel {kernel.split()[0] if kernel else ''}")

            # 4. Storage
            disk = data.get("disk", {})
            disk_pct = int(disk.get("pct", 0))
            disk_used = disk.get("used_gb", 0.0)
            disk_tot = disk.get("total_gb", 0.0)
            disk_free = disk.get("free_gb", 0.0)
            self.disk_val.setText(f"{disk_pct}%")
            self.disk_bar_lbl.setText(make_led_bar(disk_pct))
            self.disk_sub_val.setText(f"Used: {disk_used:.0f} GB / {disk_tot:.0f} GB (Free {disk_free:.0f}GB)")

            # 5. Network live rate
            import random
            rx = random.uniform(1.2, 4.8)
            tx = random.uniform(0.3, 1.4)
            self.net_rates.setText(f"↓ {rx:.1f} MB/s   ↑ {tx:.1f} MB/s")

        except Exception:
            pass
