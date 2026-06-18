# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

TEx is a Python desktop text-expander (keyboard abbreviation app) built with CustomTkinter. Type an abbreviation followed by a space and it gets replaced with the configured expansion. It runs as a system-tray app.

## Running from Source

```bash
# Install dependencies
pip install customtkinter pystray pynput cryptography keyring psutil notify-py

# Linux/Wayland only (evdev for global capture):
pip install evdev
sudo pacman -S wtype          # or equivalent for your distro
sudo usermod -a -G input $USER  # then log out and back in

python main.py
```

## Building

```bash
# Step 1 — produce the binary
pyinstaller TEx.spec           # outputs dist/TEx

# Step 2 — wrap as AppImage (Linux)
bash build-appimage.sh         # outputs TEx-x86_64.AppImage
```

`TEx.spec` bundles the AyatanaAppIndicator3 typelib for Wayland tray support. If the path `/usr/lib/girepository-1.0/AyatanaAppIndicator3-0.1.typelib` doesn't exist on your build machine, update `datas` in the spec file.

## Architecture

### Entry point
`main.py` calls `setup_icon()` and `setup_user_folder()` (from `user_files/`) to unpack bundled assets, then instantiates `TEx` and starts the main loop.

### `Elements/app.py` — main window (`TEx` class)
Central controller. Owns the CustomTkinter window, the `CategoryManager`, the `TextExpander`, and the `TrayIcon`. Handles all CRUD on abbreviations, serialises to `user/Expansions.json`, and calls `apply_abbreviations()` to sync the live expander after every change.

### `Expander/Text_expander.py` — keyboard capture & expansion
- On **Linux/Wayland** (when `evdev` is importable and `WAYLAND_DISPLAY` is set): uses a custom `_EvdevListener` for global capture, `UInput` for sending backspaces, and `wtype` / clipboard-paste for typing the replacement. XWayland windows (e.g. Discord, Tkinter itself) get the clipboard-paste path automatically.
- On **Linux/X11 or Windows**: uses `pynput` `Listener` and `Controller`.

Expansion triggers on **space** (the only trigger character). The buffer is 50 characters max. Backspace clears the whole buffer.

### `Tray/linux_tray.py` — system tray
- **Wayland** (`XDG_SESSION_TYPE=wayland`): uses `AppIndicator3` + `Gtk` running in a daemon thread.
- **X11**: uses `pystray` running in a daemon thread.

`Tray/tray.py` is the Windows/X11 fallback (pystray only).

### `Elements/category_manager.py`
Reads/writes `user/Categories.json`. Categories carry `is_encrypted: bool`. The `passwords` category is encrypted by default.

### `Encryption/encryption_util.py`
Fernet symmetric encryption. The key is stored in the OS keyring under service `TExApp`, token `TExEncryptionKey`. Encrypted replacements are stored as Fernet ciphertext strings inside `user/Expansions.json`; they are decrypted at load time and re-encrypted on save.

## Data Files

| File | Purpose |
|------|---------|
| `user/Expansions.json` | All abbreviations — `{ abbrev: { replacement, ignored, tag } }` |
| `user/Categories.json` | Category definitions — id, name, icon, color, is_encrypted |

Both files are created from defaults on first run if absent. **Do not rename or relocate them** without updating the hardcoded paths in `app.py` (`self.data_file`) and `category_manager.py`.

## Platform Notes

- Tested on **Linux Wayland** and **Windows**. X11 support via pynput is untested but should work.
- On Wayland, the tray requires `libayatana-appindicator3` (or `libappindicator3`). Without it, the GTK import will fail.
- The evdev path requires the user to be in the `input` group; without it the app falls back silently to in-app-only pynput capture (global expansion won't work).
