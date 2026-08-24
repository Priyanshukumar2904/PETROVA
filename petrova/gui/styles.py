"""
PETROVA Modern Non-Traditional Workspace Stylesheet (QSS).
Expansive glassmorphism, high-readability typography (15px+ base),
sleek horizontal telemetry capsules, and zero dead space.
"""

SPARKLING_AMBER_GREEN_THEME = """
/* ============================================================================
   PETROVA Modern Expansive Glassmorphic HUD Theme
   ============================================================================ */

QWidget {
    background-color: #06090e;
    color: #f1f5f9;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", "Ubuntu", "Cantarell", sans-serif;
    font-size: 15px;
    selection-background-color: #10b981;
    selection-color: #04070a;
}

/* --- Main Window --- */
QMainWindow {
    background-color: #06090e;
}

/* --- Top Header & Dynamic HUD Bar --- */
QFrame#HeaderBar {
    background-color: rgba(9, 14, 20, 0.95);
    border: none;
    border-bottom: 1px solid rgba(16, 185, 129, 0.15);
    padding: 10px 24px;
}

QLabel#AppTitle {
    color: #00f59b;
    font-size: 20px;
    font-weight: 900;
    letter-spacing: 3px;
}

QLabel#DistroBadge {
    background-color: rgba(16, 185, 129, 0.12);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: 14px;
    padding: 5px 14px;
    font-size: 13px;
    font-weight: 700;
}

QLabel#StateBadge {
    background-color: rgba(251, 191, 36, 0.14);
    color: #fbbf24;
    border: 1px solid rgba(251, 191, 36, 0.35);
    border-radius: 14px;
    padding: 5px 16px;
    font-size: 13px;
    font-weight: 800;
}

/* --- Telemetry Horizontal Capsule Chips (Top HUD) --- */
QFrame#TelemetryCapsule {
    background-color: rgba(14, 22, 30, 0.85);
    border: 1px solid rgba(52, 211, 153, 0.2);
    border-radius: 14px;
    padding: 5px 14px;
}

QFrame#TelemetryCapsule:hover {
    background-color: rgba(16, 185, 129, 0.15);
    border-color: #00f59b;
}

QLabel#CapsuleIcon {
    font-size: 16px;
}

QLabel#CapsuleLabel {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QLabel#CapsuleValue {
    color: #00f59b;
    font-size: 14.5px;
    font-weight: 800;
}

/* --- Buttons --- */
QPushButton {
    background-color: rgba(16, 26, 36, 0.85);
    color: #e2e8f0;
    border: 1px solid rgba(52, 211, 153, 0.22);
    border-radius: 12px;
    padding: 9px 18px;
    font-weight: 700;
    font-size: 13.5px;
}

QPushButton:hover {
    background-color: rgba(16, 185, 129, 0.22);
    border-color: #00f59b;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: rgba(245, 158, 11, 0.3);
    border-color: #fbbf24;
    color: #fef08a;
}

QPushButton#PrimaryButton {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #059669, stop:1 #10b981);
    color: #ffffff;
    border: none;
    font-weight: 800;
    font-size: 14px;
    border-radius: 12px;
    padding: 10px 22px;
}

QPushButton#PrimaryButton:hover {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #00f59b);
}

QPushButton#PrimaryButton:pressed {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #d97706, stop:1 #f59e0b);
}

QPushButton#VoiceButton {
    background-color: rgba(16, 26, 36, 0.95);
    border: 1.5px solid rgba(52, 211, 153, 0.45);
    border-radius: 25px;
    min-width: 50px;
    min-height: 50px;
    max-width: 50px;
    max-height: 50px;
    font-size: 22px;
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

QPushButton#ChipBtn {
    background-color: rgba(16, 185, 129, 0.08);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 10px;
    padding: 5px 12px;
    font-size: 12px;
    font-weight: 600;
}

QPushButton#ChipBtn:hover {
    background-color: rgba(16, 185, 129, 0.22);
    border-color: #00f59b;
    color: #ffffff;
}

/* --- Input Bar & Floating Action Deck --- */
QFrame#InputFrame {
    background-color: rgba(9, 14, 20, 0.95);
    border: none;
    border-top: 1px solid rgba(16, 185, 129, 0.15);
    padding: 12px 24px 16px 24px;
}

QTextEdit#PromptInput {
    background-color: rgba(14, 22, 32, 0.9);
    color: #f8fafc;
    border: 1.5px solid rgba(52, 211, 153, 0.25);
    border-radius: 14px;
    padding: 12px 18px;
    font-size: 15px;
    font-family: inherit;
    line-height: 1.5;
}

QTextEdit#PromptInput:focus {
    border: 1.5px solid #00f59b;
    background-color: rgba(18, 30, 42, 0.98);
}

/* --- Chat Container --- */
QScrollArea#ChatScrollArea {
    background-color: transparent;
    border: none;
}

QWidget#ChatContentWidget {
    background-color: transparent;
}

/* --- Terminal Drawer Panel --- */
QFrame#TerminalDrawer {
    background-color: #05080c;
    border-top: 2px solid #10b981;
}

QPlainTextEdit#TerminalOutput {
    background-color: #05080c;
    color: #34d399;
    font-family: "JetBrains Mono", "Fira Code", "Source Code Pro", "Consolas", monospace;
    font-size: 13.5px;
    border: none;
    padding: 12px 16px;
    line-height: 1.5;
}

QLineEdit#TerminalInput {
    background-color: #0d151c;
    color: #f8fafc;
    border: 1px solid rgba(52, 211, 153, 0.25);
    border-radius: 10px;
    padding: 10px 14px;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 13.5px;
}

QLineEdit#TerminalInput:focus {
    border: 1.5px solid #00f59b;
}

/* --- Custom Translucent Scrollbar --- */
QScrollBar:vertical {
    background: transparent;
    width: 8px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: rgba(52, 211, 153, 0.3);
    min-height: 30px;
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(0, 245, 155, 0.6);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background: transparent;
    height: 8px;
}

QScrollBar::handle:horizontal {
    background: rgba(52, 211, 153, 0.3);
    min-width: 30px;
    border-radius: 4px;
}
"""

CYBER_DARK_THEME = SPARKLING_AMBER_GREEN_THEME
