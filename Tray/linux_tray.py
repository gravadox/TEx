import os
import threading
import psutil
from notifypy import Notify

WAYLAND = os.environ.get("XDG_SESSION_TYPE") == "wayland"

if WAYLAND:
    import gi
    gi.require_version('AppIndicator3', '0.1')
    gi.require_version('Gtk', '3.0')
    from gi.repository import AppIndicator3, Gtk, GLib
else:
    import pystray
    from pystray import MenuItem as item
    from PIL import Image, ImageDraw

from Elements.buffer_window import show_buffer_window

class TrayIcon:
    def __init__(self, app):
        self.app = app
        self.tray_icon = None
        self.tray_thread = None
        self.show_buffer_window = lambda icon=None, item=None: show_buffer_window(self, icon="icon.png")
        self.icon_path = self.get_icon_path()

    def get_icon_path(self):
        """Get the absolute path to the icon file"""
        possible_paths = [
            "icon.png",
            "icon.ico", 
            os.path.join(os.path.dirname(__file__), "icon.png"),
            os.path.join(os.path.dirname(__file__), "icon.ico"),
            os.path.join(os.path.dirname(__file__), "..", "icon.png"),
            os.path.join(os.path.dirname(__file__), "..", "icon.ico"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return os.path.abspath(path)
        
        return None

    # -------------------- Public --------------------
    def create_tray_icon(self):
        if WAYLAND:
            self.create_wayland_tray()
        else:
            self.create_x11_tray()

    def destroy_tray_icon(self):
        try:
            if WAYLAND:
                def quit_gtk():
                    try:
                        Gtk.main_quit()
                    except:
                        pass
                    return False
                
                try:
                    from gi.repository import GLib
                    GLib.idle_add(quit_gtk)
                except:
                    # Fallback if GLib is not available
                    try:
                        Gtk.main_quit()
                    except:
                        pass
            else:
                if self.tray_icon:
                    self.tray_icon.stop()
                    self.tray_icon = None
            print("Tray icon destroyed")
        except Exception as e:
            print(f"Destroy tray error: {e}")

    # -------------------- Shared Methods --------------------
    def toggle_window(self):
        try:
            if self.app.winfo_exists() and self.app.winfo_viewable():
                self.app.withdraw()
            else:
                self.app.deiconify()
                self.app.lift()
                self.app.focus_force()
        except Exception as e:
            print(f"Window toggle error: {e}")
            # Try to recreate or show the window if it was destroyed
            try:
                self.app.deiconify()
                self.app.lift()
                self.app.focus_force()
            except Exception as e2:
                print(f"Failed to restore window: {e2}")

    def toggle_expansion(self):
        current_state = self.app.text_expander.enabled
        new_state = not current_state
        self.app.text_expander.set_enabled(new_state)
        if new_state:
            self.show_notification("Text expansion ENABLED")
        else:
            self.show_notification("Text expansion DISABLED")
        if not WAYLAND:
            self.update_x11_menu()

    def clear_buffer(self):
        self.app.text_expander.buffer = ""
        self.show_notification("Buffer cleared")

    def show_stats(self):
        total_abbrevs = len([k for k, v in self.app.abbrev_dict.items() 
                             if isinstance(v, dict) and not v.get('ignored', False)])
        active_abbrevs = len(self.app.text_expander.abbreviations)
        status = 'ENABLED' if self.app.text_expander.enabled else 'DISABLED'

        category_data = self.app.category_manager.categories if hasattr(self.app, 'category_manager') else {}
        total_categories = len(category_data)
        encrypted_categories = sum(1 for cat in category_data.values() if cat.get('is_encrypted'))

        process = psutil.Process(os.getpid())
        memory_mb = process.memory_info().rss / (1024 * 1024)
        cpu_percent = process.cpu_percent(interval=0.1)

        stats_msg = (
            f"Total Abbrevs: {total_abbrevs} | Active: {active_abbrevs}\n"
            f"Categories: {total_categories} | Encrypted: {encrypted_categories}\n"
            f"Status: {status}\n"
            f"Memory: {memory_mb:.1f} MB | CPU: {cpu_percent:.1f}%"
        )

        self.show_notification("TEx Statistics", stats_msg)

    def show_notification(self, title, message=""):
        try:
            notification = Notify()
            notification.application_name = "TEx - Text Expander"
            notification.title = title
            notification.message = message
            notification.icon = "icon.png"
            notification.send()
        except Exception as e:
            print(f"Notification error: {e}")

    def quit_app(self):
        try:
            # First destroy the tray icon
            self.destroy_tray_icon()
            
            # Then quit the application
            if hasattr(self.app, 'quit_application'):
                self.app.quit_application()
            else:
                # Fallback quit methods
                try:
                    self.app.quit()
                except:
                    self.app.destroy()
                    
            # Force exit if still running
            import sys
            sys.exit(0)
        except Exception as e:
            print(f"Quit error: {e}")
            import sys
            sys.exit(1)

    # -------------------- Wayland --------------------
    def create_wayland_tray(self):
        if self.icon_path and self.icon_path.endswith('.ico'):
            # Convert ICO to PNG for AppIndicator3 compatibility
            try:
                from PIL import Image
                ico_image = Image.open(self.icon_path)
                png_path = self.icon_path.replace('.ico', '.png')
                ico_image.save(png_path, 'PNG')
                icon_name = os.path.abspath(png_path)
            except Exception as e:
                print(f"Icon conversion error: {e}")
                icon_name = "application-default-icon"  # Fallback to theme icon
        elif self.icon_path:
            icon_name = os.path.abspath(self.icon_path)
        else:
            icon_name = "application-default-icon"  # Fallback to theme icon
            
        self.tray_icon = AppIndicator3.Indicator.new(
            "TEx", icon_name, AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.tray_icon.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        if self.icon_path and os.path.exists(self.icon_path):
            try:
                self.tray_icon.set_icon_full(os.path.abspath(self.icon_path), "TEx Icon")
                print(f"Icon set successfully: {self.icon_path}")
            except Exception as e:
                print(f"Error setting custom icon: {e}")
        
        menu = Gtk.Menu()

        def add_item(label, callback):
            mi = Gtk.MenuItem(label=label)
            mi.connect("activate", lambda w: callback())
            mi.show()
            menu.append(mi)

        add_item("Show/Hide TEx", self.toggle_window)
        add_item("Toggle Expansion", self.toggle_expansion)
        add_item("Show Buffer", self.show_buffer_window)
        add_item("Clear Buffer", self.clear_buffer)
        add_item("Statistics", self.show_stats)
        add_item("Quit TEx", self.quit_app)

        self.tray_icon.set_menu(menu)
        def gtk_main_wrapper():
            try:
                Gtk.main()
            except KeyboardInterrupt:
                pass
            except Exception as e:
                print(f"GTK main loop error: {e}")
        
        threading.Thread(target=gtk_main_wrapper, daemon=True).start()
        print("Wayland tray created")

    # -------------------- X11 --------------------
    def create_x11_tray(self):
        if self.tray_icon:
            return

        try:
            if self.icon_path and os.path.exists(self.icon_path):
                try:
                    image = Image.open(self.icon_path)
                    print(f"Loaded icon from: {self.icon_path}")
                except Exception as e:
                    print(f"Error loading icon from {self.icon_path}: {e}")
                    image = self.create_simple_icon()
            else:
                print(f"Icon file not found at: {self.icon_path}")
                image = self.create_simple_icon()

            menu = pystray.Menu(
                item('Show/Hide TEx', lambda icon, item: self.toggle_window(), default=True),
                pystray.Menu.SEPARATOR,
                item('Toggle Expansion', lambda icon, item: self.toggle_expansion(),
                     checked=lambda item: self.app.text_expander.enabled),
                pystray.Menu.SEPARATOR,
                item('Show Buffer', self.show_buffer_window),
                item('Clear Buffer', lambda icon, item: self.clear_buffer()),
                item('Statistics', lambda icon, item: self.show_stats()),
                pystray.Menu.SEPARATOR,
                item('Quit TEx', lambda icon, item: self.quit_app())
            )

            self.tray_icon = pystray.Icon("TEx", image, "TEx - Text Expander", menu)

            def on_click(icon, button, time):
                if button == pystray.MouseButton.LEFT:
                    self.toggle_window()

            self.tray_icon.on_click = on_click

            def run_tray():
                try:
                    self.tray_icon.run()
                except Exception as e:
                    print(f"Tray error: {e}")

            self.tray_thread = threading.Thread(target=run_tray, daemon=True)
            self.tray_thread.start()
            print("X11 tray created")
        except Exception as e:
            print(f"Failed to create tray icon: {e}")

    def create_simple_icon(self):
        image = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.ellipse([4, 4, 60, 60], fill=(70, 130, 180, 255), outline=(255, 255, 255, 255), width=2)
        draw.text((25, 20), "T", fill=(255, 255, 255, 255))
        return image

    def update_x11_menu(self):
        if self.tray_icon:
            self.tray_icon.menu = pystray.Menu(
                item('Show/Hide TEx', lambda icon, item: self.toggle_window(), default=True),
                pystray.Menu.SEPARATOR,
                item('Toggle Expansion', lambda icon, item: self.toggle_expansion(),
                     checked=lambda item: self.app.text_expander.enabled),
                pystray.Menu.SEPARATOR,
                item('Show Buffer', self.show_buffer_window),
                item('Clear Buffer', lambda icon, item: self.clear_buffer()),
                item('Statistics', lambda icon, item: self.show_stats()),
                pystray.Menu.SEPARATOR,
                item('Quit TEx', lambda icon, item: self.quit_app())
            )
