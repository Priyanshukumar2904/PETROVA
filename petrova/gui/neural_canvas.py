"""
PETROVA Monochrome Cognitive Neural Network Topology Widget.
High-contrast black-and-white synaptic lattice featuring real-time token pulse firing,
interactive mouse drag physics, and action-potential waves.
"""

import math
import random
from typing import List, Tuple, Optional
from PyQt6.QtCore import Qt, QTimer, QPointF
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QRadialGradient,
    QFont,
)
from PyQt6.QtWidgets import QFrame

from petrova.gui.styles import COLORS


class SynapticPulse:
    """An electrical action-potential pulse traveling across neural layers."""
    def __init__(self, start_pos: QPointF, end_pos: QPointF, speed: float = 0.06, color: QColor = None, size: float = 3.5):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.progress = 0.0
        self.speed = speed
        self.color = color or QColor(255, 255, 255, 255)
        self.size = size
        self.finished = False

    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.finished = True

    def current_position(self) -> QPointF:
        x = self.start_pos.x() + (self.end_pos.x() - self.start_pos.x()) * self.progress
        y = self.start_pos.y() + (self.end_pos.y() - self.start_pos.y()) * self.progress
        return QPointF(x, y)


class NeuronNode:
    """A computational neuron node."""
    def __init__(self, layer_type: str, layer_idx: int, x: float, y: float, radius: float = 4.5):
        self.layer_type = layer_type  # 'input', 'core', 'output'
        self.layer_idx = layer_idx
        self.x = x
        self.y = y
        self.base_x = x
        self.base_y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.energy = random.uniform(0.2, 0.5)
        self.phase = random.random() * math.pi * 2
        self.is_hovered = False
        self.is_dragged = False

    def update_physics(self, spring: float = 0.03, damping: float = 0.85):
        if self.is_dragged:
            return
        fx = (self.base_x - self.x) * spring
        fy = (self.base_y - self.y) * spring
        self.vx = (self.vx + fx) * damping
        self.vy = (self.vy + fy) * damping
        self.x += self.vx
        self.y += self.vy
        self.energy = max(0.1, self.energy * 0.96)


class NeuralState:
    IDLE = "IDLE"
    INPUT_ACTIVE = "INPUT_ACTIVE"
    THINKING = "THINKING"
    STREAMING = "STREAMING"
    SPEAKING = "SPEAKING"
    COMMAND_EXEC = "COMMAND_EXEC"


class NeuralVisualizerWidget(QFrame):
    """
    Monochrome Cognitive Neural Topology Visualizer.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NeuralCanvasFrame")
        self.nodes: List[NeuronNode] = []
        self.pulses: List[SynapticPulse] = []
        self.connections: List[Tuple[int, int, float]] = []
        self.state = NeuralState.IDLE
        self.status_title = "COGNITIVE SYNAPSE: IDLE"
        self.status_sub = "100% Local Inference • Alpha-Wave Monitoring"
        self.phase_text = ""
        self.audio_level = 0.0
        self.time_val = 0.0

        self.mouse_pos: Optional[QPointF] = None
        self.hovered_node: Optional[NeuronNode] = None
        self.dragged_node: Optional[NeuronNode] = None
        self.setMouseTracking(True)

        self.setFixedHeight(120)
        self.setStyleSheet(f"QFrame#NeuralCanvasFrame {{ background-color: {COLORS['background']}; border: 1px solid {COLORS['border']}; border-radius: 2px; }}")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(16)

        self._build_topology()

    def _build_topology(self):
        w = max(self.width(), 700)
        h = max(self.height(), 120)
        self.nodes.clear()
        self.connections.clear()

        # 1. Perception Cluster (Left)
        input_x = w * 0.12
        num_inputs = 5
        for i in range(num_inputs):
            y = h * (0.2 + 0.6 * (i / (num_inputs - 1)))
            node = NeuronNode("input", i, input_x + random.uniform(-14, 14), y, radius=4.5)
            self.nodes.append(node)

        # 2. Transformer Core Lattice (Center)
        core_layers = 4
        nodes_per_layer = 4
        core_start_idx = len(self.nodes)
        for col in range(core_layers):
            layer_x = w * (0.32 + 0.12 * col)
            for row in range(nodes_per_layer):
                y = h * (0.2 + 0.6 * (row / (nodes_per_layer - 1))) + (10 if col % 2 == 1 else -10)
                node = NeuronNode("core", col, layer_x + random.uniform(-10, 10), y, radius=4.0)
                self.nodes.append(node)

        # 3. Action Cluster (Right)
        output_x = w * 0.88
        num_outputs = 4
        output_start_idx = len(self.nodes)
        for i in range(num_outputs):
            y = h * (0.22 + 0.56 * (i / (num_outputs - 1)))
            node = NeuronNode("output", i, output_x + random.uniform(-14, 14), y, radius=4.5)
            self.nodes.append(node)

        # Form synaptic links
        for inp_i in range(num_inputs):
            for c_i in range(core_start_idx, core_start_idx + nodes_per_layer):
                if random.random() < 0.65:
                    self.connections.append((inp_i, c_i, random.uniform(0.4, 0.9)))

        for col in range(core_layers - 1):
            col1_start = core_start_idx + col * nodes_per_layer
            col2_start = core_start_idx + (col + 1) * nodes_per_layer
            for i in range(nodes_per_layer):
                for j in range(nodes_per_layer):
                    if random.random() < 0.5:
                        self.connections.append((col1_start + i, col2_start + j, random.uniform(0.3, 0.85)))

        last_core_start = core_start_idx + (core_layers - 1) * nodes_per_layer
        for c_i in range(last_core_start, last_core_start + nodes_per_layer):
            for out_i in range(output_start_idx, len(self.nodes)):
                if random.random() < 0.6:
                    self.connections.append((c_i, out_i, random.uniform(0.4, 0.95)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._build_topology()

    def set_state(self, state: str, phase_text: str = ""):
        self.state = state
        self.phase_text = phase_text
        if state == NeuralState.IDLE:
            self.status_title = "COGNITIVE SYNAPSE: IDLE & READY"
            self.status_sub = "100% Local Inference • Alpha-Wave Monitoring"
        elif state == NeuralState.INPUT_ACTIVE:
            self.status_title = "PERCEPTION RECEPTORS ACTIVE"
            self.status_sub = "Processing Prompt Input & Query Context..."
        elif state == NeuralState.THINKING:
            self.status_title = "CONTEXT SYNTHESIS & REASONING"
            self.status_sub = phase_text or "Evaluating System Context & Formulating Execution Plan..."
        elif state == NeuralState.STREAMING:
            self.status_title = "REAL-TIME TOKEN STREAMING"
            self.status_sub = "Active Inference • Live Synaptic Emission"
        elif state == NeuralState.SPEAKING:
            self.status_title = "NEURAL VOICE SYNTHESIS"
            self.status_sub = "High-Fidelity Audio Stream Active"
        elif state == NeuralState.COMMAND_EXEC:
            self.status_title = "ACTION ENGINE: EXECUTION"
            self.status_sub = "Executing Native Linux System Command"
        self.update()

    def fire_token_pulse(self):
        inputs = [i for i, n in enumerate(self.nodes) if n.layer_type == "input"]
        cores = [i for i, n in enumerate(self.nodes) if n.layer_type == "core"]
        outputs = [i for i, n in enumerate(self.nodes) if n.layer_type == "output"]

        if inputs and cores and outputs:
            core = random.choice(cores)
            out = random.choice(outputs)
            self.nodes[core].energy = 1.0
            self.nodes[out].energy = 1.0

            p1 = QPointF(self.nodes[core].x, self.nodes[core].y)
            p2 = QPointF(self.nodes[out].x, self.nodes[out].y)
            self.pulses.append(SynapticPulse(p1, p2, speed=0.09, color=QColor(255, 255, 255, 255), size=3.8))

    def set_audio_level(self, level: float):
        self.audio_level = max(0.0, min(1.0, level))

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position()
        if self.dragged_node:
            self.dragged_node.x = self.mouse_pos.x()
            self.dragged_node.y = self.mouse_pos.y()
            return

        hovered = None
        for node in self.nodes:
            d = math.hypot(node.x - self.mouse_pos.x(), node.y - self.mouse_pos.y())
            if d < 20:
                hovered = node
                node.is_hovered = True
            else:
                node.is_hovered = False
        self.hovered_node = hovered

    def mousePressEvent(self, event):
        pos = event.position()
        for node in self.nodes:
            d = math.hypot(node.x - pos.x(), node.y - pos.y())
            if d < 20:
                node.is_dragged = True
                self.dragged_node = node
                break

        for i, node in enumerate(self.nodes):
            dist = math.hypot(node.x - pos.x(), node.y - pos.y())
            if dist < 140:
                node.energy = 1.0
                for j, other in enumerate(self.nodes):
                    if i != j and math.hypot(node.x - other.x, node.y - other.y) < 110:
                        p1 = QPointF(node.x, node.y)
                        p2 = QPointF(other.x, other.y)
                        self.pulses.append(SynapticPulse(p1, p2, speed=0.07, color=QColor(255, 255, 255, 240), size=3.5))

    def mouseReleaseEvent(self, event):
        if self.dragged_node:
            self.dragged_node.is_dragged = False
            self.dragged_node = None

    def leaveEvent(self, event):
        self.mouse_pos = None
        self.hovered_node = None
        if self.dragged_node:
            self.dragged_node.is_dragged = False
            self.dragged_node = None

    def _on_tick(self):
        self.time_val += 0.03

        for node in self.nodes:
            node.phase += 0.04
            if not node.is_dragged:
                osc = math.sin(node.phase) * 1.2
                node.y = node.base_y + osc
            node.update_physics()

        for pulse in self.pulses:
            pulse.update()
        self.pulses = [p for p in self.pulses if not p.finished]

        if self.state in (NeuralState.THINKING, NeuralState.INPUT_ACTIVE) and random.random() < 0.25:
            if self.connections:
                a_idx, b_idx, weight = random.choice(self.connections)
                p1 = QPointF(self.nodes[a_idx].x, self.nodes[a_idx].y)
                p2 = QPointF(self.nodes[b_idx].x, self.nodes[b_idx].y)
                self.pulses.append(SynapticPulse(p1, p2, speed=0.05 + 0.03 * weight, color=QColor(255, 255, 255, 220)))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        painter.fillRect(self.rect(), QColor(COLORS["background"]))

        # 1. Synaptic Lines
        for a_idx, b_idx, weight in self.connections:
            na = self.nodes[a_idx]
            nb = self.nodes[b_idx]
            energy_factor = max(na.energy, nb.energy)
            alpha = int(35 + energy_factor * 160 + (60 if (na.is_hovered or nb.is_hovered) else 0))
            
            pen = QPen(QColor(255, 255, 255, min(255, alpha)), 1.0 + weight * 0.8)
            painter.setPen(pen)
            painter.drawLine(QPointF(na.x, na.y), QPointF(nb.x, nb.y))

        # 2. Traveling Electrical Action-Potentials
        for pulse in self.pulses:
            pos = pulse.current_position()
            glow = QRadialGradient(pos, pulse.size * 3.0)
            glow.setColorAt(0.0, QColor(255, 255, 255, 240))
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(pos, pulse.size * 2.5, pulse.size * 2.5)

            painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
            painter.drawEllipse(pos, pulse.size * 0.9, pulse.size * 0.9)

        # 3. Neuron Nodes
        for node in self.nodes:
            pos = QPointF(node.x, node.y)
            r = node.radius + (node.energy * 2.0)

            if node.energy > 0.3 or node.is_hovered:
                halo = QRadialGradient(pos, r * 3.0)
                halo.setColorAt(0.0, QColor(255, 255, 255, 140))
                halo.setColorAt(1.0, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(halo))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(pos, r * 2.8, r * 2.8)

            body_color = QColor(255, 255, 255) if node.layer_type in ("input", "output") else QColor(189, 189, 189)
            painter.setBrush(QBrush(body_color))
            painter.setPen(QPen(QColor(0, 0, 0), 1.2))
            painter.drawEllipse(pos, r, r)

        # 4. Monochrome Header
        painter.setPen(QColor(COLORS["foreground"]))
        font_title = QFont("JetBrains Mono", 10, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.drawText(16, 22, self.status_title)

        painter.setPen(QColor(COLORS["muted"]))
        font_sub = QFont("JetBrains Mono", 9, QFont.Weight.Normal)
        painter.setFont(font_sub)
        painter.drawText(16, 38, self.status_sub)

        # 5. Layer labels
        painter.setPen(QColor(COLORS["muted"]))
        font_layer = QFont("JetBrains Mono", 8, QFont.Weight.Bold)
        painter.setFont(font_layer)
        painter.drawText(int(w * 0.08), h - 8, "PERCEPTION")
        painter.drawText(int(w * 0.45), h - 8, "TRANSFORMER CORE")
        painter.drawText(int(w * 0.82), h - 8, "ACTION MOTOR")
