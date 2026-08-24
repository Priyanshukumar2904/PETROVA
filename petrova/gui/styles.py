"""
PETROVA GUI Dark Theme & Cybernetic Obsidian Stylesheet (QSS).
Modern, translucent glassmorphic look with electric cyan & neon violet accents.
"""

CYBER_DARK_THEME = """
/* ============================================================================
   PETROVA Modern Cyber Dark Palette
   ============================================================================ */

QWidget {
    background-color: #0c0f17;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", "Ubuntu", "Cantarell", sans-serif;
    font-size: 13px;
    selection-background-color: #00f0ff;
    selection-color: #0c0f17;
}

/* --- Main Window --- */
QMainWindow {
    background-color: #0a0d14;
}

/* --- Top Header Bar --- */
QFrame#HeaderBar {
    background-color: #111622;
    border-bottom: 1px solid #1e2638;
    padding: 6px 16px;
}

QLabel#AppTitle {
    color: #00f0ff;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 2px;
}

QLabel#DistroBadge {
    background-color: #182234;
    color: #38bdf8;
    border: 1px solid #0284c7;
    border-radius: 12px;
    padding: 3px 10px;
    font-size: 11px;
    font-weight: 600;
}

QLabel#StateBadge {
    background-color: rgba(0, 240, 255, 0.12);
    color: #00f0ff;
    border: 1px solid rgba(0, 240, 255, 0.35);
    border-radius: 12px;
    padding: 3px 12px;
    font-size: 11px;
    font-weight: 700;
}

/* --- Buttons --- */
QPushButton {
    background-color: #161d2d;
    color: #e2e8f0;
    border: 1px solid #232f48;
    border-radius: 8px;
    padding: 7px 14px;
    font-weight: 600;
    font-size: 12px;
}

QPushButton:hover {
    background-color: #1e293f;
    border-color: #00f0ff;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #0f1522;
}

QPushButton#PrimaryButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00b4d8, stop:1 #0077b6);
    color: #ffffff;
    border: none;
    font-weight: 700;
}

QPushButton#PrimaryButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f0ff, stop:1 #0096c7);
}

QPushButton#VoiceButton {
    background-color: #192233;
    border: 1px solid #00f0ff;
    border-radius: 20px;
    min-width: 40px;
    min-height: 40px;
    max-width: 40px;
    max-height: 40px;
    font-size: 16px;
}

QPushButton#VoiceButton:hover {
    background-color: #00f0ff;
    color: #0c0f17;
}

QPushButton#VoiceButton[listening="true"] {
    background-color: #ff0055;
    border-color: #ff4d6d;
    color: #ffffff;
}

QPushButton#HeaderIconBtn {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    font-size: 14px;
    padding: 4px 8px;
    border-radius: 6px;
}

QPushButton#HeaderIconBtn:hover {
    background-color: #1e2638;
    color: #00f0ff;
}

/* --- Input Bar --- */
QFrame#InputFrame {
    background-color: #111622;
    border-top: 1px solid #1e2638;
    padding: 8px 16px;
}

QTextEdit#PromptInput {
    background-color: #161c2b;
    color: #f1f5f9;
    border: 1px solid #232e44;
    border-radius: 10px;
    padding: 8px 12px;
    font-size: 13px;
    font-family: inherit;
}

QTextEdit#PromptInput:focus {
    border: 1px solid #00f0ff;
    background-color: #182030;
}

/* --- Chat Container --- */
QScrollArea#ChatScrollArea {
    background-color: #0c0f17;
    border: none;
}

QWidget#ChatContentWidget {
    background-color: #0c0f17;
}

/* --- Telemetry Sidebar Panel --- */
QFrame#TelemetryPanel {
    background-color: #101420;
    border-left: 1px solid #1a2233;
    min-width: 280px;
    max-width: 320px;
}

QLabel#SidebarTitle {
    color: #38bdf8;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 4px 0px;
}

QFrame#TelemetryCard {
    background-color: #151b29;
    border: 1px solid #202b40;
    border-radius: 10px;
    padding: 10px;
}

QProgressBar {
    background-color: #1e2638;
    border: none;
    border-radius: 4px;
    height: 8px;
    text-align: right;
    font-size: 9px;
    color: transparent;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f0ff, stop:1 #38bdf8);
    border-radius: 4px;
}

QProgressBar#RamBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #06b6d4);
}

QProgressBar#BatteryBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #a855f7, stop:1 #ec4899);
}

/* --- Terminal Drawer Panel --- */
QFrame#TerminalDrawer {
    background-color: #080a0f;
    border-top: 1px solid #00f0ff;
}

QPlainTextEdit#TerminalOutput {
    background-color: #080a0f;
    color: #00ffaf;
    font-family: "JetBrains Mono", "Fira Code", "Source Code Pro", "Consolas", monospace;
    font-size: 12px;
    border: none;
    padding: 8px;
}

QLineEdit#TerminalInput {
    background-color: #101420;
    color: #f8fafc;
    border: 1px solid #1e2638;
    border-radius: 6px;
    padding: 6px 10px;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12px;
}

QLineEdit#TerminalInput:focus {
    border: 1px solid #00f0ff;
}

/* --- Custom Scrollbar --- */
QScrollBar:vertical {
    background: #0a0d14;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #1e2638;
    min-height: 20px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: #334155;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: #0a0d14;
    height: 8px;
}

QScrollBar::handle:horizontal {
    background: #1e2638;
    min-width: 20px;
    border-radius: 4px;
}
"""
