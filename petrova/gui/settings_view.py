"""
PETROVA Unified Settings & System Configuration View.
Manages user profile, local AI server endpoint, voice engine, memory knowledge vault, and autonomy permissions.
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QScrollArea,
    QMessageBox,
)

from petrova.config.settings import get_config, save_config
from petrova.gui.styles import COLORS
from petrova.gui.memory_dialog import MemoryVaultDialog
from petrova.gui.notifications import notify


class SettingsViewWidget(QWidget):
    """
    Dedicated SETTINGS Configuration View.
    """
    config_saved = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.load_settings()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Header Bar
        hdr = QHBoxLayout()
        title = QLabel("SYSTEM CONFIGURATION & PREFERENCES")
        title.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 14px; font-weight: 900; letter-spacing: 1px;")
        
        save_btn = QPushButton("💾 Save Preferences")
        save_btn.setObjectName("MonochromePill")
        save_btn.clicked.connect(self.save_settings)

        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(save_btn)
        layout.addLayout(hdr)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        content = QWidget()
        c_layout = QVBoxLayout(content)
        c_layout.setContentsMargins(0, 0, 0, 0)
        c_layout.setSpacing(12)

        # 1. User Identity Card
        id_card = self._create_card("USER IDENTITY")
        id_layout = QVBoxLayout(id_card)
        id_layout.setSpacing(8)

        id_layout.addWidget(self._make_field_label("User Display Name:"))
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(f"background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; color: {COLORS['foreground']}; padding: 6px; font-family: 'JetBrains Mono'; font-size: 13px;")
        id_layout.addWidget(self.name_input)
        c_layout.addWidget(id_card)

        # 2. Local AI Inference Server Card
        ai_card = self._create_card("LOCAL AI INFERENCE SERVER")
        ai_layout = QVBoxLayout(ai_card)
        ai_layout.setSpacing(8)

        ai_layout.addWidget(self._make_field_label("AI Provider / Backend:"))
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["llama-server (Default)", "ollama", "custom"])
        self.provider_combo.setStyleSheet(f"background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; color: {COLORS['foreground']}; padding: 6px; font-family: 'JetBrains Mono';")
        ai_layout.addWidget(self.provider_combo)

        ai_layout.addWidget(self._make_field_label("Local Server Endpoint:"))
        self.endpoint_input = QLineEdit()
        self.endpoint_input.setStyleSheet(f"background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; color: {COLORS['foreground']}; padding: 6px; font-family: 'JetBrains Mono';")
        ai_layout.addWidget(self.endpoint_input)

        c_layout.addWidget(ai_card)

        # 3. Voice & Speech Synthesis Card
        voice_card = self._create_card("VOICE & SPEECH SYNTHESIS")
        v_layout = QVBoxLayout(voice_card)
        v_layout.setSpacing(8)

        v_layout.addWidget(self._make_field_label("Active Neural Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems([
            "Nova (Female Clear & Professional)",
            "Aria (Female Smooth & Natural)",
            "Onyx (Male Deep & Resonant)",
            "Echo (Male Technical & Crisp)",
            "Shimmer (Female Soft Tone)",
        ])
        self.voice_combo.setStyleSheet(f"background: {COLORS['surface']}; border: 1px solid {COLORS['border']}; color: {COLORS['foreground']}; padding: 6px; font-family: 'JetBrains Mono';")
        v_layout.addWidget(self.voice_combo)

        self.voice_enabled_chk = QCheckBox("Enable Spoken Voice Output by Default")
        self.voice_enabled_chk.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 13px;")
        v_layout.addWidget(self.voice_enabled_chk)
        c_layout.addWidget(voice_card)

        # 4. Long-Term Memory Vault Card
        mem_card = self._create_card("LONG-TERM MEMORY & KNOWLEDGE VAULT")
        m_layout = QVBoxLayout(mem_card)
        m_layout.setSpacing(8)

        mem_desc = QLabel("PETROVA stores persistent user facts, preferences, and workspace context locally.")
        mem_desc.setStyleSheet(f"color: {COLORS['secondary']}; font-family: 'JetBrains Mono'; font-size: 12px;")
        m_layout.addWidget(mem_desc)

        open_vault_btn = QPushButton("🔑 Open Memory Vault Manager (Ctrl+M)")
        open_vault_btn.setObjectName("MonochromePill")
        open_vault_btn.clicked.connect(self._open_memory_dialog)
        m_layout.addWidget(open_vault_btn)
        c_layout.addWidget(mem_card)

        c_layout.addStretch()
        scroll.setWidget(content)
        layout.addWidget(scroll, 1)

    def _create_card(self, title: str) -> QFrame:
        frame = QFrame()
        frame.setObjectName("LowerCard")
        hdr = QLabel(title)
        hdr.setStyleSheet(f"color: {COLORS['muted']}; font-family: 'JetBrains Mono'; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        return frame

    def _make_field_label(self, txt: str) -> QLabel:
        lbl = QLabel(txt)
        lbl.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 12px; font-weight: bold;")
        return lbl

    def load_settings(self):
        config = get_config()
        self.name_input.setText(config.user_name or "Cipher")
        self.endpoint_input.setText(config.get("api_base", "http://127.0.0.1:8080/v1"))
        from petrova.voice import is_voice_enabled
        self.voice_enabled_chk.setChecked(is_voice_enabled())

    def save_settings(self):
        config = get_config()
        config.set("user_name", self.name_input.text().strip() or "Cipher")
        from petrova.voice import set_voice_enabled
        set_voice_enabled(self.voice_enabled_chk.isChecked())
        config.save()
        notify("Preferences updated and saved.", level="success")
        self.config_saved.emit()

    def _open_memory_dialog(self):
        dlg = MemoryVaultDialog(self)
        dlg.exec()
