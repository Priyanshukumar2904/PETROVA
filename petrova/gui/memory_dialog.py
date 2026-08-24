"""
PETROVA Memory & Knowledge Vault Dialog.
Allows users to visually browse, search, add, or delete persistent memory entries.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QFrame,
)

from petrova.memory.store import (
    get_all_memories,
    search_memories,
    delete_memory_by_id,
    save_memory,
)


class MemoryVaultDialog(QDialog):
    """Visual memory inspector and manager."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🧠 PETROVA Memory & Knowledge Vault")
        self.resize(550, 420)
        self.setStyleSheet("""
            QDialog {
                background-color: #0d1117;
            }
        """)

        self._setup_ui()
        self.load_memories()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # Header
        title = QLabel("🧠 PERSISTENT MEMORY & KNOWLEDGE VAULT")
        title.setStyleSheet("color: #00f0ff; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        layout.addWidget(title)

        desc = QLabel("PETROVA retains user preferences, hardware notes, and work habits across sessions.")
        desc.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(desc)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search stored memories...")
        self.search_input.textChanged.connect(self._on_search)
        search_layout.addWidget(self.search_input)

        refresh_btn = QPushButton("↻ Refresh")
        refresh_btn.clicked.connect(self.load_memories)
        search_layout.addWidget(refresh_btn)
        layout.addLayout(search_layout)

        # Memories List
        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: #161b22;
                border: 1px solid #30363d;
                border-radius: 8px;
                padding: 6px;
            }
            QListWidget::item {
                background-color: #0d1117;
                border: 1px solid #21262d;
                border-radius: 6px;
                padding: 8px;
                margin-bottom: 4px;
                color: #e6edf3;
            }
            QListWidget::item:selected {
                border-color: #00f0ff;
                background-color: #1f293d;
            }
        """)
        layout.addWidget(self.list_widget)

        # Add Memory Row
        add_layout = QHBoxLayout()
        self.new_mem_input = QLineEdit()
        self.new_mem_input.setPlaceholderText("Add a new fact or preference manually...")
        self.new_mem_input.returnPressed.connect(self._on_add)
        
        add_btn = QPushButton("+ Add Memory")
        add_btn.setObjectName("PrimaryButton")
        add_btn.clicked.connect(self._on_add)

        delete_btn = QPushButton("🗑️ Delete Selected")
        delete_btn.setStyleSheet("background-color: #7f1d1d; color: #fecaca; border: 1px solid #991b1b;")
        delete_btn.clicked.connect(self._on_delete)

        add_layout.addWidget(self.new_mem_input)
        add_layout.addWidget(add_btn)
        add_layout.addWidget(delete_btn)
        layout.addLayout(add_layout)

    def load_memories(self):
        """Fetch and populate memories."""
        self.list_widget.clear()
        mems = get_all_memories()
        for m in mems:
            item = QListWidgetItem(f"[{m.get('category', 'general').upper()}] {m['content']}")
            item.setData(Qt.ItemDataRole.UserRole, m["id"])
            self.list_widget.addItem(item)

    def _on_search(self, text: str):
        query = text.strip()
        if not query:
            self.load_memories()
            return

        self.list_widget.clear()
        mems = search_memories(query, limit=20)
        for m in mems:
            item = QListWidgetItem(f"[{m.get('category', 'general').upper()}] {m['content']}")
            item.setData(Qt.ItemDataRole.UserRole, m["id"])
            self.list_widget.addItem(item)

    def _on_add(self):
        text = self.new_mem_input.text().strip()
        if not text:
            return
        save_memory(content=text, category="user_preference", importance=0.8)
        self.new_mem_input.clear()
        self.load_memories()

    def _on_delete(self):
        selected = self.list_widget.currentItem()
        if not selected:
            QMessageBox.information(self, "Delete Memory", "Please select a memory to delete.")
            return

        mem_id = selected.data(Qt.ItemDataRole.UserRole)
        if delete_memory_by_id(mem_id):
            self.load_memories()
