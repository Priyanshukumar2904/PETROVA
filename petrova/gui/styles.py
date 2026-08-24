"""
PETROVA Modern Translucent Glassmorphic Stylesheet (QSS).
Sparkling Amber-Green & Deep Carbon Slate with smooth curves,
translucent layers, and zero cluttered lines.
"""

SPARKLING_AMBER_GREEN_THEME = """
/* ============================================================================
   PETROVA Translucent Glass & Sparkling Amber-Green Theme
   ============================================================================ */

QWidget {
    background-color: #06090e;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", "Ubuntu", "Cantarell", sans-serif;
    font-size: 13.5px;
    selection-background-color: #10b981;
    selection-color: #04070a;
}

/* --- Main Window --- */
QMainWindow {
    background-color: #06090e;
}

/* --- Top Header Bar --- */
QFrame#HeaderBar {
    background-color: rgba(10, 16, 23, 0.85);
    border: none;
    border-bottom: 1px solid rgba(16, 185, 129, 0.12);
    padding: 8px 20px;
}

QLabel#AppTitle {
    color: #00f59b;
    font-size: 17px;
    font-weight: 900;
    letter-spacing: 2.5px;
}

QLabel#DistroBadge {
    background-color: rgba(16, 185, 129, 0.1);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.25);
    border-radius: 14px;
    padding: 4px 12px;
    font-size: 11.5px;
    font-weight: 600;
}

QLabel#StateBadge {
    background-color: rgba(251, 191, 36, 0.12);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.3);
    border-radius: 14px;
    padding: 4px 14px;
    font-size: 11.5px;
    font-weight: 700;
}

/* --- Buttons --- */
QPushButton {
    background-color: rgba(16, 26, 34, 0.8);
    color: #cbd5e1;
    border: 1px solid rgba(52, 211, 153, 0.18);
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
    font-size: 12.5px;
}

QPushButton:hover {
    background-color: rgba(16, 185, 129, 0.18);
    border-color: #00f59b;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: rgba(245, 158, 11, 0.25);
    border-color: #fbbf24;
    color: #fef08a;
}

QPushButton#PrimaryButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
    border: none;
    font-weight: 700;
    border-radius: 10px;
}

QPushButton#PrimaryButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #00f59b);
}

QPushButton#PrimaryButton:pressed {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
}

QPushButton#VoiceButton {
    background-color: rgba(16, 26, 34, 0.9);
    border: 1.5px solid rgba(52, 211, 153, 0.4);
    border-radius: 22px;
    min-width: 44px;
    min-height: 44px;
    max-width: 44px;
    max-height: 44px;
    font-size: 18px;
}

QPushButton#VoiceButton:hover {
    background-color: #10b981;
    color: #06090e;
    border-color: #00f59b;
}

QPushButton#VoiceButton[listening="true"] {
    background-color: #ef4444;
    border-color: #f87171;
    color: #ffffff;
}

QPushButton#HeaderIconBtn {
    background-color: transparent;
    border: none;
    color: #94a3b8;
    font-size: 13px;
    padding: 6px 12px;
    border-radius: 8px;
}

QPushButton#HeaderIconBtn:hover {
    background-color: rgba(16, 185, 129, 0.12);
    color: #00f59b;
}

/* --- Input Bar --- */
QFrame#InputFrame {
    background-color: rgba(10, 16, 23, 0.92);
    border: none;
    border-top: 1px solid rgba(16, 185, 129, 0.15);
    padding: 10px 20px;
}

QTextEdit#PromptInput {
    background-color: rgba(16, 26, 35, 0.85);
    color: #f8fafc;
    border: 1px solid rgba(52, 211, 153, 0.2);
    border-radius: 12px;
    padding: 10px 14px;
    font-size: 13.5px;
    font-family: inherit;
}

QTextEdit#PromptInput:focus {
    border: 1.5px solid #00f59b;
    background-color: rgba(18, 30, 40, 0.95);
}

/* --- Chat Container --- */
QScrollArea#ChatScrollArea {
    background-color: transparent;
    border: none;
}

QWidget#ChatContentWidget {
    background-color: transparent;
}

/* --- Telemetry Minimalist Sidebar Panel --- */
QFrame#TelemetryPanel {
    background-color: rgba(9, 14, 20, 0.92);
    border: none;
    border-left: 1px solid rgba(16, 185, 129, 0.1);
    min-width: 260px;
    max-width: 300px;
}

QLabel#SidebarTitle {
    color: #34d399;
    font-size: 13px;
    font-weight: 800;
    letter-spacing: 1.5px;
    padding: 2px 0px;
}

QFrame#TelemetryCard {
    background-color: rgba(14, 22, 30, 0.7);
    border: 1px solid rgba(52, 211, 153, 0.12);
    border-radius: 14px;
    padding: 12px;
}

QProgressBar {
    background-color: rgba(20, 32, 44, 0.7);
    border: none;
    border-radius: 5px;
    height: 7px;
    text-align: right;
    color: transparent;
}

QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #00f59b);
    border-radius: 5px;
}

QProgressBar#RamBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #34d399);
}

QProgressBar#BatteryBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #f59e0b, stop:1 #fbbf24);
}

/* --- Terminal Drawer Panel --- */
QFrame#TerminalDrawer {
    background-color: #06090d;
    border-top: 1.5px solid #10b981;
}

QPlainTextEdit#TerminalOutput {
    background-color: #06090d;
    color: #34d399;
    font-family: "JetBrains Mono", "Fira Code", "Source Code Pro", "Consolas", monospace;
    font-size: 12.5px;
    border: none;
    padding: 10px;
}

QLineEdit#TerminalInput {
    background-color: #0d161d;
    color: #f8fafc;
    border: 1px solid rgba(52, 211, 153, 0.2);
    border-radius: 8px;
    padding: 8px 12px;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12.5px;
}

QLineEdit#TerminalInput:focus {
    border: 1.5px solid #00f59b;
}

/* --- Custom Translucent Scrollbar --- */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(52, 211, 153, 0.25);
    min-height: 24px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(0, 245, 155, 0.5);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 6px;
}

QScrollBar::handle:horizontal {
    background: rgba(52, 211, 153, 0.25);
    min-width: 24px;
    border-radius: 3px;
}
"""

CYBER_DARK_THEME = SPARKLING_AMBER_GREEN_THEME
