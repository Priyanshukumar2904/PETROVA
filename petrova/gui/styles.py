"""
PETROVA Cyber-HUD & Futuristic Terminal Operating System Stylesheet (QSS).
Matches the reference layout: Deep Carbon Obsidian, precision wireframe borders,
high-legibility typography, segmented LED bars, and sparkling amber-green accents.
"""

SPARKLING_AMBER_GREEN_THEME = """
/* ============================================================================
   PETROVA Cyber-HUD & Linux Terminal Operating Assistant Theme
   ============================================================================ */

QWidget {
    background-color: #06080c;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", "Ubuntu", "JetBrains Mono", monospace, sans-serif;
    font-size: 13.5px;
    selection-background-color: #00f59b;
    selection-color: #04070a;
}

QMainWindow {
    background-color: #06080c;
}

/* --- Top Title Bar --- */
QFrame#TitleBar {
    background-color: #080c12;
    border-bottom: 1px solid #16202c;
    padding: 6px 14px;
}

QLabel#TitleText {
    color: #cbd5e1;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12.5px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#SecurityBadge {
    color: #00f59b;
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 1px;
}

QLabel#ClockLabel {
    color: #94a3b8;
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 600;
}

/* --- Left Navigation Sidebar --- */
QFrame#NavSidebar {
    background-color: #070a0f;
    border-right: 1px solid #16202c;
    min-width: 175px;
    max-width: 195px;
}

QLabel#BrandTitle {
    color: #ffffff;
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 2px;
}

QLabel#BrandSub {
    color: #64748b;
    font-size: 10px;
    letter-spacing: 1px;
    font-weight: 700;
}

QLabel#OnlineDot {
    color: #00f59b;
    font-size: 11px;
    font-weight: 700;
}

QPushButton#NavItem {
    background-color: transparent;
    color: #94a3b8;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px 12px;
    font-weight: 700;
    font-size: 12.5px;
    text-align: left;
    letter-spacing: 0.5px;
}

QPushButton#NavItem:hover {
    background-color: rgba(22, 32, 44, 0.8);
    color: #00f59b;
    border-color: #1e2d3d;
}

QPushButton#NavItem[active="true"] {
    background-color: #ffffff;
    color: #06080c;
    border: 1px solid #ffffff;
    font-weight: 900;
}

QFrame#ShortcutsCard {
    background-color: #080c12;
    border: 1px solid #16202c;
    border-radius: 8px;
    padding: 8px 10px;
}

QLabel#ShortcutHeader {
    color: #64748b;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
}

QLabel#ShortcutItem {
    color: #94a3b8;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
}

/* --- Center Greeting & Sparkline Bar --- */
QFrame#GreetingCard {
    background-color: #080d14;
    border: 1px solid #16202c;
    border-radius: 8px;
    padding: 12px 18px;
}

QLabel#GreetingTitle {
    color: #ffffff;
    font-family: "JetBrains Mono", monospace;
    font-size: 16px;
    font-weight: 800;
}

QLabel#GreetingSub {
    color: #94a3b8;
    font-size: 12.5px;
}

QFrame#SparklineBar {
    background-color: #080d14;
    border: 1px solid #16202c;
    border-radius: 8px;
    padding: 6px 12px;
}

QFrame#SparklineChip {
    background-color: transparent;
    border-right: 1px solid #16202c;
    padding: 2px 10px;
}

QLabel#SparkChipLabel {
    color: #64748b;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

QLabel#SparkChipValue {
    color: #00f59b;
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 800;
}

/* --- Center AI Chat Container --- */
QFrame#ChatOuterFrame {
    background-color: #070a0f;
    border: 1px solid #16202c;
    border-radius: 8px;
}

QFrame#ChatHeader {
    background-color: #080d14;
    border-bottom: 1px solid #16202c;
    padding: 6px 14px;
}

QLabel#ChatHeaderTitle {
    color: #cbd5e1;
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 800;
    letter-spacing: 1px;
}

QLabel#ChatHeaderId {
    color: #64748b;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
}

QScrollArea#ChatScrollArea {
    background-color: transparent;
    border: none;
}

QWidget#ChatContentWidget {
    background-color: transparent;
}

/* --- Message Cards --- */
QFrame#UserCard {
    background-color: #0a1017;
    border: 1px solid #1a2636;
    border-radius: 8px;
    padding: 10px 14px;
    margin-left: 60px;
}

QFrame#AssistantCard {
    background-color: #070a0f;
    border: 1px solid #16202c;
    border-radius: 8px;
    padding: 12px 16px;
    margin-right: 20px;
}

QLabel#RoleBadgeYou {
    color: #38bdf8;
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 800;
    letter-spacing: 1px;
}

QLabel#RoleBadgePetrova {
    color: #00f59b;
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 900;
    letter-spacing: 1px;
}

QFrame#TableBox {
    background-color: #05080c;
    border: 1px solid #16202c;
    border-radius: 6px;
    padding: 8px 12px;
    margin: 6px 0;
}

QPushButton#ActionPill {
    background-color: transparent;
    color: #00f59b;
    border: 1px solid #16202c;
    border-radius: 6px;
    padding: 5px 12px;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

QPushButton#ActionPill:hover {
    background-color: rgba(0, 245, 155, 0.15);
    border-color: #00f59b;
    color: #ffffff;
}

QPushButton#ActionPill:pressed {
    background-color: #00f59b;
    color: #06080c;
}

/* --- Prompt Input Frame --- */
QFrame#InputFrame {
    background-color: #080d14;
    border: 1px solid #16202c;
    border-radius: 8px;
    padding: 6px 12px;
}

QTextEdit#PromptInput {
    background-color: transparent;
    color: #f8fafc;
    border: none;
    font-family: "JetBrains Mono", "Segoe UI", monospace;
    font-size: 13.5px;
    padding: 4px;
}

QPushButton#MicBtn {
    background-color: transparent;
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    color: #94a3b8;
    font-size: 15px;
    min-width: 34px;
    min-height: 34px;
    max-width: 34px;
    max-height: 34px;
}

QPushButton#MicBtn:hover {
    background-color: rgba(0, 245, 155, 0.15);
    border-color: #00f59b;
    color: #00f59b;
}

QPushButton#SendBtn {
    background-color: transparent;
    border: 1px solid #1e2d3d;
    border-radius: 6px;
    color: #00f59b;
    font-size: 14px;
    font-weight: bold;
    min-width: 34px;
    min-height: 34px;
    max-width: 34px;
    max-height: 34px;
}

QPushButton#SendBtn:hover {
    background-color: #00f59b;
    color: #06080c;
}

/* --- Bottom Horizon 3-Card Dock --- */
QFrame#BottomDockCard {
    background-color: #080d14;
    border: 1px solid #16202c;
    border-radius: 8px;
    padding: 8px 12px;
}

QLabel#BottomDockTitle {
    color: #64748b;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 1px;
}

/* --- Right System Overview Sidebar --- */
QFrame#OverviewSidebar {
    background-color: #070a0f;
    border-left: 1px solid #16202c;
    min-width: 250px;
    max-width: 275px;
    padding: 10px 14px;
}

QLabel#SidebarHeaderTitle {
    color: #cbd5e1;
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 800;
    letter-spacing: 1px;
}

QFrame#TelemetryBlock {
    background-color: transparent;
    border-bottom: 1px solid #121a24;
    padding: 6px 0px 8px 0px;
}

QLabel#BlockLabel {
    color: #cbd5e1;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.5px;
}

QLabel#BlockValue {
    color: #00f59b;
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 800;
}

QLabel#BlockSub {
    color: #64748b;
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
}

/* Segmented LED Bar */
QLabel#LedBar {
    color: #00f59b;
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 11.5px;
    letter-spacing: 1.5px;
    font-weight: bold;
}

/* PETROVA CORE Bottom HUD */
QFrame#CoreHudFrame {
    background-color: #080d14;
    border: 1px solid #16202c;
    border-radius: 8px;
    padding: 10px;
}

QLabel#CoreHudTitle {
    color: #cbd5e1;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}

QLabel#CoreHudKey {
    color: #64748b;
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
}

QLabel#CoreHudVal {
    color: #00f59b;
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 700;
}

/* --- Terminal Drawer Panel --- */
QFrame#TerminalDrawer {
    background-color: #05080c;
    border-top: 2px solid #00f59b;
}

QPlainTextEdit#TerminalOutput {
    background-color: #05080c;
    color: #00f59b;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 13px;
    border: none;
    padding: 10px;
}

QLineEdit#TerminalInput {
    background-color: #080d14;
    color: #f8fafc;
    border: 1px solid #16202c;
    border-radius: 6px;
    padding: 8px 12px;
    font-family: "JetBrains Mono", monospace;
    font-size: 13px;
}

QLineEdit#TerminalInput:focus {
    border-color: #00f59b;
}

/* Custom Scrollbars */
QScrollBar:vertical {
    background: transparent;
    width: 6px;
}

QScrollBar::handle:vertical {
    background: #16202c;
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #00f59b;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

CYBER_DARK_THEME = SPARKLING_AMBER_GREEN_THEME
