import pystray
from PIL import Image, ImageDraw
from pystray import MenuItem as item
import threading
from Elements.buffer_window import show_buffer_window
import psutil
import os
from notifypy import Notify

class TrayIcon:
    def __init__(self, app):
        self.app = app
        self.tray_icon = None
        self.tray_thread = None
        self.show_buffer_window = lambda icon=None, item=None: show_buffer_window(self, icon="icon.png")

    def create_simple_icon(self):
        """Create a simple icon if icon.ico doesn't exist"""

        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        draw.ellipse([4, 4, 60, 60], fill=(70, 130, 180, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((25, 20), "T", fill=(255, 255, 255, 255))
        
        return image

    def create_tray_icon(self):
        if self.tray_icon:
            return

        try:
            try:
                image = Image.open("icon.ico")
            except (FileNotFoundError, OSError):
                image = self.create_simple_icon()
            
            menu = pystray.Menu(
                item('Show/Hide TEx', self.toggle_window, default=True),
                pystray.Menu.SEPARATOR,
                item('Toggle Expansion', self.toggle_expansion, checked=lambda item: self.app.text_expander.enabled),
                pystray.Menu.SEPARATOR,
                item('Show Buffer', self.show_buffer_window), 
                item('Clear Buffer', self.clear_buffer),
                item('Statistics', self.show_stats),
                pystray.Menu.SEPARATOR,
                item('Quit TEx', self.quit_app)
            )            
            self.tray_icon = pystray.Icon(
                "TEx", 
                image, 
                "TEx - Text Expander", 
                menu
            )
            
            def on_click(icon, button, time):
                if button == pystray.MouseButton.left:
                    self.toggle_window()
            
            self.tray_icon.on_click = on_click
            
            def run_tray():
                try:
                    self.tray_icon.run()
                except Exception as e:
                    print(f"Tray error: {e}")
            
            self.tray_thread = threading.Thread(target=run_tray, daemon=True)
            self.tray_thread.start()
            
            print("Tray icon created successfully")
            
        except Exception as e:
            print(f"Failed to create tray icon: {e}")

    def toggle_window(self):
        """Toggle window visibility"""
        try:
            if self.app.winfo_viewable():
                self.hide_window()
            else:
                self.show_window()
        except Exception as e:
            print(f"Toggle error: {e}")
            self.show_window()

    def show_window(self, icon=None, item=None):
        """Show the main window"""
        try:
            self.app.deiconify()
            self.app.lift()
            self.app.focus_force()
            print("Window shown")
        except Exception as e:
            print(f"Show window error: {e}")

    def hide_window(self, icon=None, item=None):
        """Hide the main window"""
        try:
            self.app.withdraw()
            print("Window hidden")
        except Exception as e:
            print(f"Hide window error: {e}")

    def toggle_expansion(self, icon=None, item=None):
        """Toggle text expansion on/off"""
        try:
            current_state = self.app.text_expander.enabled
            new_state = not current_state
            
            print(f"Toggling expansion: {current_state} -> {new_state}")
            
            self.app.text_expander.set_enabled(new_state)
            
            if new_state:
                self.show_notification("Text expansion ENABLED")
                print("✅ Expansion ENABLED from tray")
            else:
                self.show_notification("Text expansion DISABLED")
                print("❌ Expansion DISABLED from tray")
                
            self.update_menu()
            
        except Exception as e:
            print(f"Toggle expansion error: {e}")

    def update_menu(self):
        """Update the tray menu to reflect current state"""
        try:
            if self.tray_icon:
                menu = pystray.Menu(
                    item('Show/Hide TEx', self.toggle_window, default=True),
                    pystray.Menu.SEPARATOR,
                    item('Toggle Expansion', self.toggle_expansion, checked=lambda item: self.app.text_expander.enabled),
                    pystray.Menu.SEPARATOR,
                    item('Show Buffer', self.show_buffer_window),
                    item('Clear Buffer', self.clear_buffer),
                    item('Statistics', self.show_stats),
                    pystray.Menu.SEPARATOR,
                    item('Quit TEx', self.quit_app)
                )

                self.tray_icon.menu = menu
        except Exception as e:
            print(f"Update menu error: {e}")

    def clear_buffer(self, icon=None, item=None):
        """Clear the text expansion buffer"""
        try:
            self.app.text_expander.buffer = ""
            self.show_notification("Buffer cleared")
        except Exception as e:
            print(f"Clear buffer error: {e}")

    def show_stats(self, icon=None, item=None):
        """Show expansion statistics"""
        try:
            # Abbreviation stats
            total_abbrevs = len([k for k, v in self.app.abbrev_dict.items() 
                                 if isinstance(v, dict) and not v.get('ignored', False)])
            active_abbrevs = len(self.app.text_expander.abbreviations)
            status = 'ENABLED' if self.app.text_expander.enabled else 'DISABLED'

            # Category stats
            category_data = self.app.category_manager.categories if hasattr(self.app, 'category_manager') else {}
            total_categories = len(category_data)
            encrypted_categories = sum(1 for cat in category_data.values() if cat.get('is_encrypted'))
            # Resource usage
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / (1024 * 1024)  # Resident Set Size in MB
            cpu_percent = process.cpu_percent(interval=0.1)

            # Build stats message
            stats_msg = (
                f"Total Abbrevs: {total_abbrevs} | Active: {active_abbrevs}\n"
                f"Categories: {total_categories} | Encrypted: {encrypted_categories}\n"
                f"Status: {status}\n"
                f"Memory: {memory_mb:.1f} MB | CPU: {cpu_percent:.1f}%"
            )

            self.show_notification("TEx Statistics", stats_msg)

        except Exception as e:
            print(f"Show stats error: {e}")

    def show_notification(self, title, message=""):
        try:
            notification = Notify()
            notification.application_name = "TEx - Text Expander" ,
            notification._notification_application_name = "TEx - Text Expander",
            notification.app_id = "TEx - Text Expander"
            notification.title = title
            notification.message = message
            notification.icon = "icon.ico"  # or "path/to/your/icon.png"
            notification.send()
        except Exception as e:
            print(f"Notification error: {e}")

    def quit_app(self, icon=None, item=None):
        """Quit the application"""
        try:
            self.app.quit_application()
        except Exception as e:
            print(f"Quit error: {e}")

    def destroy_tray_icon(self):
        """Destroy the tray icon"""
        try:
            if self.tray_icon:
                self.tray_icon.stop()
                self.tray_icon = None
            if self.tray_thread:
                self.tray_thread = None
            print("Tray icon destroyed")
        except Exception as e:
            print(f"Destroy tray error: {e}")