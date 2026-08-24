#!/usr/bin/env bash
# ==============================================================================
# PETROVA One-Click Installer, Desktop App & Global Command Setup
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "⚡ Installing PETROVA (AI Operating Assistant & Desktop GUI for Linux)..."

# 1. Ensure Python 3.10+ is available
if ! command -v python3 &>/dev/null; then
    echo "❌ Error: python3 is not installed on your system."
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating isolated Python virtual environment..."
    python3 -m venv "$VENV_DIR"
fi

echo "📦 Installing / updating PETROVA dependencies (CLI & Desktop GUI)..."
"$VENV_DIR/bin/pip" install --upgrade pip --quiet
"$VENV_DIR/bin/pip" install -e "$SCRIPT_DIR" --quiet

# 3. Create global CLI launcher in ~/.local/bin
mkdir -p "$BIN_DIR"

# CLI Launcher (petrova)
cat << 'LAUNCHER' > "$BIN_DIR/petrova"
#!/usr/bin/env bash
# Global CLI launcher for PETROVA
INSTALL_DIR="PETROVA_DIR_PLACEHOLDER"
VENV_PYTHON="$INSTALL_DIR/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "PETROVA virtual environment missing. Running setup..."
    bash "$INSTALL_DIR/install.sh"
fi

exec "$VENV_PYTHON" -m petrova.cli "$@"
LAUNCHER

# GUI Launcher (petrova-gui)
cat << 'LAUNCHER_GUI' > "$BIN_DIR/petrova-gui"
#!/usr/bin/env bash
# Global Desktop GUI launcher for PETROVA
INSTALL_DIR="PETROVA_DIR_PLACEHOLDER"
VENV_PYTHON="$INSTALL_DIR/.venv/bin/python"

if [ ! -x "$VENV_PYTHON" ]; then
    echo "PETROVA virtual environment missing. Running setup..."
    bash "$INSTALL_DIR/install.sh"
fi

exec "$VENV_PYTHON" -m petrova.gui "$@"
LAUNCHER_GUI

# Replace placeholder with absolute path
sed -i "s|PETROVA_DIR_PLACEHOLDER|$SCRIPT_DIR|g" "$BIN_DIR/petrova"
sed -i "s|PETROVA_DIR_PLACEHOLDER|$SCRIPT_DIR|g" "$BIN_DIR/petrova-gui"
chmod +x "$BIN_DIR/petrova"
chmod +x "$BIN_DIR/petrova-gui"

# 4. Register Desktop Launcher and System Icons
"$VENV_DIR/bin/python" -c "from petrova.gui.desktop import ensure_desktop_entry; ensure_desktop_entry()"

echo ""
echo "=================================================================="
echo "✅ PETROVA installed successfully!"
echo "🚀 1. Launch Terminal Mode:     petrova"
echo "🖥️  2. Launch Desktop GUI Mode: petrova-gui (or type /gui in CLI)"
echo "📱 3. Launch from App Menu:     Click 'PETROVA' in your desktop launcher"
echo "=================================================================="
echo ""
