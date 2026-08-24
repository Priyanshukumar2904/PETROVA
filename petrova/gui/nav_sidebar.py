"""
PETROVA Left Navigation Sidebar & Shortcuts Widget.
Matches the reference layout with hexagonal logo, section switcher, and keyboard shortcuts guide.
"""

from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QApplication,
)


class HexLogoWidget(QWidget):
    """Hexagonal geometric brand icon with glowing 'P' glyph."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(48, 48)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw outer hexagon
        points = [
            QPointF(24, 4),
            QPointF(42, 14),
            QPointF(42, 34),
            QPointF(24, 44),
            QPointF(6, 34),
            QPointF(6, 14),
        ]
        poly = QPolygonF(points)

        painter.setPen(QPen(QColor(0, 245, 155), 1.5))
        painter.setBrush(QBrush(QColor(8, 14, 22, 230)))
        painter.drawPolygon(poly)

        # Draw inner hexagon
        inner_points = [
            QPointF(24, 10),
            QPointF(36, 17),
            QPointF(36, 31),
            QPointF(24, 38),
            QPointF(12, 31),
            QPointF(12, 17),
        ]
        inner_poly = QPolygonF(inner_points)
        painter.setPen(QPen(QColor(16, 185, 129, 140), 1.0))
        painter.drawPolygon(inner_poly)

        # Draw centered 'P'
        painter.setPen(QColor(255, 255, 255))
        font = painter.font()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "P")


class NavSidebarWidget(QFrame):
    """
    Left-hand vertical navigation sidebar with shortcuts card.
    """
    nav_changed = pyqtSignal(str)
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("NavSidebar")
        self.active_tab = "HOME"
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 16, 12, 14)
        layout.setSpacing(12)

        # 1. Top Logo Header
        logo_row = QHBoxLayout()
        logo_row.setSpacing(10)
        self.logo = HexLogoWidget()
        logo_row.addWidget(self.logo)

        brand_text_vbox = QVBoxLayout()
        brand_text_vbox.setSpacing(2)
        
        brand_title = QLabel("PETROVA")
        brand_title.setObjectName("BrandTitle")
        
        brand_sub = QLabel("AI ASSISTANT")
        brand_sub.setObjectName("BrandSub")

        online_row = QHBoxLayout()
        online_row.setSpacing(4)
        online_dot = QLabel("•")
        online_dot.setStyleSheet("color: #00f59b; font-size: 14px; font-weight: bold;")
        online_lbl = QLabel("ONLINE")
        online_lbl.setObjectName("OnlineDot")
        online_row.addWidget(online_dot)
        online_row.addWidget(online_lbl)
        online_row.addStretch()

        brand_text_vbox.addWidget(brand_title)
        brand_text_vbox.addWidget(brand_sub)
        brand_text_vbox.addLayout(online_row)

        logo_row.addLayout(brand_text_vbox)
        layout.addLayout(logo_row)

        layout.addSpacing(10)

        # 2. Navigation Menu Items
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

        # 3. Bottom Shortcuts Card
        shortcuts_card = QFrame()
        shortcuts_card.setObjectName("ShortcutsCard")
        sc_layout = QVBoxLayout(shortcuts_card)
        sc_layout.setContentsMargins(8, 8, 8, 8)
        sc_layout.setSpacing(4)

        sc_title = QLabel("SHORTCUTS")
        sc_title.setObjectName("ShortcutHeader")
        sc_layout.addWidget(sc_title)

        shortcuts_list = [
            ("[H]", "Home"),
            ("[A]", "AI Chat"),
            ("[S]", "System"),
            ("[F]", "Files"),
            ("[T]", "Tasks"),
            ("[G]", "Settings"),
            ("[Q]", "Quit"),
        ]
        for key_str, desc in shortcuts_list:
            sc_lbl = QLabel(f"<b>{key_str}</b>  {desc}")
            sc_lbl.setObjectName("ShortcutItem")
            sc_layout.addWidget(sc_lbl)

        layout.addWidget(shortcuts_card)

    def _set_active_tab(self, key: str):
        self.active_tab = key
        for k, btn in self.nav_buttons.items():
            btn.setProperty("active", "true" if k == key else "false")
            btn.style().polish(btn)
        self.nav_changed.emit(key)
