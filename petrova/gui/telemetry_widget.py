"""
PETROVA V1 Monochrome System Overview & Hardware Monitor Widget.
Featuring realistic multi-harmonic wave pattern Petrova Core visualizer,
segmented LED bars, real-time hardware telemetry, and dynamic network I/O.
"""

import math
import random
from typing import Dict, Any
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QPolygonF
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QScrollArea,
)

from petrova.linux.stats import get_system_telemetry, get_network_speed
from petrova.gui.styles import COLORS


def make_led_bar(percent: int, total_blocks: int = 20) -> str:
    """Generate segmented LED block string e.g. ████████░░░░░░░░░░░░."""
    pct = max(0, min(100, percent))
    filled = int((pct / 100.0) * total_blocks)
    empty = total_blocks - filled
    return "█" * filled + "░" * empty


class PetrovaCoreIndicator(QWidget):
    """
    Realistic multi-harmonic acoustic & holographic core wave visualizer.
    Generates radiating frequency wave patterns when speaking/listening,
    high-frequency orbital flux when thinking, and calm breathing waves when idle.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(90, 90)
        self.phase = 0.0
        self.status = "READY"
        self.audio_level = 0.0

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(24)  # ~40 FPS smooth wave rendering

    def set_status(self, status: str):
        self.status = status
        self.update()

    def set_audio_level(self, level: float):
        self.audio_level = max(0.0, min(1.0, level))

    def _on_tick(self):
        # Update wave phase based on current state
        if self.status in ("SPEAKING", "LISTENING"):
            self.phase += 0.12
            # Simulate dynamic speech amplitude waveform if not provided
            self.audio_level = 0.4 + 0.5 * math.sin(self.phase * 2.5) ** 2
        elif self.status in ("THINKING", "PROCESSING", "EXECUTING"):
            self.phase += 0.16
            self.audio_level = 0.3 + 0.3 * math.sin(self.phase * 4.0) ** 2
        else:
            self.phase += 0.04
            self.audio_level = 0.1 + 0.05 * math.sin(self.phase)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        cx, cy = 45.0, 45.0
        center = QPointF(cx, cy)

        # Draw outer subtle boundary circle
        painter.setPen(QPen(QColor(COLORS["border"]), 1.0))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(center, 42.0, 42.0)

        # 1. Concentric Multi-Harmonic Acoustic Waveform Rings
        num_rings = 4 if self.status in ("SPEAKING", "LISTENING") else 3
        is_speaking = self.status in ("SPEAKING", "LISTENING")

        for ring_i in range(num_rings):
            base_r = 14.0 + ring_i * 8.0
            amp = (4.5 + ring_i * 2.5) * self.audio_level if is_speaking else 1.5
            freq = 6 if ring_i % 2 == 0 else 8
            
            wave_points = []
            num_points = 64
            for pt_i in range(num_points):
                theta = (pt_i / float(num_points)) * math.pi * 2
                # Multi-harmonic radial displacement: sin + cos harmonics
                disp = amp * math.sin(freq * theta + self.phase * (1.0 + ring_i * 0.4))
                if is_speaking:
                    disp += (amp * 0.5) * math.cos((freq * 2) * theta - self.phase * 1.5)
                
                r = max(4.0, base_r + disp)
                x = cx + r * math.cos(theta)
                y = cy + r * math.sin(theta)
                wave_points.append(QPointF(x, y))

            # Draw polygon wave ring
            poly = QPolygonF(wave_points)
            alpha = int(255 - ring_i * 45) if is_speaking else int(180 - ring_i * 40)
            pen_w = 1.6 if (ring_i == 0 or is_speaking) else 1.0
            painter.setPen(QPen(QColor(255, 255, 255, alpha), pen_w))
            painter.drawPolygon(poly)

        # 2. Orbital Reticle Ticks (Compass alignment ticks)
        painter.setPen(QPen(QColor(COLORS["muted"]), 1.0))
        for tick_i in range(8):
            ang = (tick_i / 8.0) * math.pi * 2 + (self.phase * 0.2 if self.status == "THINKING" else 0)
            p1 = QPointF(cx + 38.0 * math.cos(ang), cy + 38.0 * math.sin(ang))
            p2 = QPointF(cx + 42.0 * math.cos(ang), cy + 42.0 * math.sin(ang))
            painter.drawLine(p1, p2)

        # 3. Inner Solid Core Iris
        core_r = 6.0 + (3.0 * self.audio_level if is_speaking else 1.0 * math.sin(self.phase))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(COLORS["foreground"])))
        painter.drawEllipse(center, core_r, core_r)

        # Center Void Dot
        painter.setBrush(QBrush(QColor(COLORS["background"])))
        painter.drawEllipse(center, core_r * 0.45, core_r * 0.45)


class TelemetryDashboardWidget(QFrame):
    """
    Right-hand System Overview panel matching the exact reference mockup.
    """
    refresh_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("RightSystemMonitor")
        self.setFixedWidth(320)
        self._setup_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(1500)

        self.update_telemetry()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 14, 12, 14)
        layout.setSpacing(8)

        # 1. Header: SYSTEM OVERVIEW ^
        top_row = QHBoxLayout()
        title = QLabel("SYSTEM OVERVIEW")
        title.setObjectName("OverviewHeaderTitle")
        
        caret_lbl = QLabel("^")
        caret_lbl.setStyleSheet(f"color: {COLORS['muted']}; font-family: 'JetBrains Mono'; font-weight: bold;")

        top_row.addWidget(title)
        top_row.addStretch()
        top_row.addWidget(caret_lbl)
        layout.addLayout(top_row)

        layout.addSpacing(2)

        # Scroll Area for clean overflow handling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(6)

        # --- Section 16: CPU ---
        self.cpu_frame, self.cpu_temp_val, self.cpu_bar_lbl, self.cpu_sub_1, self.cpu_sub_2 = self._create_metric_block("CPU")
        c_layout.addWidget(self.cpu_frame)

        # --- Section 17: MEMORY ---
        self.ram_frame, self.ram_val, self.ram_bar_lbl, self.ram_sub_1, self.ram_sub_2 = self._create_metric_block("MEMORY")
        c_layout.addWidget(self.ram_frame)

        # --- Section 18: GPU ---
        self.gpu_frame, self.gpu_val, self.gpu_bar_lbl, self.gpu_sub_1, self.gpu_sub_2 = self._create_metric_block("GPU")
        c_layout.addWidget(self.gpu_frame)

        # --- Section 19: STORAGE ---
        self.disk_frame, self.disk_val, self.disk_bar_lbl, self.disk_sub_1, self.disk_sub_2 = self._create_metric_block("STORAGE")
        c_layout.addWidget(self.disk_frame)

        # --- Section 20: NETWORK ---
        self.net_frame = QFrame()
        self.net_frame.setObjectName("MonitorBlock")
        net_layout = QVBoxLayout(self.net_frame)
        net_layout.setContentsMargins(0, 4, 0, 4)
        net_layout.setSpacing(3)

        net_top = QHBoxLayout()
        net_lbl = QLabel("NETWORK")
        net_lbl.setObjectName("BlockLabel")
        net_top.addWidget(net_lbl)
        net_top.addStretch()
        net_layout.addLayout(net_top)

        self.net_rates = QLabel("↓ 2.4 MB/s       ↑ 0.8 MB/s")
        self.net_rates.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono', monospace; font-size: 11.5px; font-weight: bold;")
        self.net_sparkline = QLabel("∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿∿")
        self.net_sparkline.setStyleSheet(f"color: {COLORS['secondary']}; font-family: 'JetBrains Mono', monospace; font-size: 11.5px;")
        net_layout.addWidget(self.net_rates)
        net_layout.addWidget(self.net_sparkline)
        c_layout.addWidget(self.net_frame)

        # --- Section 21: PETROVA CORE ---
        self.core_frame = QFrame()
        self.core_frame.setObjectName("PetrovaCoreFrame")
        core_layout = QVBoxLayout(self.core_frame)
        core_layout.setContentsMargins(10, 10, 10, 10)
        core_layout.setSpacing(6)

        core_top = QLabel("PETROVA CORE")
        core_top.setObjectName("CoreTitle")
        core_layout.addWidget(core_top)

        self.core_anim = PetrovaCoreIndicator()
        core_layout.addWidget(self.core_anim, alignment=Qt.AlignmentFlag.AlignCenter)

        for k, v_attr in [("STATUS:", "core_status_lbl"), ("MODE:", "core_mode_lbl"), ("DATA:", "core_data_lbl")]:
            row = QHBoxLayout()
            row.setSpacing(6)
            k_lbl = QLabel(k)
            k_lbl.setObjectName("CoreKey")
            v_lbl = QLabel("READY" if k == "STATUS:" else "LOCAL INFERENCE" if k == "MODE:" else "PRIVATE & SECURE")
            v_lbl.setObjectName("CoreVal")
            setattr(self, v_attr, v_lbl)
            row.addWidget(k_lbl)
            row.addWidget(v_lbl)
            row.addStretch()
            core_layout.addLayout(row)

        c_layout.addWidget(self.core_frame)

        # --- Section 22: SYSTEM INFO ---
        self.sysinfo_frame = QFrame()
        self.sysinfo_frame.setObjectName("PetrovaCoreFrame")
        sys_layout = QVBoxLayout(self.sysinfo_frame)
        sys_layout.setContentsMargins(10, 8, 10, 8)
        sys_layout.setSpacing(3)

        sys_title = QLabel("SYSTEM INFO")
        sys_title.setObjectName("CoreTitle")
        sys_layout.addWidget(sys_title)

        self.sys_os_lbl = QLabel("OS: Linux")
        self.sys_os_lbl.setObjectName("BlockSubDetail")
        self.sys_kernel_lbl = QLabel("Kernel: 7.x.x")
        self.sys_kernel_lbl.setObjectName("BlockSubDetail")
        self.sys_cpu_lbl = QLabel("CPU: Detected")
        self.sys_cpu_lbl.setObjectName("BlockSubDetail")

        sys_layout.addWidget(self.sys_os_lbl)
        sys_layout.addWidget(self.sys_kernel_lbl)
        sys_layout.addWidget(self.sys_cpu_lbl)

        c_layout.addWidget(self.sysinfo_frame)
        c_layout.addStretch()

        scroll.setWidget(content)
        layout.addWidget(scroll)

    def _create_metric_block(self, label: str):
        frame = QFrame()
        frame.setObjectName("MonitorBlock")
        b_layout = QVBoxLayout(frame)
        b_layout.setContentsMargins(0, 4, 0, 4)
        b_layout.setSpacing(2)

        top = QHBoxLayout()
        lbl = QLabel(label)
        lbl.setObjectName("BlockLabel")
        val = QLabel("--%")
        val.setObjectName("BlockValue")
        top.addWidget(lbl)
        top.addStretch()
        top.addWidget(val)
        b_layout.addLayout(top)

        bar = QLabel(make_led_bar(0))
        bar.setObjectName("LedProgressBar")
        b_layout.addWidget(bar)

        sub1 = QLabel("--")
        sub1.setObjectName("BlockSubDetail")
        sub2 = QLabel("--")
        sub2.setObjectName("BlockSubDetail")
        b_layout.addWidget(sub1)
        b_layout.addWidget(sub2)

        return frame, val, bar, sub1, sub2

    def set_core_status(self, status: str):
        """Update core state (READY, THINKING, PROCESSING, EXECUTING, WAITING, SPEAKING, ERROR)."""
        self.core_status_lbl.setText(status)
        self.core_anim.set_status(status)

    def update_telemetry(self):
        try:
            data = get_system_telemetry()

            # 1. CPU
            cpu_info = data.get("cpu_info", {})
            cores_cnt = cpu_info.get("cores", 12)
            freq_ghz = cpu_info.get("freq_ghz", 3.42)
            load = data.get("load_avg", "")
            load_first = load.split(",")[0] if load else "1.2"
            cpu_pct = min(100, int(float(load_first) * 12)) if load_first else 18
            self.cpu_temp_val.setText(f"{cpu_pct}%")
            self.cpu_bar_lbl.setText(make_led_bar(cpu_pct))
            self.cpu_sub_1.setText(f"Cores: {cores_cnt}")
            self.cpu_sub_2.setText(f"Freq: {freq_ghz:.2f} GHz")

            # 2. Memory
            ram = data.get("ram", {})
            ram_pct = int(ram.get("pct", 0))
            ram_used = ram.get("used_gb", 0.0)
            ram_tot = ram.get("total_gb", 0.0)
            swap_used = ram.get("swap_used_gb", 0.0)
            swap_tot = ram.get("swap_total_gb", 4.0)
            self.ram_val.setText(f"{ram_pct}%")
            self.ram_bar_lbl.setText(make_led_bar(ram_pct))
            self.ram_sub_1.setText(f"Used: {ram_used:.1f} GB / {ram_tot:.0f} GB")
            self.ram_sub_2.setText(f"Swap: {swap_used:.1f} GB / {swap_tot:.0f} GB")

            # 3. GPU
            gpu = data.get("gpu", {})
            gpu_pct = int(gpu.get("utilization_pct", 12))
            gpu_name = gpu.get("name", "Integrated Graphics")
            vram_used = gpu.get("vram_used_gb", 1.2)
            vram_tot = gpu.get("vram_total_gb", 4.0)
            gpu_temp = gpu.get("temp_c", 51)
            self.gpu_val.setText(f"{gpu_pct}%")
            self.gpu_bar_lbl.setText(make_led_bar(gpu_pct))
            self.gpu_sub_1.setText(f"{gpu_name}")
            self.gpu_sub_2.setText(f"VRAM: {vram_used:.1f} GB / {vram_tot:.0f} GB • Temp: {gpu_temp}°C")

            # 4. Storage
            disk = data.get("disk", {})
            disk_pct = int(disk.get("pct", 0))
            disk_used = disk.get("used_gb", 0.0)
            disk_tot = disk.get("total_gb", 0.0)
            disk_free = disk.get("free_gb", 0.0)
            self.disk_val.setText(f"{disk_pct}%")
            self.disk_bar_lbl.setText(make_led_bar(disk_pct))
            self.disk_sub_1.setText(f"Used: {disk_used:.0f} GB / {disk_tot:.0f} GB")
            self.disk_sub_2.setText(f"Free: {disk_free:.0f} GB")

            # 5. Network Speed
            rx, tx = get_network_speed()
            self.net_rates.setText(f"↓ {rx:.1f} MB/s       ↑ {tx:.1f} MB/s")

            # 6. System Info
            distro = data.get("distro", {})
            self.sys_os_lbl.setText(f"OS: {distro.get('pretty_name', 'Linux')}")
            self.sys_kernel_lbl.setText(f"Kernel: {data.get('kernel', 'Linux')}")
            self.sys_cpu_lbl.setText(f"CPU: {cpu_info.get('model', 'Processor')[:24]}")

        except Exception:
            pass
