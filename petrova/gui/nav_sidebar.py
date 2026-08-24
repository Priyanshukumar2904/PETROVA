"""
PETROVA V1 Monochrome Navigation Sidebar & Shortcuts Widget.
Exact implementation of the visual specification:
205-220px width, monochrome geometric logo, vertical nav buttons with solid white active highlight,
and compact rectangular shortcuts panel.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QFont
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QApplication,
)

from petrova.gui.styles import COLORS


class HexLogoWidget(QWidget):
    """Monochrome geometric hexagonal brand icon with 'P' glyph."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(54, 54)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Outer Hexagon
        points = [
            QPointF(27, 4),
            QPointF(48, 15),
            QPointF(48, 39),
            QPointF(27, 50),
            QPointF(6, 39),
            QPointF(6, 15),
        ]
        poly = QPolygonF(points)
        painter.setPen(QPen(QColor(COLORS["foreground"]), 1.5))
        painter.setBrush(QBrush(QColor(COLORS["background"])))
        painter.drawPolygon(poly)

        # Inner Hexagon
        inner_points = [
            QPointF(27, 10),
            QPointF(42, 18),
            QPointF(42, 36),
            QPointF(27, 44),
            QPointF(12, 36),
            QPointF(12, 18),
        ]
        inner_poly = QPolygonF(inner_points)
        painter.setPen(QPen(QColor(COLORS["border_highlight"]), 1.0))
        painter.drawPolygon(inner_poly)

        # Central 'P'
        painter.setPen(QColor(COLORS["foreground"]))
        font = QFont("JetBrains Mono", 13, QFont.Weight.ExtraBold)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "P")


class NavSidebarWidget(QFrame):
    """
    Left navigation panel (210px width) matching reference mockup.
    """
    nav_changed = pyqtSignal(str)
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavSidebar")
        self.setFixedWidth(210)
        self.active_tab = "HOME"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 18, 14, 16)
        layout.setSpacing(12)

        # 1. Top Brand & Geometric Logo
        logo_container = QVBoxLayout()
        logo_container.setSpacing(4)
        logo_container.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.logo = HexLogoWidget()
        logo_container.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)

        brand_lbl = QLabel("P E T R O V A")
        brand_lbl.setObjectName("NavLogoText")
        brand_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_container.addWidget(brand_lbl)

        sub_lbl = QLabel("AI ASSISTANT")
        sub_lbl.setObjectName("NavSubText")
        sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_container.addWidget(sub_lbl)

        online_row = QHBoxLayout()
        online_row.setAlignment(Qt.AlignmentFlag.AlignCenter)
        online_row.setSpacing(4)
        dot = QLabel("•")
        dot.setStyleSheet(f"color: {COLORS['foreground']}; font-size: 14px; font-weight: bold;")
        online_txt = QLabel("ONLINE")
        online_txt.setObjectName("NavOnlineText")
        online_row.addWidget(dot)
        online_row.addWidget(online_txt)
        logo_container.addLayout(online_row)

        layout.addLayout(logo_container)
        layout.addSpacing(14)

        # 2. Vertical Navigation Menu Items
        self.nav_buttons = {}
        menu_items = [
            ("HOME", "⌂  HOME"),
            ("AI_CHAT", "💬  AI CHAT"),
            ("SYSTEM", "📈  SYSTEM"),
            ("FILES", "📁  FILES"),
            ("TASKS", "📋  TASKS"),
            ("SETTINGS", "⚙️  SETTINGS"),
        ]

        for key, label in menu_items:
            btn = QPushButton(label)
            btn.setObjectName("NavItem")
            btn.setProperty("active", "true" if key == self.active_tab else "false")
            btn.clicked.connect(lambda checked, k=key: self._set_active_tab(k))
            self.nav_buttons[key] = btn
            layout.addWidget(btn)

        layout.addStretch()

        # 3. Compact Rectangular Shortcuts Panel
        sc_card = QFrame()
        sc_card.setObjectName("ShortcutsPanel")
        sc_layout = QVBoxLayout(sc_card)
        sc_layout.setContentsMargins(10, 8, 10, 8)
        sc_layout.setSpacing(3)

        sc_head = QLabel("SHORTCUTS")
        sc_head.setObjectName("ShortcutsHeader")
        sc_layout.addWidget(sc_head)

        shortcuts = [
            ("[H]", "Home"),
            ("[A]", "AI Chat"),
            ("[S]", "System"),
            ("[F]", "Files"),
            ("[T]", "Tasks"),
            ("[G]", "Settings"),
            ("[Q]", "Quit"),
        ]
        for k_str, desc in shortcuts:
            line = QLabel(f"<b>{k_str}</b>  {desc}")
            line.setObjectName("ShortcutLine")
            sc_layout.addWidget(line)

        layout.addWidget(sc_card)

    def _set_active_tab(self, key: str):
        self.active_tab = key
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().polish(btn)
        self.nav_changed.emit(key)
