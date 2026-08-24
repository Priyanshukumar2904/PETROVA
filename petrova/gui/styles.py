"""
PETROVA Monochrome Cyber-HUD Stylesheet & Theme System.
Exact implementation of the V1 Monochrome Specification:
#000000 (Black background), #FFFFFF (Primary Text), #BDBDBD (Secondary Text), #555555 / #333333 (Borders).
"""

# Centralized Theme Dictionary (allowing future color themes without changing component code)
COLORS = {
    "background": "#000000",
    "surface": "#050505",
    "surface_elevated": "#0a0a0a",
    "foreground": "#FFFFFF",
    "secondary": "#BDBDBD",
    "muted": "#757575",
    "border": "#333333",
    "border_highlight": "#555555",
    "border_active": "#FFFFFF",
    "accent": "#FFFFFF",
    "accent_inverted": "#000000",
    "led_filled": "#FFFFFF",
    "led_empty": "#222222",
}

MONOCHROME_THEME_QSS = f"""
/* ============================================================================
   PETROVA V1 Monochrome Cyber-HUD Theme
   ============================================================================ */

QWidget {{
    background-color: {COLORS["background"]};
    color: {COLORS["foreground"]};
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Inter", "Ubuntu", "JetBrains Mono", monospace, sans-serif;
    font-size: 13px;
    selection-background-color: {COLORS["foreground"]};
    selection-color: {COLORS["background"]};
}}

QMainWindow {{
    background-color: {COLORS["background"]};
}}

/* --- Top System Bar --- */
QFrame#TopSystemBar {{
    background-color: {COLORS["background"]};
    border: none;
    border-bottom: 1px solid {COLORS["border"]};
    min-height: 42px;
    max-height: 48px;
    padding: 4px 16px;
}}

QLabel#TopBarBrand {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 1.5px;
}}

QLabel#TopBarSub {{
    color: {COLORS["muted"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 500;
}}

QLabel#TopBarPrivacy {{
    color: {COLORS["secondary"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QLabel#TopBarClock {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 600;
}}

/* --- Left Navigation Panel --- */
QFrame#NavSidebar {{
    background-color: {COLORS["background"]};
    border: none;
    border-right: 1px solid {COLORS["border"]};
    min-width: 205px;
    max-width: 220px;
}}

QLabel#NavLogoText {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 3px;
}}

QLabel#NavSubText {{
    color: {COLORS["muted"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}}

QLabel#NavOnlineText {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 700;
}}

QPushButton#NavItem {{
    background-color: transparent;
    color: {COLORS["secondary"]};
    border: 1px solid transparent;
    border-radius: 2px;
    padding: 8px 14px;
    font-family: "JetBrains Mono", "Segoe UI", monospace;
    font-weight: 700;
    font-size: 12.5px;
    text-align: left;
    letter-spacing: 1px;
}}

QPushButton#NavItem:hover {{
    background-color: {COLORS["surface_elevated"]};
    color: {COLORS["foreground"]};
    border-color: {COLORS["border"]};
}}

QPushButton#NavItem[active="true"] {{
    background-color: {COLORS["foreground"]};
    color: {COLORS["background"]};
    border: 1px solid {COLORS["foreground"]};
    font-weight: 900;
}}

QFrame#ShortcutsPanel {{
    background-color: {COLORS["background"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 8px 10px;
}}

QLabel#ShortcutsHeader {{
    color: {COLORS["muted"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
    font-weight: 800;
    letter-spacing: 1.5px;
}}

QLabel#ShortcutLine {{
    color: {COLORS["secondary"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
}}

/* --- Central Workspace: Greeting Panel --- */
QFrame#GreetingPanel {{
    background-color: {COLORS["background"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 14px 18px;
}}

QLabel#GreetingTitle {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 16px;
    font-weight: 700;
}}

QLabel#GreetingSubtitle {{
    color: {COLORS["secondary"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 12.5px;
}}

/* --- Central Workspace: System Metric Strip --- */
QFrame#MetricStrip {{
    background-color: {COLORS["background"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 4px 6px;
}}

QFrame#MetricCell {{
    background-color: transparent;
    border-right: 1px solid {COLORS["border"]};
    padding: 2px 8px;
}}

QLabel#MetricCellTitle {{
    color: {COLORS["muted"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.5px;
}}

QLabel#MetricCellValue {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 700;
}}

/* --- Central Workspace: AI Assistant Panel --- */
QFrame#ChatMainFrame {{
    background-color: {COLORS["background"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
}}

QFrame#ChatHeaderBar {{
    background-color: {COLORS["background"]};
    border-bottom: 1px solid {COLORS["border"]};
    padding: 6px 14px;
}}

QLabel#ChatHeaderTitle {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 1px;
}}

QLabel#ChatHeaderId {{
    color: {COLORS["muted"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
}}

QScrollArea#ChatScrollArea {{
    background-color: transparent;
    border: none;
}}

QWidget#ChatContentWidget {{
    background-color: transparent;
}}

/* Message Blocks */
QFrame#TechnicalMessageBlock {{
    background-color: transparent;
    border: none;
    padding: 4px 0px;
}}

QLabel#LabelYou {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 800;
    letter-spacing: 1px;
}}

QLabel#LabelPetrova {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 900;
    letter-spacing: 1px;
}}

QLabel#MessageBody {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", "Segoe UI", monospace;
    font-size: 13.5px;
    line-height: 1.5;
}}

/* Structured Table Output */
QFrame#StructureTableBox {{
    background-color: {COLORS["surface"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 8px 12px;
    margin: 6px 0px;
}}

QPushButton#MonochromePill {{
    background-color: {COLORS["background"]};
    color: {COLORS["foreground"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 4px 12px;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}

QPushButton#MonochromePill:hover {{
    background-color: {COLORS["foreground"]};
    color: {COLORS["background"]};
    border-color: {COLORS["foreground"]};
}}

QPushButton#MonochromePill:pressed {{
    background-color: {COLORS["secondary"]};
    color: {COLORS["background"]};
}}

/* --- Input Bar --- */
QFrame#AiInputFrame {{
    background-color: {COLORS["background"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 6px 12px;
}}

QTextEdit#AiInputText {{
    background-color: transparent;
    color: {COLORS["foreground"]};
    border: none;
    font-family: "JetBrains Mono", "Segoe UI", monospace;
    font-size: 13.5px;
}}

QPushButton#InputIconBtn {{
    background-color: transparent;
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 13px;
    min-width: 32px;
    min-height: 32px;
    max-width: 32px;
    max-height: 32px;
}}

QPushButton#InputIconBtn:hover {{
    background-color: {COLORS["foreground"]};
    color: {COLORS["background"]};
    border-color: {COLORS["foreground"]};
}}

/* --- Lower Central Panels (3-Card Row) --- */
QFrame#LowerCard {{
    background-color: {COLORS["background"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 8px 12px;
}}

QLabel#LowerCardTitle {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 1px;
}}

/* --- Right System Overview Sidebar --- */
QFrame#RightSystemMonitor {{
    background-color: {COLORS["background"]};
    border: none;
    border-left: 1px solid {COLORS["border"]};
    min-width: 300px;
    max-width: 340px;
    padding: 10px 14px;
}}

QLabel#OverviewHeaderTitle {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 1px;
}}

QFrame#MonitorBlock {{
    background-color: transparent;
    border-bottom: 1px solid {COLORS["border"]};
    padding: 6px 0px 8px 0px;
}}

QLabel#BlockLabel {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 800;
    letter-spacing: 0.5px;
}}

QLabel#BlockValue {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 800;
}}

QLabel#LedProgressBar {{
    color: {COLORS["led_filled"]};
    font-family: "JetBrains Mono", "Courier New", monospace;
    font-size: 12px;
    letter-spacing: 1.5px;
    font-weight: bold;
}}

QLabel#BlockSubDetail {{
    color: {COLORS["secondary"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
}}

/* PETROVA CORE Panel */
QFrame#PetrovaCoreFrame {{
    background-color: {COLORS["background"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 10px;
}}

QLabel#CoreTitle {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 11.5px;
    font-weight: 800;
    letter-spacing: 1px;
}}

QLabel#CoreKey {{
    color: {COLORS["muted"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
}}

QLabel#CoreVal {{
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 700;
}}

/* --- Bottom Status Bar --- */
QFrame#BottomStatusBar {{
    background-color: {COLORS["background"]};
    border: none;
    border-top: 1px solid {COLORS["border"]};
    min-height: 28px;
    max-height: 32px;
    padding: 2px 14px;
}}

QLabel#StatusTextLeft {{
    color: {COLORS["muted"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
    font-weight: 600;
}}

QLabel#StatusTextRight {{
    color: {COLORS["secondary"]};
    font-family: "JetBrains Mono", monospace;
    font-size: 10.5px;
    font-weight: 600;
}}

/* Terminal Drawer */
QFrame#TerminalDrawer {{
    background-color: {COLORS["background"]};
    border-top: 2px solid {COLORS["foreground"]};
}}

QPlainTextEdit#TerminalOutput {{
    background-color: {COLORS["background"]};
    color: {COLORS["foreground"]};
    font-family: "JetBrains Mono", "Fira Code", monospace;
    font-size: 12.5px;
    border: none;
    padding: 8px;
}}

QLineEdit#TerminalInput {{
    background-color: {COLORS["surface"]};
    color: {COLORS["foreground"]};
    border: 1px solid {COLORS["border"]};
    border-radius: 2px;
    padding: 6px 10px;
    font-family: "JetBrains Mono", monospace;
    font-size: 12.5px;
}}

QLineEdit#TerminalInput:focus {{
    border-color: {COLORS["foreground"]};
}}

/* Custom Scrollbars */
QScrollBar:vertical {{
    background: transparent;
    width: 6px;
}}

QScrollBar::handle:vertical {{
    background: {COLORS["border"]};
    min-height: 20px;
    border-radius: 0px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS["foreground"]};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}
"""

SPARKLING_AMBER_GREEN_THEME = MONOCHROME_THEME_QSS
CYBER_DARK_THEME = MONOCHROME_THEME_QSS
