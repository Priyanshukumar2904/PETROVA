"""
PETROVA Interactive Cognitive Neural Visualizer.
Accurate multi-layer transformer & cognitive topology with real-time token firing,
live audio resonance, spring-damper physics, and mouse interactivity.
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
    def __init__(self, start_pos: QPointF, end_pos: QPointF, speed: float = 0.05, color: QColor = None, size: float = 3.0):
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
    def __init__(self, layer_type: str, layer_idx: int, x: float, y: float, radius: float = 4.0):
        self.layer_type = layer_type  # 'input', 'core', 'output'
        self.layer_idx = layer_idx
        self.x = x
        self.y = y
        self.base_x = x
        self.base_y = y
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.energy = random.uniform(0.15, 0.4)
        self.activation = random.uniform(0.1, 0.5)
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
    Accurate, Interactive Cognitive Neural Topology Widget.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nodes: List[NeuronNode] = []
        self.pulses: List[SynapticPulse] = []
        self.connections: List[Tuple[int, int, float]] = []  # (node_a_idx, node_b_idx, weight)
        self.state = NeuralState.IDLE
        self.status_title = "COGNITIVE ARCHITECTURE"
        self.status_sub = "Idle • Alpha-Wave Monitoring"
        self.phase_text = ""
        
        # Audio resonance
        self.audio_level = 0.0
        self.time_val = 0.0

        # Mouse tracking & Dragging
        self.mouse_pos: Optional[QPointF] = None
        self.hovered_node: Optional[NeuronNode] = None
        self.dragged_node: Optional[NeuronNode] = None
        self.setMouseTracking(True)

        self.setMinimumHeight(115)
        self.setMaximumHeight(135)

        # 60 FPS animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(16)

        self._build_topology()

    def _build_topology(self):
        """Construct a 3-stage cognitive topology (Perception -> Latent Core -> Action)."""
        w = max(self.width(), 800)
        h = max(self.height(), 120)
        self.nodes.clear()
        self.connections.clear()

        # 1. Perception / Input Cluster (Left: x ~ 10% to 22%)
        input_x = w * 0.14
        num_inputs = 5
        for i in range(num_inputs):
            y = h * (0.2 + 0.6 * (i / (num_inputs - 1)))
            node = NeuronNode("input", i, input_x + random.uniform(-15, 15), y, radius=4.5)
            self.nodes.append(node)

        # 2. Cognitive Latent Core (Center Transformer Lattice: x ~ 35% to 65%)
        core_layers = 3
        nodes_per_layer = 4
        core_start_idx = len(self.nodes)
        for col in range(core_layers):
            layer_x = w * (0.35 + 0.15 * col)
            for row in range(nodes_per_layer):
                y = h * (0.22 + 0.56 * (row / (nodes_per_layer - 1))) + (10 if col % 2 == 1 else -10)
                node = NeuronNode("core", col, layer_x + random.uniform(-10, 10), y, radius=4.0)
                self.nodes.append(node)

        # 3. Action / Output Cluster (Right: x ~ 82% to 88%)
        output_x = w * 0.86
        num_outputs = 4
        output_start_idx = len(self.nodes)
        for i in range(num_outputs):
            y = h * (0.25 + 0.5 * (i / (num_outputs - 1)))
            node = NeuronNode("output", i, output_x + random.uniform(-15, 15), y, radius=4.5)
            self.nodes.append(node)

        # 4. Form functional synaptic links between layers
        # Inputs -> First Core Layer
        for inp_i in range(num_inputs):
            for c_i in range(core_start_idx, core_start_idx + nodes_per_layer):
                if random.random() < 0.7:
                    self.connections.append((inp_i, c_i, random.uniform(0.4, 0.9)))

        # Inter-Core Lattice Links
        for col in range(core_layers - 1):
            col1_start = core_start_idx + col * nodes_per_layer
            col2_start = core_start_idx + (col + 1) * nodes_per_layer
            for i in range(nodes_per_layer):
                for j in range(nodes_per_layer):
                    if random.random() < 0.55:
                        self.connections.append((col1_start + i, col2_start + j, random.uniform(0.3, 0.85)))

        # Last Core Layer -> Outputs
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
            self.status_title = "COGNITIVE SYNAPSE: IDLE"
            self.status_sub = "Listening & Ready • 100% Local Inference"
        elif state == NeuralState.INPUT_ACTIVE:
            self.status_title = "PERCEPTION ACTIVE"
            self.status_sub = "Processing Natural Language Query..."
        elif state == NeuralState.THINKING:
            self.status_title = "REASONING & CONTEXT SYNTHESIS"
            self.status_sub = phase_text or "Evaluating System Context & Formulating Plan..."
        elif state == NeuralState.STREAMING:
            self.status_title = "TOKEN STREAM GENERATION"
            self.status_sub = "Active Inference • Zero-Latency Stream"
        elif state == NeuralState.SPEAKING:
            self.status_title = "NEURAL SPEECH ACTIVE"
            self.status_sub = "High-Fidelity Neural Voice Synthesis"
        elif state == NeuralState.COMMAND_EXEC:
            self.status_title = "ACTION ENGINE: EXECUTION"
            self.status_sub = "Running Native Linux Shell Command"
        self.update()

    def fire_token_pulse(self):
        """Called in real-time on every LLM token streamed."""
        # Find input, core, and output node to send genuine token pulse through
        inputs = [i for i, n in enumerate(self.nodes) if n.layer_type == "input"]
        cores = [i for i, n in enumerate(self.nodes) if n.layer_type == "core"]
        outputs = [i for i, n in enumerate(self.nodes) if n.layer_type == "output"]

        if inputs and cores and outputs:
            inp = random.choice(inputs)
            core = random.choice(cores)
            out = random.choice(outputs)

            self.nodes[core].energy = 1.0
            self.nodes[out].energy = 1.0

            # Pulse from Core to Output
            color = QColor(0, 245, 155, 240) if random.random() > 0.3 else QColor(251, 191, 36, 240)
            p1 = QPointF(self.nodes[core].x, self.nodes[core].y)
            p2 = QPointF(self.nodes[out].x, self.nodes[out].y)
            self.pulses.append(SynapticPulse(p1, p2, speed=0.08, color=color, size=3.5))

    def set_audio_level(self, level: float):
        """Microphone volume reactivity."""
        self.audio_level = max(0.0, min(1.0, level))

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position()
        if self.dragged_node:
            self.dragged_node.x = self.mouse_pos.x()
            self.dragged_node.y = self.mouse_pos.y()
            return

        # Check node hover
        hovered = None
        for node in self.nodes:
            d = math.hypot(node.x - self.mouse_pos.x(), node.y - self.mouse_pos.y())
            if d < 18:
                hovered = node
                node.is_hovered = True
            else:
                node.is_hovered = False
        self.hovered_node = hovered

    def mousePressEvent(self, event):
        pos = event.position()
        # Check if clicking on a node to drag
        for node in self.nodes:
            d = math.hypot(node.x - pos.x(), node.y - pos.y())
            if d < 20:
                node.is_dragged = True
                self.dragged_node = node
                break

        # Radial synaptic pulse burst on click
        for i, node in enumerate(self.nodes):
            dist = math.hypot(node.x - pos.x(), node.y - pos.y())
            if dist < 140:
                node.energy = 1.0
                for j, other in enumerate(self.nodes):
                    if i != j and math.hypot(node.x - other.x, node.y - other.y) < 100:
                        p1 = QPointF(node.x, node.y)
                        p2 = QPointF(other.x, other.y)
                        color = QColor(251, 191, 36, 240) if random.random() > 0.5 else QColor(0, 245, 155, 240)
                        self.pulses.append(SynapticPulse(p1, p2, speed=0.06, color=color))

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

        # Update nodes with smooth spring physics
        for node in self.nodes:
            node.phase += 0.04
            # Organic subtle breath oscillation
            if not node.is_dragged:
                osc = math.sin(node.phase) * 1.2
                node.y = node.base_y + osc
            node.update_physics()

        # Update active pulses
        for pulse in self.pulses:
            pulse.update()
        self.pulses = [p for p in self.pulses if not p.finished]

        # Autonomous thinking pulses when active
        if self.state in (NeuralState.THINKING, NeuralState.INPUT_ACTIVE) and random.random() < 0.25:
            if self.connections:
                a_idx, b_idx, weight = random.choice(self.connections)
                p1 = QPointF(self.nodes[a_idx].x, self.nodes[a_idx].y)
                p2 = QPointF(self.nodes[b_idx].x, self.nodes[b_idx].y)
                color = QColor(0, 245, 155, 220) if random.random() > 0.4 else QColor(251, 191, 36, 220)
                self.pulses.append(SynapticPulse(p1, p2, speed=0.05 + 0.03 * weight, color=color))

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        w = self.width()
        h = self.height()

        # 1. Subtle Translucent Backdrop
        bg_grad = QLinearGradient(0, 0, w, h)
        bg_grad.setColorAt(0.0, QColor(8, 14, 20, 220))
        bg_grad.setColorAt(1.0, QColor(4, 7, 10, 240))
        painter.fillRect(self.rect(), bg_grad)

        # 2. Draw Synaptic Interconnection Lines
        for a_idx, b_idx, weight in self.connections:
            na = self.nodes[a_idx]
            nb = self.nodes[b_idx]

            # Line opacity increases if connected nodes have high energy or are hovered
            energy_factor = max(na.energy, nb.energy)
            alpha = int(25 + energy_factor * 120 + (100 if (na.is_hovered or nb.is_hovered) else 0))
            
            pen_color = QColor(16, 185, 129, min(230, alpha))
            if energy_factor > 0.6:
                pen_color = QColor(0, 245, 155, min(240, alpha))
            
            pen = QPen(pen_color, 1.0 + weight * 0.8)
            painter.setPen(pen)
            painter.drawLine(QPointF(na.x, na.y), QPointF(nb.x, nb.y))

        # 3. Draw Traveling Electrical Pulses
        for pulse in self.pulses:
            pos = pulse.current_position()
            # Pulse glow
            glow = QRadialGradient(pos, pulse.size * 3)
            glow.setColorAt(0.0, pulse.color)
            glow.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(glow))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(pos, pulse.size * 2.5, pulse.size * 2.5)

            # Core dot
            painter.setBrush(QBrush(QColor(255, 255, 255, 250)))
            painter.drawEllipse(pos, pulse.size * 0.8, pulse.size * 0.8)

        # 4. Draw Neuron Nodes
        for node in self.nodes:
            pos = QPointF(node.x, node.y)
            r = node.radius + (node.energy * 2.0)

            # Outer glow halo
            if node.energy > 0.3 or node.is_hovered:
                halo_color = QColor(251, 191, 36, 160) if node.energy > 0.8 else QColor(0, 245, 155, 140)
                halo = QRadialGradient(pos, r * 3.5)
                halo.setColorAt(0.0, halo_color)
                halo.setColorAt(1.0, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(halo))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(pos, r * 3, r * 3)

            # Node body
            body_color = QColor(0, 245, 155) if node.layer_type == "input" else \
                         QColor(16, 185, 129) if node.layer_type == "core" else \
                         QColor(251, 191, 36)
            
            painter.setBrush(QBrush(body_color))
            painter.setPen(QPen(QColor(255, 255, 255, 180), 1.2))
            painter.drawEllipse(pos, r, r)

        # 5. Draw Clean Minimalist Header Overlay (Top Center)
        painter.setPen(QColor(0, 245, 155))
        font_title = QFont("-apple-system", 10, QFont.Weight.Bold)
        painter.setFont(font_title)
        painter.drawText(20, 24, self.status_title)

        painter.setPen(QColor(148, 163, 184))
        font_sub = QFont("-apple-system", 9, QFont.Weight.Normal)
        painter.setFont(font_sub)
        painter.drawText(20, 40, self.status_sub)

        # Layer Labels along Bottom
        painter.setPen(QColor(100, 116, 139))
        font_layer = QFont("monospace", 8, QFont.Weight.DemiBold)
        painter.setFont(font_layer)
        painter.drawText(int(w * 0.10), h - 10, "PERCEPTION")
        painter.drawText(int(w * 0.46), h - 10, "TRANSFORMER CORE")
        painter.drawText(int(w * 0.82), h - 10, "ACTION / MOTOR")
