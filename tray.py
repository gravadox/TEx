import pystray
from PIL import Image
from pystray import MenuItem as item
import threading

class TrayIcon:
    def __init__(self, app):
        self.app = app
        self.tray_icon = None
        self.tray_thread = None

    def create_tray_icon(self):
        if self.tray_icon:
            return

        image = Image.open("icon.ico")
        menu = (
            item('Show', self.app.show_main_window),
            item('Quit', self.app.quit_application)
        )
        self.tray_icon = pystray.Icon("name", image, "App Name", menu)
        self.tray_thread = threading.Thread(target=self.tray_icon.run)
        self.tray_thread.start()

    def destroy_tray_icon(self):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
            if self.tray_thread and threading.current_thread() != self.tray_thread:
                self.tray_thread.join()
            self.tray_thread = None
