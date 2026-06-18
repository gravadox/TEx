#!/usr/bin/env bash
set -e

APPDIR="TEx.AppDir"
BINARY="./dist/TEx"

if [ ! -f "$BINARY" ]; then
    echo "Error: dist/TEx not found. Build it first with: pyinstaller TEx.spec"
    exit 1
fi

# Download appimagetool if not present
if [ ! -f "./appimagetool-x86_64.AppImage" ]; then
    echo "Downloading appimagetool..."
    curl -Lo appimagetool-x86_64.AppImage \
        "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppDir structure
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/applications"

# Copy files into AppDir
cp "$BINARY"    "$APPDIR/usr/bin/TEx"
cp icon.png     "$APPDIR/usr/share/icons/hicolor/256x256/apps/TEx.png"
cp TEx.desktop  "$APPDIR/usr/share/applications/TEx.desktop"

# AppImage requires these symlinks at the root of AppDir
ln -sf usr/bin/TEx              "$APPDIR/AppRun"
ln -sf usr/share/icons/hicolor/256x256/apps/TEx.png "$APPDIR/TEx.png"
ln -sf usr/share/applications/TEx.desktop           "$APPDIR/TEx.desktop"

# Build the AppImage
# APPIMAGE_EXTRACT_AND_RUN=1 makes appimagetool extract itself instead of
# mounting via FUSE — avoids "no space left on device" errors in /tmp
ARCH=x86_64 APPIMAGE_EXTRACT_AND_RUN=1 ./appimagetool-x86_64.AppImage "$APPDIR" "TEx-x86_64.AppImage"

echo ""
echo "Done: TEx-x86_64.AppImage Was Created"
