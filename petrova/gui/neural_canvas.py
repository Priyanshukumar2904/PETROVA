"""
PETROVA Neural Activity & Synaptic Thought Visualizer.
Renders an animated, organic neural constellation with synaptic pulses,
showing real-time thinking states, voice waveforms, and idle breathing.
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
    """An electrical action-potential pulse traveling along a synapse."""
    def __init__(self, start_idx: int, end_idx: int, speed: float = 0.04, color: QColor = None):
        self.start_idx = start_idx
        self.end_idx = end_idx
        self.progress = 0.0  # 0.0 to 1.0
        self.speed = speed
        self.color = color or QColor(0, 240, 255, 220)
        self.finished = False

    def update(self):
        self.progress += self.speed
        if self.progress >= 1.0:
            self.finished = True


class NeuralNode:
    """A neuron node in the neural network."""
    def __init__(self, x: float, y: float, radius: float = 3.5):
        self.x = x
        self.y = y
        self.base_x = x
        self.base_y = y
        self.vx = (random.random() - 0.5) * 0.4
        self.vy = (random.random() - 0.5) * 0.4
        self.radius = radius
        self.energy = random.random() * 0.5
        self.pulse_phase = random.random() * math.pi * 2


class NeuralState:
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    SPEAKING = "SPEAKING"


class NeuralVisualizerWidget(QWidget):
    """
    Custom animated QWidget displaying PETROVA's internal neural thinking patterns.
    """
    def __init__(self, parent=None, num_nodes: int = 36):
        super().__init__(parent)
        self.num_nodes = num_nodes
        self.nodes: List[NeuralNode] = []
        self.pulses: List[SynapticPulse] = []
        self.state = NeuralState.IDLE
        self.status_text = "PETROVA Synaptic Core: Idle"
        self.phase_text = ""
        
        # Audio / resonance reactivity
        self.audio_level = 0.0  # 0.0 to 1.0
        self.time_offset = 0.0

        self.mouse_pos: Optional[QPointF] = None
        self.setMouseTracking(True)

        self.setMinimumHeight(110)
        self.setMaximumHeight(140)

        # 60 FPS animation timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(16)

        self._init_nodes()

    def _init_nodes(self):
        w = max(self.width(), 600)
        h = max(self.height(), 120)
        self.nodes.clear()
        for _ in range(self.num_nodes):
            x = random.uniform(20, w - 20)
            y = random.uniform(15, h - 15)
            r = random.uniform(2.5, 4.5)
            self.nodes.append(NeuralNode(x, y, r))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = self.width()
        h = self.height()
        for node in self.nodes:
            node.x = max(10, min(w - 10, node.x))
            node.y = max(10, min(h - 10, node.y))
            node.base_x = node.x
            node.base_y = node.y

    def set_state(self, state: str, phase_text: str = ""):
        """Update neural operational state."""
        self.state = state
        self.phase_text = phase_text
        if state == NeuralState.IDLE:
            self.status_text = "PETROVA Synaptic Core: Idle & Listening"
        elif state == NeuralState.LISTENING:
            self.status_text = "🎙️ Neural Audio Receptor Active: Listening to Voice..."
        elif state == NeuralState.THINKING:
            self.status_text = f"⚡ Neural Synthesis Active: {phase_text or 'Reasoning & Evaluating Context'}"
        elif state == NeuralState.SPEAKING:
            self.status_text = "🔊 Synaptic Speech Stream: Responding..."
        self.update()

    def set_audio_level(self, level: float):
        """Set voice microphone loudness level for audio reactivity."""
        self.audio_level = max(0.0, min(1.0, level))

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.position()

    def leaveEvent(self, event):
        self.mouse_pos = None

    def mousePressEvent(self, event):
        # Trigger an interactive burst of synaptic pulses on click
        w = self.width()
        h = self.height()
        pos = event.position()
        for i, node in enumerate(self.nodes):
            dist = math.hypot(node.x - pos.x(), node.y - pos.y())
            if dist < 120:
                node.energy = 1.0
                # Spawn pulses to neighboring nodes
                for j, other in enumerate(self.nodes):
                    if i != j and math.hypot(node.x - other.x, node.y - other.y) < 90:
                        self.pulses.append(SynapticPulse(i, j, speed=0.06, color=QColor(0, 255, 180, 240)))

    def _on_tick(self):
        self.time_offset += 0.025
        w = max(self.width(), 100)
        h = max(self.height(), 60)

        # 1. Update nodes
        speed_multiplier = 1.0
        if self.state == NeuralState.THINKING:
            speed_multiplier = 2.4
        elif self.state == NeuralState.LISTENING:
            speed_multiplier = 1.6

        for i, node in enumerate(self.nodes):
            node.pulse_phase += 0.04 * speed_multiplier
            node.x += node.vx * speed_multiplier
            node.y += node.vy * speed_multiplier

            # Bounce off edges
            if node.x < 15 or node.x > w - 15:
                node.vx *= -1
            if node.y < 15 or node.y > h - 15:
                node.vy *= -1

            # Mouse interaction gravity
            if self.mouse_pos:
                dx = self.mouse_pos.x() - node.x
                dy = self.mouse_pos.y() - node.y
                d = math.hypot(dx, dy)
                if d < 100 and d > 2:
                    node.x += (dx / d) * 0.4
                    node.y += (dy / d) * 0.4

            # Energy decay
            node.energy = max(0.1, node.energy * 0.98)

        # 2. Spawn random synaptic pulses based on state
        if self.state == NeuralState.THINKING and random.random() < 0.35:
            start = random.randint(0, len(self.nodes) - 1)
            # Find close neighbor
            neighbors = []
            for idx, other in enumerate(self.nodes):
                if idx != start:
                    d = math.hypot(self.nodes[start].x - other.x, self.nodes[start].y - other.y)
                    if d < 110:
                        neighbors.append(idx)
            if neighbors:
                end = random.choice(neighbors)
                color = QColor(168, 85, 247, 240) if random.random() > 0.5 else QColor(0, 240, 255, 240)
                self.pulses.append(SynapticPulse(start, end, speed=random.uniform(0.04, 0.08), color=color))

        elif self.state == NeuralState.LISTENING and random.random() < 0.2:
            start = random.randint(0, len(self.nodes) - 1)
            neighbors = [idx for idx, other in enumerate(self.nodes) if idx != start and math.hypot(self.nodes[start].x - other.x, self.nodes[start].y - other.y) < 90]
            if neighbors:
                self.pulses.append(SynapticPulse(start, random.choice(neighbors), speed=0.05, color=QColor(0, 255, 175, 230)))

        elif self.state == NeuralState.IDLE and random.random() < 0.04:
            start = random.randint(0, len(self.nodes) - 1)
            neighbors = [idx for idx, other in enumerate(self.nodes) if idx != start and math.hypot(self.nodes[start].x - other.x, self.nodes[start].y - other.y) < 80]
            if neighbors:
                self.pulses.append(SynapticPulse(start, random.choice(neighbors), speed=0.03, color=QColor(0, 240, 255, 160)))

        # 3. Update pulses
        for pulse in self.pulses:
            pulse.update()
        self.pulses = [p for p in self.pulses if not p.finished]

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        # Background Gradient
        bg_grad = QLinearGradient(0, 0, w, h)
        bg_grad.setColorAt(0.0, QColor(10, 14, 23))
        bg_grad.setColorAt(0.5, QColor(14, 20, 32))
        bg_grad.setColorAt(1.0, QColor(8, 11, 18))
        painter.fillRect(0, 0, w, h, bg_grad)

        # Border
        painter.setPen(QPen(QColor(30, 41, 59, 180), 1))
        painter.drawRect(0, 0, w - 1, h - 1)

        # Draw Synaptic Connections (Lines)
        max_dist = 95
        if self.state == NeuralState.THINKING:
            max_dist = 115
        elif self.state == NeuralState.LISTENING:
            max_dist = 105

        for i in range(len(self.nodes)):
            n1 = self.nodes[i]
            for j in range(i + 1, len(self.nodes)):
                n2 = self.nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < max_dist:
                    alpha = int((1.0 - (dist / max_dist)) * 140)
                    
                    if self.state == NeuralState.THINKING:
                        line_color = QColor(140, 70, 255, min(255, alpha + 50))
                    elif self.state == NeuralState.LISTENING:
                        line_color = QColor(0, 255, 175, min(255, alpha + 40))
                    else:
                        line_color = QColor(0, 200, 255, alpha)

                    painter.setPen(QPen(line_color, 1.2))
                    painter.drawLine(QPointF(n1.x, n1.y), QPointF(n2.x, n2.y))

        # Draw Synaptic Pulses (Action Potential Sparks)
        for pulse in self.pulses:
            if pulse.start_idx < len(self.nodes) and pulse.end_idx < len(self.nodes):
                n1 = self.nodes[pulse.start_idx]
                n2 = self.nodes[pulse.end_idx]
                px = n1.x + (n2.x - n1.x) * pulse.progress
                py = n1.y + (n2.y - n1.y) * pulse.progress

                # Glowing spark
                spark_grad = QRadialGradient(px, py, 8)
                spark_grad.setColorAt(0.0, pulse.color)
                spark_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(spark_grad))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(QPointF(px, py), 6, 6)

                # Bright center core
                painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
                painter.drawEllipse(QPointF(px, py), 2, 2)

        # Draw Neural Nodes
        for node in self.nodes:
            breath = math.sin(node.pulse_phase) * 1.5
            rad = max(2.0, node.radius + breath + (node.energy * 3.0))

            if self.state == NeuralState.THINKING:
                core_color = QColor(192, 132, 252)
                glow_color = QColor(147, 51, 234, 180)
            elif self.state == NeuralState.LISTENING:
                core_color = QColor(52, 211, 153)
                glow_color = QColor(16, 185, 129, 180)
            elif self.state == NeuralState.SPEAKING:
                core_color = QColor(56, 189, 248)
                glow_color = QColor(14, 165, 233, 200)
            else:
                core_color = QColor(0, 240, 255)
                glow_color = QColor(0, 180, 255, 140)

            # Outer glow
            glow_grad = QRadialGradient(node.x, node.y, rad * 2.5)
            glow_grad.setColorAt(0.0, glow_color)
            glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(glow_grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(QPointF(node.x, node.y), rad * 2.5, rad * 2.5)

            # Core
            painter.setBrush(QBrush(core_color))
            painter.drawEllipse(QPointF(node.x, node.y), rad, rad)

            # Center white sparkle
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.drawEllipse(QPointF(node.x, node.y), max(1.0, rad * 0.4), max(1.0, rad * 0.4))

        # Bottom Status Overlay Bar
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(10, 14, 22, 210)))
        painter.drawRect(0, h - 26, w, 26)

        painter.setPen(QPen(QColor(0, 240, 255, 60), 1))
        painter.drawLine(0, h - 26, w, h - 26)

        # Render Status Text
        painter.setPen(QColor(200, 220, 240))
        font = QFont("-apple-system", 9, QFont.Weight.Medium)
        font.setStyleHint(QFont.StyleHint.SansSerif)
        painter.setFont(font)
        painter.drawText(16, h - 8, self.status_text)

        # Pulse indicator dot
        pulse_alpha = int((math.sin(self.time_offset * 4) + 1.0) * 110) + 35
        if self.state == NeuralState.THINKING:
            dot_color = QColor(192, 132, 252, pulse_alpha)
        elif self.state == NeuralState.LISTENING:
            dot_color = QColor(52, 211, 153, pulse_alpha)
        else:
            dot_color = QColor(0, 240, 255, pulse_alpha)

        painter.setBrush(QBrush(dot_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(w - 22, h - 17, 8, 8)
