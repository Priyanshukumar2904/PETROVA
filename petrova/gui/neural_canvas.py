"""
PETROVA Interactive Cognitive Neural Visualizer.
Expansive multi-layer transformer & cognitive topology spanning the full workspace,
featuring real-time token firing, live audio resonance, spring-damper physics, and mouse interactivity.
"""

import math
import random
import time
from typing import List, Tuple, Optional
from PyQt6.QtCore import Qt, QTimer, QPointF, pyqtSlot
from PyQt6.QtGui import (
    QPainter,
    QColor,
    QPen,
    QBrush,
    QRadialGradient,
    QLinearGradient,
    QFont,
    QPainterPath,
)
from PyQt6.QtWidgets import QWidget


class SynapticPulse:
    """An electrical action-potential pulse traveling across neural layers."""
    def __init__(self, start_pos: QPointF, end_pos: QPointF, speed: float = 0.05, color: QColor = None, size: float = 3.5):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.progress = 0.0  # 0.0 to 1.0
        self.speed = speed
        self.color = color or QColor(0, 245, 155, 230)
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
    """A functional computational neuron inside the cognitive topology."""
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
        self.activation = random.uniform(0.2, 0.6)
        self.phase = random.random() * math.pi * 2
        self.is_hovered = False
        self.is_dragged = False

    def update_physics(self, spring: float = 0.03, damping: float = 0.85):
        if self.is_dragged:
            return
        # Spring force back to base position
        fx = (self.base_x - self.x) * spring
        fy = (self.base_y - self.y) * spring
        self.vx = (self.vx + fx) * damping
        self.vy = (self.vy + fy) * damping
        self.x += self.vx
        self.y += self.vy
        # Energy decay
        self.energy = max(0.1, self.energy * 0.96)


class NeuralState:
    IDLE = "IDLE"
    INPUT_ACTIVE = "INPUT_ACTIVE"
    THINKING = "THINKING"
    STREAMING = "STREAMING"
    SPEAKING = "SPEAKING"
    COMMAND_EXEC = "COMMAND_EXEC"


class NeuralVisualizerWidget(QWidget):
    """
    Expansive, Full-Width Cognitive Neural Topology Widget.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes: List[NeuronNode] = []
        self.pulses: List[SynapticPulse] = []
        self.connections: List[Tuple[int, int, float]] = []  # (node_a_idx, node_b_idx, weight)
        self.state = NeuralState.IDLE
        self.status_title = "COGNITIVE SYNAPSE: IDLE"
        self.status_sub = "100% Local Inference • Real-time Sysfs & Kernel Telemetry Active"
        self.phase_text = ""
        
        # Audio resonance
        self.audio_level = 0.0
        self.time_val = 0.0

        # Mouse tracking & Dragging
        self.mouse_pos: Optional[QPointF] = None
        self.hovered_node: Optional[NeuronNode] = None
        self.dragged_node: Optional[NeuronNode] = None
        self.setMouseTracking(True)

        self.setMinimumHeight(140)
        self.setMaximumHeight(165)

        # 60 FPS animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(16)

        self._build_topology()

    def _build_topology(self):
        """Construct a spacious, full-width cognitive topology."""
        w = max(self.width(), 850)
        h = max(self.height(), 140)
        self.nodes.clear()
        self.connections.clear()

        # 1. Perception Cluster (Left: x ~ 10% to 20%)
        input_x = w * 0.12
        num_inputs = 6
        for i in range(num_inputs):
            y = h * (0.18 + 0.64 * (i / (num_inputs - 1)))
            node = NeuronNode("input", i, input_x + random.uniform(-18, 18), y, radius=5.0)
            self.nodes.append(node)

        # 2. Transformer Latent Lattice (Center: x ~ 32% to 68%)
        core_layers = 4
        nodes_per_layer = 4
        core_start_idx = len(self.nodes)
        for col in range(core_layers):
            layer_x = w * (0.32 + 0.12 * col)
            for row in range(nodes_per_layer):
                y = h * (0.2 + 0.6 * (row / (nodes_per_layer - 1))) + (12 if col % 2 == 1 else -12)
                node = NeuronNode("core", col, layer_x + random.uniform(-12, 12), y, radius=4.5)
                self.nodes.append(node)

        # 3. Motor / Action Cluster (Right: x ~ 84% to 90%)
        output_x = w * 0.88
        num_outputs = 5
        output_start_idx = len(self.nodes)
        for i in range(num_outputs):
            y = h * (0.2 + 0.6 * (i / (num_outputs - 1)))
            node = NeuronNode("output", i, output_x + random.uniform(-18, 18), y, radius=5.0)
            self.nodes.append(node)

        # 4. Form functional synaptic links
        # Perception -> Core
        for inp_i in range(num_inputs):
            for c_i in range(core_start_idx, core_start_idx + nodes_per_layer):
                if random.random() < 0.7:
                    self.connections.append((inp_i, c_i, random.uniform(0.4, 0.95)))

        # Inter-Core Layers
        for col in range(core_layers - 1):
            col1_start = core_start_idx + col * nodes_per_layer
            col2_start = core_start_idx + (col + 1) * nodes_per_layer
            for i in range(nodes_per_layer):
                for j in range(nodes_per_layer):
                    if random.random() < 0.5:
                        self.connections.append((col1_start + i, col2_start + j, random.uniform(0.3, 0.85)))

        # Core -> Action Cluster
        last_core_start = core_start_idx + (core_layers - 1) * nodes_per_layer
        for c_i in range(last_core_start, last_core_start + nodes_per_layer):
            for out_i in range(output_start_idx, len(self.nodes)):
                if random.random() < 0.65:
                    self.connections.append((c_i, out_i, random.uniform(0.4, 0.95)))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._build_topology()

    def set_state(self, state: str, phase_text: str = ""):
        """Update operational cognitive state."""
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
            self.status_sub = "High-Fidelity Neural Audio Stream Active"
        elif state == NeuralState.COMMAND_EXEC:
            self.status_title = "ACTION ENGINE: EXECUTION"
            self.status_sub = "Executing Native Linux System Command"
        self.update()

    def fire_token_pulse(self):
        """Called in real-time on every LLM token streamed."""
        inputs = [i for i, n in enumerate(self.nodes) if n.layer_type == "input"]
        cores = [i for i, n in enumerate(self.nodes) if n.layer_type == "core"]
        outputs = [i for i, n in enumerate(self.nodes) if n.layer_type == "output"]

        if inputs and cores and outputs:
            inp = random.choice(inputs)
            core = random.choice(cores)
            out = random.choice(outputs)

            self.nodes[core].energy = 1.0
            self.nodes[out].energy = 1.0

            color = QColor(0, 245, 155, 245) if random.random() > 0.3 else QColor(251, 191, 36, 245)
            p1 = QPointF(self.nodes[core].x, self.nodes[core].y)
            p2 = QPointF(self.nodes[out].x, self.nodes[out].y)
            self.pulses.append(SynapticPulse(p1, p2, speed=0.08, color=color, size=4.0))

    def set_audio_level(self, level: float):
        """Microphone volume reactivity."""
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
            if d < 22:
                hovered = node
                node.is_hovered = True
            else:
                node.is_hovered = False
        self.hovered_node = hovered

    def mousePressEvent(self, event):
        pos = event.position()
        for node in self.nodes:
            d = math.hypot(node.x - pos.x(), node.y - pos.y())
            if d < 22:
                node.is_dragged = True
                self.dragged_node = node
                break

        for i, node in enumerate(self.nodes):
            dist = math.hypot(node.x - pos.x(), node.y - pos.y())
            if dist < 160:
                node.energy = 1.0
                for j, other in enumerate(self.nodes):
                    if i != j and math.hypot(node.x - other.x, node.y - other.y) < 120:
                        p1 = QPointF(node.x, node.y)
                        p2 = QPointF(other.x, other.y)
                        color = QColor(251, 191, 36, 240) if random.random() > 0.5 else QColor(0, 245, 155, 240)
                        self.pulses.append(SynapticPulse(p1, p2, speed=0.06, color=color, size=4.0))

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
                osc = math.sin(node.phase) * 1.5
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
                color = QColor(0, 245, 155, 220) if random.random() > 0.4 else QColor(251, 191, 36, 220)
                self.pulses.append(SynapticPulse(p1, p2, speed=0.05 + 0.03 * weight, color=color, size=3.5))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        # 1. Subtle Translucent Backdrop
        bg_grad = QLinearGradient(0, 0, w, h)
        bg_grad.setColorAt(0.0, QColor(9, 14, 20, 230))
        bg_grad.setColorAt(1.0, QColor(5, 8, 12, 245))
        painter.fillRect(self.rect(), bg_grad)

        # 2. Draw Synaptic Interconnection Lines
        for a_idx, b_idx, weight in self.connections:
            na = self.nodes[a_idx]
            nb = self.nodes[b_idx]

            energy_factor = max(na.energy, nb.energy)
            alpha = int(30 + energy_factor * 130 + (120 if (na.is_hovered or nb.is_hovered) else 0))
            
            pen_color = QColor(16, 185, 129, min(240, alpha))
            if energy_factor > 0.6:
                pen_color = QColor(0, 245, 155, min(250, alpha))
            
            pen = QPen(pen_color, 1.2 + weight * 0.9)
            painter.setPen(pen)
            painter.drawLine(QPointF(na.x, na.y), QPointF(nb.x, nb.y))

        # 3. Draw Traveling Electrical Pulses
        for pulse in self.pulses:
            pos = pulse.current_position()
            glow = QRadialGradient(pos, pulse.size * 3.5)
            glow.setColorAt(0.0, pulse.color)
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(pos, pulse.size * 3, pulse.size * 3)

            painter.setBrush(QBrush(QColor(255, 255, 255, 255)))
            painter.drawEllipse(pos, pulse.size * 0.9, pulse.size * 0.9)

        # 4. Draw Neuron Nodes
        for node in self.nodes:
            pos = QPointF(node.x, node.y)
            r = node.radius + (node.energy * 2.5)

            if node.energy > 0.3 or node.is_hovered:
                halo_color = QColor(251, 191, 36, 170) if node.energy > 0.8 else QColor(0, 245, 155, 150)
                halo = QRadialGradient(pos, r * 3.5)
                halo.setColorAt(0.0, halo_color)
                halo.setColorAt(1.0, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(halo))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(pos, r * 3.2, r * 3.2)

            body_color = QColor(0, 245, 155) if node.layer_type == "input" else \
                         QColor(16, 185, 129) if node.layer_type == "core" else \
                         QColor(251, 191, 36)
            
            painter.setBrush(QBrush(body_color))
            painter.setPen(QPen(QColor(255, 255, 255, 200), 1.5))
            painter.drawEllipse(pos, r, r)

        # 5. Prominent Clear Header Overlay (Top Left)
        painter.setPen(QColor(0, 245, 155))
        font_title = QFont("-apple-system", 11, QFont.Weight.ExtraBold)
        painter.setFont(font_title)
        painter.drawText(24, 28, self.status_title)

        painter.setPen(QColor(148, 163, 184))
        font_sub = QFont("-apple-system", 10, QFont.Weight.DemiBold)
        painter.setFont(font_sub)
        painter.drawText(24, 48, self.status_sub)

        # Layer Labels along Bottom
        painter.setPen(QColor(100, 116, 139))
        font_layer = QFont("monospace", 9, QFont.Weight.Bold)
        painter.setFont(font_layer)
        painter.drawText(int(w * 0.08), h - 12, "PERCEPTION CLUSTER")
        painter.drawText(int(w * 0.44), h - 12, "TRANSFORMER REASONING CORE")
        painter.drawText(int(w * 0.80), h - 12, "ACTION / MOTOR CLUSTER")
