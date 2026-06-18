#!/usr/bin/env bash
set -e

REPO="gravadox/TEx"
INSTALL_DIR="$HOME/.local/share/TEx"
BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$HOME/.local/share/applications"

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$ICON_DIR" "$DESKTOP_DIR"

# Check for python3-gi (PyGObject) — required for the Wayland tray icon
if ! python3 -c "import gi" 2>/dev/null; then
    echo "WARNING: PyGObject (python3-gi) is not installed."
    echo "  Arch:          sudo pacman -S python-gobject"
    echo "  Ubuntu/Debian: sudo apt install python3-gi"
    echo "  Fedora:        sudo dnf install python3-gobject"
    echo ""
fi

# If running from the repo (local binary exists), use it; otherwise download from GitHub
if [ -f "./dist/TEx" ]; then
    echo "Using local binary..."
    cp "./dist/TEx" "$INSTALL_DIR/TEx"
    cp "./icon.png" "$INSTALL_DIR/icon.png"
else
    echo "Downloading TEx from GitHub releases..."
    curl -fL "https://github.com/$REPO/releases/latest/download/TEx" -o "$INSTALL_DIR/TEx"
    curl -fL "https://raw.githubusercontent.com/$REPO/main/icon.png" -o "$INSTALL_DIR/icon.png"
fi

chmod +x "$INSTALL_DIR/TEx"
cp "$INSTALL_DIR/icon.png" "$ICON_DIR/TEx.png"

# Wrapper: sets cwd so relative paths (user/, icon.png) resolve correctly
cat > "$BIN_DIR/TEx" << EOF
#!/bin/bash
cd "$INSTALL_DIR"
exec "$INSTALL_DIR/TEx" "\$@"
EOF
chmod +x "$BIN_DIR/TEx"

cat > "$DESKTOP_DIR/TEx.desktop" << EOF
[Desktop Entry]
Name=TEx
Comment=Simple text expander / keyboard abbreviation application
Exec=$BIN_DIR/TEx
Icon=TEx
Type=Application
Categories=Utility;
StartupNotify=false
EOF
chmod +x "$DESKTOP_DIR/TEx.desktop"

update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true


SHELL_RC="$HOME/.bashrc"
[ -f "$HOME/.zshrc" ] && SHELL_RC="$HOME/.zshrc"

if ! grep -q '\.local/bin' "$SHELL_RC" 2>/dev/null; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
    echo "Added ~/.local/bin to PATH in $SHELL_RC"
fi

if command -v fish &>/dev/null; then
    fish -c 'fish_add_path ~/.local/bin' 2>/dev/null || true
fi


echo ""
echo "---------------------------------------------------------------------"
echo "TEx installed."
echo "  Run:      TEx"
echo "  Launcher: app menu -> TEx"
echo ""
echo "---------------------------------------------------------------------"
echo "If 'TEx' is not found in terminal, add to your ~/.bashrc or ~/.zshrc:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo "---------------------------------------------------------------------"
echo ""
echo "                                NOTE                                 "
echo "---------------------------------------------------------------------"
echo "Requires the user to be in the 'input' group, use:"
echo "sudo usermod -a -G input $USER "
echo "then log out and back in"
echo "---------------------------------------------------------------------"
