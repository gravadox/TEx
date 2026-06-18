from pynput.keyboard import Key, Listener, Controller, KeyCode
import threading
import time
import platform
import os


def _detect_use_evdev():
    if platform.system() != 'Linux':
        return False
    if not os.environ.get('WAYLAND_DISPLAY'):
        return False
    try:
        import evdev  # noqa: F401
        return True
    except ImportError:
        return False


_USE_EVDEV = _detect_use_evdev()

if _USE_EVDEV:
    import evdev
    from evdev import ecodes as ec, categorize, KeyEvent as EvKeyEvent
    import subprocess
    import select as _select


if _USE_EVDEV:
    class _EvdevListener:
        """Global keyboard listener for Linux/Wayland using evdev.
        Requires the user to be in the 'input' group:
          sudo usermod -a -G input $USER  (then log out and back in)
        """

        # US QWERTY key code → character
        _NORMAL = {
            ec.KEY_GRAVE: '`', ec.KEY_1: '1', ec.KEY_2: '2', ec.KEY_3: '3',
            ec.KEY_4: '4', ec.KEY_5: '5', ec.KEY_6: '6', ec.KEY_7: '7',
            ec.KEY_8: '8', ec.KEY_9: '9', ec.KEY_0: '0',
            ec.KEY_MINUS: '-', ec.KEY_EQUAL: '=',
            ec.KEY_Q: 'q', ec.KEY_W: 'w', ec.KEY_E: 'e', ec.KEY_R: 'r',
            ec.KEY_T: 't', ec.KEY_Y: 'y', ec.KEY_U: 'u', ec.KEY_I: 'i',
            ec.KEY_O: 'o', ec.KEY_P: 'p',
            ec.KEY_LEFTBRACE: '[', ec.KEY_RIGHTBRACE: ']', ec.KEY_BACKSLASH: '\\',
            ec.KEY_A: 'a', ec.KEY_S: 's', ec.KEY_D: 'd', ec.KEY_F: 'f',
            ec.KEY_G: 'g', ec.KEY_H: 'h', ec.KEY_J: 'j', ec.KEY_K: 'k',
            ec.KEY_L: 'l', ec.KEY_SEMICOLON: ';', ec.KEY_APOSTROPHE: "'",
            ec.KEY_Z: 'z', ec.KEY_X: 'x', ec.KEY_C: 'c', ec.KEY_V: 'v',
            ec.KEY_B: 'b', ec.KEY_N: 'n', ec.KEY_M: 'm',
            ec.KEY_COMMA: ',', ec.KEY_DOT: '.', ec.KEY_SLASH: '/',
        }
        _SHIFTED = {
            ec.KEY_GRAVE: '~', ec.KEY_1: '!', ec.KEY_2: '@', ec.KEY_3: '#',
            ec.KEY_4: '$', ec.KEY_5: '%', ec.KEY_6: '^', ec.KEY_7: '&',
            ec.KEY_8: '*', ec.KEY_9: '(', ec.KEY_0: ')',
            ec.KEY_MINUS: '_', ec.KEY_EQUAL: '+',
            ec.KEY_Q: 'Q', ec.KEY_W: 'W', ec.KEY_E: 'E', ec.KEY_R: 'R',
            ec.KEY_T: 'T', ec.KEY_Y: 'Y', ec.KEY_U: 'U', ec.KEY_I: 'I',
            ec.KEY_O: 'O', ec.KEY_P: 'P',
            ec.KEY_LEFTBRACE: '{', ec.KEY_RIGHTBRACE: '}', ec.KEY_BACKSLASH: '|',
            ec.KEY_A: 'A', ec.KEY_S: 'S', ec.KEY_D: 'D', ec.KEY_F: 'F',
            ec.KEY_G: 'G', ec.KEY_H: 'H', ec.KEY_J: 'J', ec.KEY_K: 'K',
            ec.KEY_L: 'L', ec.KEY_SEMICOLON: ':', ec.KEY_APOSTROPHE: '"',
            ec.KEY_Z: 'Z', ec.KEY_X: 'X', ec.KEY_C: 'C', ec.KEY_V: 'V',
            ec.KEY_B: 'B', ec.KEY_N: 'N', ec.KEY_M: 'M',
            ec.KEY_COMMA: '<', ec.KEY_DOT: '>', ec.KEY_SLASH: '?',
        }
        _SPECIAL = {
            ec.KEY_SPACE: Key.space,
            ec.KEY_ENTER: Key.enter,
            ec.KEY_KPENTER: Key.enter,
            ec.KEY_TAB: Key.tab,
            ec.KEY_BACKSPACE: Key.backspace,
            ec.KEY_DELETE: Key.delete,
            ec.KEY_LEFT: Key.left,
            ec.KEY_RIGHT: Key.right,
            ec.KEY_UP: Key.up,
            ec.KEY_DOWN: Key.down,
            ec.KEY_HOME: Key.home,
            ec.KEY_END: Key.end,
            ec.KEY_PAGEUP: Key.page_up,
            ec.KEY_PAGEDOWN: Key.page_down,
            ec.KEY_ESC: Key.esc,
        }
        _SHIFT_CODES = {ec.KEY_LEFTSHIFT, ec.KEY_RIGHTSHIFT}
        _FLUSH_MODS = {
            ec.KEY_LEFTCTRL, ec.KEY_RIGHTCTRL,
            ec.KEY_LEFTALT, ec.KEY_RIGHTALT,
            ec.KEY_LEFTMETA, ec.KEY_RIGHTMETA,
        }

        def __init__(self, on_press):
            self._on_press = on_press
            self._thread = None
            self._stop_event = threading.Event()
            self._shift = False
            self._devices = self._find_keyboards()
            if not self._devices:
                print("⚠️  No accessible keyboard devices found.")
                print("    Add your user to the 'input' group, then log out and back in:")
                print("      sudo usermod -a -G input $USER")

        def _find_keyboards(self):
            keyboards = []
            for path in evdev.list_devices():
                try:
                    dev = evdev.InputDevice(path)
                    caps = dev.capabilities()
                    if ec.EV_KEY in caps and ec.KEY_A in caps[ec.EV_KEY]:
                        keyboards.append(dev)
                except (PermissionError, OSError):
                    pass
            return keyboards

        def start(self):
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

        def stop(self):
            self._stop_event.set()
            if self._thread:
                self._thread.join(timeout=1.0)
                self._thread = None

        def _run(self):
            while not self._stop_event.is_set():
                fds = [d.fd for d in self._devices]
                if not fds:
                    time.sleep(0.1)
                    continue
                try:
                    r, _, _ = _select.select(fds, [], [], 0.05)
                except Exception:
                    time.sleep(0.05)
                    continue
                for fd in r:
                    dev = next((d for d in self._devices if d.fd == fd), None)
                    if not dev:
                        continue
                    try:
                        for event in dev.read():
                            if event.type == ec.EV_KEY:
                                self._process(categorize(event))
                    except Exception:
                        pass

        def _process(self, kev):
            code = kev.scancode
            state = kev.keystate

            if code in self._SHIFT_CODES:
                self._shift = (state != EvKeyEvent.key_up)
                return

            # Flush buffer on ctrl/alt/meta press
            if code in self._FLUSH_MODS:
                if state == EvKeyEvent.key_down:
                    self._on_press(Key.ctrl)
                return

            if state == EvKeyEvent.key_up:
                return

            if code in self._SPECIAL:
                self._on_press(self._SPECIAL[code])
                return

            char_map = self._SHIFTED if self._shift else self._NORMAL
            char = char_map.get(code)
            if char:
                self._on_press(KeyCode.from_char(char))


class TextExpander:
    def __init__(self):
        self.abbreviations = {}
        self.buffer = ""
        self.buffer_size = 50
        self.controller = Controller() if not _USE_EVDEV else None
        self.listener = None
        self.enabled = True
        self._listener_lock = threading.Lock()
        self._force_stop = False
        self._uinput = None
        if _USE_EVDEV:
            try:
                self._uinput = evdev.UInput(
                    {ec.EV_KEY: [ec.KEY_BACKSPACE, ec.KEY_LEFTCTRL, ec.KEY_V]},
                    name='tex-expander'
                )
            except Exception as e:
                print(f"⚠️  UInput unavailable ({e}); backspace will fall back to wtype")

    def start_listening(self):
        with self._listener_lock:
            if self.listener is None and not self._force_stop:
                try:
                    if _USE_EVDEV:
                        candidate = _EvdevListener(on_press=self.on_key_press)
                        if candidate._devices:
                            self.listener = candidate
                        else:
                            # input group not yet active — fall back to pynput (in-app only)
                            print("⚠️  evdev: no accessible keyboard devices.")
                            print("    Global capture requires logging out and back in after:")
                            print("      sudo usermod -a -G input $USER")
                            print("    Falling back to in-app capture only.")
                            self.listener = Listener(on_press=self.on_key_press)
                    else:
                        self.listener = Listener(on_press=self.on_key_press)
                    self.listener.start()
                except Exception as e:
                    print(f"❌ Failed to start listener: {e}")

    def stop_listening(self):
        with self._listener_lock:
            self._force_stop = True
            if self.listener:
                try:
                    self.listener.stop()
                    self.listener = None
                    time.sleep(0.1)
                except Exception as e:
                    print(f"❌ Failed to stop listener: {e}")

    def on_key_press(self, key):
        if self._force_stop or not self.enabled:
            return
        try:
            if hasattr(key, 'char') and key.char is not None:
                if key.char.isprintable():
                    self.buffer += key.char
            elif key in [Key.space, Key.enter, Key.tab, Key.delete, Key.left,
                         Key.right, Key.up, Key.down, Key.home, Key.end,
                         Key.page_up, Key.page_down, Key.esc, Key.ctrl,
                         Key.shift, Key.alt, Key.alt_l, Key.alt_r, "\x01"]:
                if key == Key.space:
                    self.buffer += ' '
                elif key == Key.enter:
                    self.buffer += '\n'
                elif key == Key.tab:
                    self.buffer += '\t'
                self.check_abbreviations()
            elif key == Key.backspace:
                if self.buffer:
                    self.buffer = ''
            else:
                pass

        except AttributeError:
            pass

        if len(self.buffer) > self.buffer_size:
            self.buffer = self.buffer[-self.buffer_size:]

    def check_abbreviations(self):
        if self._force_stop or not self.enabled:
            return

        if not self.buffer.endswith(' '):
            return

        words = self.buffer.strip().split()
        if not words:
            return

        last_word = words[-1]
        for abbrev, replacement in self.abbreviations.items():
            if last_word == abbrev:
                self.expand_abbreviation(abbrev, replacement)
                break

    def expand_abbreviation(self, abbrev, replacement):
        if self._force_stop or not self.enabled:
            return

        if _USE_EVDEV:
            self._expand_wayland(abbrev, replacement)
        else:
            self._expand_xorg(abbrev, replacement)

    def _is_focused_xwayland(self):
        """Return True if the currently focused window is running under XWayland."""
        try:
            result = subprocess.run(
                ['hyprctl', 'activewindow', '-j'],
                capture_output=True, text=True, timeout=1
            )
            import json
            return json.loads(result.stdout).get('xwayland', False)
        except Exception:
            return False

    def _type_via_clipboard(self, text):
        """Paste text via wl-copy + Ctrl+V — handles all Unicode in XWayland apps."""
        try:
            old = subprocess.run(
                ['wl-paste', '-n'], capture_output=True, text=True, timeout=1
            ).stdout
        except Exception:
            old = None

        try:
            subprocess.run(['wl-copy', '--', text], timeout=1)
            time.sleep(0.02)
            if self._uinput:
                self._uinput.write(ec.EV_KEY, ec.KEY_LEFTCTRL, 1)
                self._uinput.write(ec.EV_KEY, ec.KEY_V, 1)
                self._uinput.syn()
                time.sleep(0.01)
                self._uinput.write(ec.EV_KEY, ec.KEY_V, 0)
                self._uinput.write(ec.EV_KEY, ec.KEY_LEFTCTRL, 0)
                self._uinput.syn()
                time.sleep(0.05)
        finally:
            if old is not None:
                time.sleep(0.05)
                try:
                    subprocess.run(['wl-copy', '--', old], timeout=1)
                except Exception:
                    pass

    def _expand_wayland(self, abbrev, replacement):
        """Expand on Wayland.
        Backspaces: UInput (kernel-level, reaches both XWayland and native Wayland).
        Text: clipboard paste for XWayland (Discord, Tkinter), wtype for native Wayland.
        """
        self.enabled = False
        try:
            self.buffer = self.buffer[:-len(abbrev) + 1]
            count = len(abbrev) + 1

            if self._uinput:
                for _ in range(count):
                    self._uinput.write(ec.EV_KEY, ec.KEY_BACKSPACE, 1)
                    self._uinput.write(ec.EV_KEY, ec.KEY_BACKSPACE, 0)
                    self._uinput.syn()
                time.sleep(0.04)
            else:
                args = ['wtype']
                for _ in range(count):
                    args.extend(['-k', 'BackSpace'])
                subprocess.run(args, timeout=5)
                time.sleep(0.04)

            text = replacement + ' '
            if self._is_focused_xwayland():
                self._type_via_clipboard(text)
            else:
                subprocess.run(['wtype', '--', text], timeout=5)

            self.buffer = ""
        except FileNotFoundError:
            print("❌ 'wtype' not found. Install it: sudo pacman -S wtype")
        except Exception as e:
            print(f"❌ Expansion error: {e}")
        finally:
            self.enabled = True

    def _expand_xorg(self, abbrev, replacement):
        """Expand using pynput Controller — works on Windows / X11."""
        was_enabled = self.enabled
        if was_enabled:
            self.stop_listening()
        try:
            self.buffer = self.buffer[:-len(abbrev) + 1]
            for _ in range(len(abbrev) + 1):
                self.controller.press(Key.backspace)
                self.controller.release(Key.backspace)
            self.controller.type(replacement + " ")
            self.buffer = ""
        finally:
            if was_enabled:
                self._force_stop = False
                self.enabled = True
                self.start_listening()

    def add_abbreviation(self, abbrev, replacement):
        self.abbreviations[abbrev] = replacement

    def remove_abbreviation(self, abbrev):
        if abbrev in self.abbreviations:
            del self.abbreviations[abbrev]

    def clear_abbreviations(self):
        self.abbreviations.clear()

    def set_enabled(self, enabled):
        print(f"🔧 Setting expansion enabled: {enabled}")
        if enabled:
            self._force_stop = False
            self.enabled = True
            self.start_listening()
            print("✅ Text expansion ENABLED - Listener started")
        else:
            self.enabled = False
            self.stop_listening()
            print("❌ Text expansion DISABLED - Listener stopped")
