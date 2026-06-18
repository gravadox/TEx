#!/usr/bin/env bash
set -e

REPO="gravadox/TEx"
INSTALL_DIR="$HOME/.local/share/TEx"
BIN_DIR="$HOME/.local/bin"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$HOME/.local/share/applications"

mkdir -p "$INSTALL_DIR" "$BIN_DIR" "$ICON_DIR" "$DESKTOP_DIR"

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

echo ""
echo "TEx installed."
echo "  Run:      TEx"
echo "  Launcher: app menu -> TEx"
echo ""
echo "If 'TEx' is not found in terminal, add to your ~/.bashrc or ~/.zshrc:"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
