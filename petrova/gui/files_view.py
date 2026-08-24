"""
PETROVA File Intelligence & Storage Partition View.
Allows real inspection of largest directories, cache sizes, downloads, and 1-click cleanups.
"""

import os
import shutil
import subprocess
from pathlib import Path
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
)

from petrova.gui.styles import COLORS
from petrova.linux.stats import get_disk_usage


class DiskScanWorker(QObject):
    finished = pyqtSignal(list)

    def run(self):
        items = []
        home = str(Path.home())
        targets = [
            (f"{home}/Downloads", "Downloads"),
            (f"{home}/.cache", "User Cache"),
            (f"{home}/.local/share", "Local Data"),
            (f"{home}/Videos", "Videos"),
            ("/var/log", "System Logs"),
            ("/var/cache/pacman/pkg", "Pacman Cache"),
            ("/usr/lib", "System Libraries"),
        ]

        for path, label in targets:
            if os.path.exists(path):
                try:
                    res = subprocess.run(["du", "-sh", path], capture_output=True, text=True, timeout=2.0)
                    if res.returncode == 0 and res.stdout:
                        size_str = res.stdout.split()[0]
                        items.append((label, path, size_str))
                except Exception:
                    pass
        self.finished.emit(items)


class FilesViewWidget(QWidget):
    """
    Dedicated FILES and Storage Analyzer View.
    """
    execute_command_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.refresh_storage()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(12)

        # Header Bar
        hdr = QHBoxLayout()
        title = QLabel("FILE INTELLIGENCE & STORAGE EXPLORER")
        title.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 14px; font-weight: 900; letter-spacing: 1px;")
        
        scan_btn = QPushButton("🔍 Scan Disks")
        scan_btn.setObjectName("MonochromePill")
        scan_btn.clicked.connect(self.scan_directories)

        hdr.addWidget(title)
        hdr.addStretch()
        hdr.addWidget(scan_btn)
        layout.addLayout(hdr)

        # 1. Partition Usage Card
        self.disk_card = QFrame()
        self.disk_card.setObjectName("LowerCard")
        d_layout = QVBoxLayout(self.disk_card)
        d_layout.setContentsMargins(14, 10, 14, 10)
        d_layout.setSpacing(6)

        self.disk_lbl = QLabel("ROOT PARTITION: -- / -- GB")
        self.disk_lbl.setStyleSheet(f"color: {COLORS['foreground']}; font-family: 'JetBrains Mono'; font-size: 13px; font-weight: bold;")
        
        self.disk_bar = QProgressBar()
        self.disk_bar.setRange(0, 100)
        self.disk_bar.setValue(0)
        self.disk_bar.setFixedHeight(8)
        self.disk_bar.setTextVisible(False)
        self.disk_bar.setStyleSheet(f"""
            QProgressBar {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['border']};
                border-radius: 1px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS['foreground']};
            }}
        """)

        d_layout.addWidget(self.disk_lbl)
        d_layout.addWidget(self.disk_bar)
        layout.addWidget(self.disk_card)

        # 2. Directory Breakdown Table
        dir_title = QLabel("LARGE STORAGE CONSUMERS")
        dir_title.setStyleSheet(f"color: {COLORS['muted']}; font-family: 'JetBrains Mono'; font-size: 11.5px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(dir_title)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["CATEGORY", "PATH", "SIZE"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                color: {COLORS['foreground']};
                border: 1px solid {COLORS['border']};
                gridline-color: {COLORS['border']};
                font-family: 'JetBrains Mono', monospace;
                font-size: 12.5px;
            }}
            QHeaderView::section {{
                background-color: {COLORS['background']};
                color: {COLORS['muted']};
                border: 1px solid {COLORS['border']};
                padding: 4px 8px;
                font-weight: bold;
            }}
        """)
        layout.addWidget(self.table, 1)

        # 3. 1-Click Operations
        actions_bar = QHBoxLayout()
        actions_bar.setSpacing(8)

        clean_cache_btn = QPushButton("[ 🗑️ Clean User Cache ]")
        clean_cache_btn.setObjectName("MonochromePill")
        clean_cache_btn.clicked.connect(lambda: self.execute_command_requested.emit("rm -rf ~/.cache/*"))

        clean_pkg_btn = QPushButton("[ 📦 Clean Pacman Cache ]")
        clean_pkg_btn.setObjectName("MonochromePill")
        clean_pkg_btn.clicked.connect(lambda: self.execute_command_requested.emit("sudo pacman -Sc --noconfirm"))

        inspect_btn = QPushButton("[ 📂 Open Downloads ]")
        inspect_btn.setObjectName("MonochromePill")
        inspect_btn.clicked.connect(lambda: self.execute_command_requested.emit("ls -la ~/Downloads"))

        actions_bar.addWidget(clean_cache_btn)
        actions_bar.addWidget(clean_pkg_btn)
        actions_bar.addWidget(inspect_btn)
        actions_bar.addStretch()
        layout.addLayout(actions_bar)

    def refresh_storage(self):
        disk = get_disk_usage()
        used = disk.get("used_gb", 0)
        tot = disk.get("total_gb", 0)
        pct = int(disk.get("pct", 0))
        free = disk.get("free_gb", 0)

        self.disk_lbl.setText(f"ROOT PARTITION (/): {used:.1f} GB used / {tot:.1f} GB total ({free:.1f} GB free, {pct}%)")
        self.disk_bar.setValue(pct)
        self.scan_directories()

    def scan_directories(self):
        if hasattr(self, "worker_thread") and self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

        self.worker_thread = QThread(self)
        self.worker = DiskScanWorker()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_scan_finished)
        self.worker_thread.start()

    def _on_scan_finished(self, items: list):
        self.table.setRowCount(len(items))
        for row, (label, path, size) in enumerate(items):
            self.table.setItem(row, 0, QTableWidgetItem(label))
            self.table.setItem(row, 1, QTableWidgetItem(path))
            self.table.setItem(row, 2, QTableWidgetItem(size))

        if hasattr(self, "worker_thread") and self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()

    def closeEvent(self, event):
        if hasattr(self, "worker_thread") and self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        super().closeEvent(event)

