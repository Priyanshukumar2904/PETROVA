"""
PETROVA Compact Monochrome Cognitive Neural Network Topology Widget.
Fits cleanly inside the top Greeting Panel empty space without clutter or overlap.
Features interactive synaptic lattice, real-time token pulse firing, and node dynamics.
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
from PyQt6.QtWidgets import QWidget, QFrame

from petrova.gui.styles import COLORS


class SynapticPulse:
    """An electrical action-potential pulse traveling across neural layers."""
    def __init__(self, start_pos: QPointF, end_pos: QPointF, speed: float = 0.08, color: QColor = None, size: float = 3.0):
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
    def __init__(self, layer_type: str, layer_idx: int, x: float, y: float, radius: float = 3.5):
        self.layer_type = layer_type
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

    def update_physics(self, spring: float = 0.04, damping: float = 0.85):
        if self.is_dragged:
            return
        fx = (self.base_x - self.x) * spring
        fy = (self.base_y - self.y) * spring
        self.vx = (self.vx + fx) * damping
        self.vy = (self.vy + fy) * damping
        self.x += self.vx
        self.y += self.vy
        self.energy = max(0.1, self.energy * 0.95)


class NeuralState:
    IDLE = "IDLE"
    INPUT_ACTIVE = "INPUT_ACTIVE"
    THINKING = "THINKING"
    STREAMING = "STREAMING"
    SPEAKING = "SPEAKING"
    COMMAND_EXEC = "COMMAND_EXEC"


class CompactNeuralWidget(QWidget):
    """
    Compact interactive neural network canvas designed specifically to fit
    inside the right empty space of the top Greeting Panel.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes: List[NeuronNode] = []
        self.pulses: List[SynapticPulse] = []
        self.connections: List[Tuple[int, int, float]] = []
        self.state = NeuralState.IDLE
        self.status_title = "COGNITIVE SYNAPSE: READY"
        self.status_sub = "Local Inference • Synaptic Lattice"
        self.phase_text = ""
        self.audio_level = 0.0
        self.time_val = 0.0

        self.mouse_pos: Optional[QPointF] = None
        self.hovered_node: Optional[NeuronNode] = None
        self.dragged_node: Optional[NeuronNode] = None
        self.setMouseTracking(True)

        self.setFixedHeight(54)
        self.setMinimumWidth(260)
        self.setMaximumWidth(420)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(18)

        self._build_topology()

    def _build_topology(self):
        w = max(self.width(), 280)
        h = max(self.height(), 54)
        self.nodes.clear()
        self.connections.clear()

        # 1. Perception Cluster (Left)
        num_inputs = 3
        for i in range(num_inputs):
            y = h * (0.22 + 0.56 * (i / (num_inputs - 1)))
            node = NeuronNode("input", i, 16 + random.uniform(-4, 4), y, radius=3.2)
            self.nodes.append(node)

        # 2. Transformer Core (Center Columns)
        core_layers = 3
        nodes_per_layer = 3
        core_start_idx = len(self.nodes)
        for col in range(core_layers):
            layer_x = 55 + col * ((w - 90) / max(1, core_layers))
            for row in range(nodes_per_layer):
                y = h * (0.2 + 0.6 * (row / (nodes_per_layer - 1))) + (4 if col % 2 == 1 else -4)
                node = NeuronNode("core", col, layer_x + random.uniform(-4, 4), y, radius=3.0)
                self.nodes.append(node)

        # 3. Action Cluster (Right)
        num_outputs = 3
        output_start_idx = len(self.nodes)
        for i in range(num_outputs):
            y = h * (0.22 + 0.56 * (i / (num_outputs - 1)))
            node = NeuronNode("output", i, w - 16 + random.uniform(-4, 4), y, radius=3.2)
            self.nodes.append(node)

        # Connect Synapses
        for inp_i in range(num_inputs):
            for c_i in range(core_start_idx, core_start_idx + nodes_per_layer):
                if random.random() < 0.7:
                    self.connections.append((inp_i, c_i, random.uniform(0.4, 0.9)))

        for col in range(core_layers - 1):
            col1 = core_start_idx + col * nodes_per_layer
            col2 = core_start_idx + (col + 1) * nodes_per_layer
            for i in range(nodes_per_layer):
                for j in range(nodes_per_layer):
                    if random.random() < 0.55:
                        self.connections.append((col1 + i, col2 + j, random.uniform(0.3, 0.85)))

        last_col = core_start_idx + (core_layers - 1) * nodes_per_layer
        for c_i in range(last_col, last_col + nodes_per_layer):
            for out_i in range(output_start_idx, len(self.nodes)):
                if random.random() < 0.7:
                    self.connections.append((c_i, out_i, random.uniform(0.4, 0.95)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._build_topology()

    def set_state(self, state: str, phase_text: str = ""):
        self.state = state
        self.phase_text = phase_text
        if phase_text:
            self.status_sub = phase_text
        elif state == NeuralState.IDLE:
            self.status_title = "COGNITIVE SYNAPSE: READY"
            self.status_sub = "Local Inference • Synaptic Lattice"
        elif state == NeuralState.INPUT_ACTIVE:
            self.status_title = "PERCEPTION RECEPTORS ACTIVE"
            self.status_sub = "Processing Prompt Context..."
        elif state == NeuralState.THINKING:
            self.status_title = "SYNTHESIS & REASONING"
            self.status_sub = "Evaluating System Context..."
        elif state == NeuralState.STREAMING:
            self.status_title = "ACTIVE SYNAPTIC EMISSION"
            self.status_sub = "Active Inference Stream"
        elif state == NeuralState.SPEAKING:
            self.status_title = "NEURAL VOICE SYNTHESIS"
            self.status_sub = "Audio Stream Active"
        elif state == NeuralState.COMMAND_EXEC:
            self.status_title = "ACTION ENGINE: EXECUTION"
            self.status_sub = "Executing Linux Command"
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
            self.pulses.append(SynapticPulse(p1, p2, speed=0.10, color=QColor(255, 255, 255, 255), size=3.2))

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
            if d < 16:
                hovered = node
                node.is_hovered = True
            else:
                node.is_hovered = False
        self.hovered_node = hovered

    def mousePressEvent(self, event):
        pos = event.position()
        for node in self.nodes:
            d = math.hypot(node.x - pos.x(), node.y - pos.y())
            if d < 16:
                node.is_dragged = True
                self.dragged_node = node
                break

        for i, node in enumerate(self.nodes):
            dist = math.hypot(node.x - pos.x(), node.y - pos.y())
            if dist < 80:
                node.energy = 1.0
                for j, other in enumerate(self.nodes):
                    if i != j and math.hypot(node.x - other.x, node.y - other.y) < 70:
                        p1 = QPointF(node.x, node.y)
                        p2 = QPointF(other.x, other.y)
                        self.pulses.append(SynapticPulse(p1, p2, speed=0.08, color=QColor(255, 255, 255, 240), size=3.0))

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
            node.phase += 0.05
            if not node.is_dragged:
                osc = math.sin(node.phase) * 0.8
                node.y = node.base_y + osc
            node.update_physics()

        for pulse in self.pulses:
            pulse.update()
        self.pulses = [p for p in self.pulses if not p.finished]

        if self.state in (NeuralState.THINKING, NeuralState.INPUT_ACTIVE) and random.random() < 0.2:
            if self.connections:
                a_idx, b_idx, weight = random.choice(self.connections)
                p1 = QPointF(self.nodes[a_idx].x, self.nodes[a_idx].y)
                p2 = QPointF(self.nodes[b_idx].x, self.nodes[b_idx].y)
                self.pulses.append(SynapticPulse(p1, p2, speed=0.06 + 0.03 * weight, color=QColor(255, 255, 255, 220)))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. Synaptic Lines
        for a_idx, b_idx, weight in self.connections:
            na = self.nodes[a_idx]
            nb = self.nodes[b_idx]
            energy_factor = max(na.energy, nb.energy)
            alpha = int(40 + energy_factor * 160 + (50 if (na.is_hovered or nb.is_hovered) else 0))
            
            pen = QPen(QColor(255, 255, 255, min(255, alpha)), 1.0 + weight * 0.5)
            painter.setPen(pen)
            painter.drawLine(QPointF(na.x, na.y), QPointF(nb.x, nb.y))

        # 2. Traveling Electrical Action-Potentials
        for pulse in self.pulses:
            pos = pulse.current_position()
            glow = QRadialGradient(pos, pulse.size * 2.5)
            glow.setColorAt(0.0, QColor(255, 255, 255, 240))
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(pos, pulse.size * 2.0, pulse.size * 2.0)

            painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
            painter.drawEllipse(pos, pulse.size * 0.8, pulse.size * 0.8)

        # 3. Neuron Nodes
        for node in self.nodes:
            pos = QPointF(node.x, node.y)
            r = node.radius + (node.energy * 1.5)

            if node.energy > 0.3 or node.is_hovered:
                halo = QRadialGradient(pos, r * 2.5)
                halo.setColorAt(0.0, QColor(255, 255, 255, 130))
                halo.setColorAt(1.0, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(halo))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(pos, r * 2.2, r * 2.2)

            body_color = QColor(255, 255, 255) if node.layer_type in ("input", "output") else QColor(189, 189, 189)
            painter.setBrush(QBrush(body_color))
            painter.setPen(QPen(QColor(0, 0, 0), 1.0))
            painter.drawEllipse(pos, r, r)


# Backwards compatibility alias
NeuralVisualizerWidget = CompactNeuralWidget
