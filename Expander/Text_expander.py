from pynput.keyboard import Key, Listener, Controller
import threading
import time

class TextExpander:
    def __init__(self):
        self.abbreviations = {}
        self.buffer = ""
        self.buffer_size = 50
        self.controller = Controller()
        self.listener = None
        self.enabled = True
        self._listener_lock = threading.Lock()
        self._force_stop = False
    
    def start_listening(self):
        """Start the keyboard listener"""
        with self._listener_lock:
            if self.listener is None and not self._force_stop:
                try:
                    self.listener = Listener(on_press=self.on_key_press)
                    self.listener.start()
                    # print("🎧 Keyboard listener STARTED")
                except Exception as e:
                    print(f"❌ Failed to start listener: {e}")
    
    def stop_listening(self):
        """Stop the keyboard listener COMPLETELY"""
        with self._listener_lock:
            self._force_stop = True
            if self.listener:
                try:
                    self.listener.stop()
                    self.listener = None
                    # print("🛑 Keyboard listener STOPPED")
                    time.sleep(0.1)
                except Exception as e:
                    print(f"❌ Failed to stop listener: {e}")
   
    def on_key_press(self, key):
        """Handle key press events"""
        # print(f"Key pressed: {key}")
        if self._force_stop or not self.enabled:
            return
        try:
            if hasattr(key, 'char') and key.char is not None:
                if key.char.isprintable():
                    self.buffer += key.char
            elif key in [Key.space, Key.enter, Key.tab, key.delete, key.left, key.right, key.up, key.down, key.home, key.end, key.page_up, key.page_down, key.esc, key.ctrl,key.shift ,key.alt, key.alt_l, key.alt_r, "\x01"]:
                if key == Key.space:
                    self.buffer += ' '
                elif key == Key.enter:
                    self.buffer += '\n'
                elif key == Key.tab:
                    self.buffer += '\t'
                self.check_abbreviations()
            elif key == Key.backspace:
                if self.buffer:
                    self.buffer = '' # for now lets just make it that backspace clears the buffer, should find a way around ctrl+a+backspace in the future
                    # self.buffer = self.buffer[:-1]
            else:
                pass

        except AttributeError:
            pass

        if len(self.buffer) > self.buffer_size:
            self.buffer = self.buffer[-self.buffer_size:]

    def check_abbreviations(self):
        """Check if buffer ends with an abbreviation as a standalone word followed by space"""
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
        """Replace abbreviation with its expansion"""
        if self._force_stop or not self.enabled:
            return
            
        was_enabled = self.enabled
        if was_enabled:
            self.stop_listening()
        
        try:
            self.buffer = self.buffer[:-len(abbrev)+1]
            
            for _ in range(len(abbrev) + 1):
                self.controller.press(Key.backspace)
                self.controller.release(Key.backspace)
            
            self.controller.type(replacement+" ")
            # print(f"🔄 Expanded: {abbrev} -> {replacement}")
            
            self.buffer = ""
        finally:
            if was_enabled:
                self._force_stop = False
                self.enabled = True
                self.start_listening()
    
    def add_abbreviation(self, abbrev, replacement):
        """Add a new abbreviation"""
        self.abbreviations[abbrev] = replacement
    
    def remove_abbreviation(self, abbrev):
        """Remove an abbreviation"""
        if abbrev in self.abbreviations:
            del self.abbreviations[abbrev]
    
    def clear_abbreviations(self):
        """Clear all abbreviations"""
        self.abbreviations.clear()
    
    def set_enabled(self, enabled):
        """Enable or disable text expansion"""
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
