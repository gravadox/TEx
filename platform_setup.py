import sys
import os
import platform

class PlatformSetup:
    @staticmethod
    def get_platform_info():
        """Get detailed platform information"""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'python_version': sys.version
        }
    
    @staticmethod
    def check_permissions():
        """Check if the app has necessary permissions"""
        system = platform.system()
        
        if system == "Darwin": 
            return PlatformSetup._check_macos_permissions()
        elif system == "Windows":
            return PlatformSetup._check_windows_permissions()
        elif system == "Linux":
            return PlatformSetup._check_linux_permissions()
        
        return True, "Unknown platform"
    
    @staticmethod
    def _check_macos_permissions():
        """Check macOS accessibility permissions"""
        try:
            from pynput import keyboard
            
            def test_key(key):
                pass
            
            listener = keyboard.Listener(on_press=test_key)
            listener.start()
            listener.stop()
            
            return True, "Accessibility permissions granted"
        except Exception as e:
            return False, f"Accessibility permissions required. Go to System Preferences > Security & Privacy > Privacy > Accessibility and add Python/Terminal. Error: {str(e)}"
    
    @staticmethod
    def _check_windows_permissions():
        """Check Windows permissions"""
        try:
            from pynput import keyboard
            
            def test_key(key):
                pass
            
            listener = keyboard.Listener(on_press=test_key)
            listener.start()
            listener.stop()
            
            return True, "Permissions OK"
        except Exception as e:
            return False, f"May need to run as administrator for some applications. Error: {str(e)}"
    
    @staticmethod
    def _check_linux_permissions():
        """Check Linux permissions"""
        try:
            from pynput import keyboard
            
            def test_key(key):
                pass
            
            listener = keyboard.Listener(on_press=test_key)
            listener.start()
            listener.stop()
            
            display = os.environ.get('DISPLAY')
            wayland = os.environ.get('WAYLAND_DISPLAY')
            
            if wayland:
                return True, "Running on Wayland - some features may be limited"
            elif display:
                return True, "Running on X11 - full functionality available"
            else:
                return False, "No display server detected"
                
        except Exception as e:
            return False, f"Permission error. Try running with appropriate user permissions. Error: {str(e)}"
    
    @staticmethod
    def setup_autostart():
        """Setup application to start automatically"""
        system = platform.system()
        
        if system == "Windows":
            return PlatformSetup._setup_windows_autostart()
        elif system == "Darwin":
            return PlatformSetup._setup_macos_autostart()
        elif system == "Linux":
            return PlatformSetup._setup_linux_autostart()
    
    @staticmethod
    def _setup_windows_autostart():
        """Setup Windows autostart via registry"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                               "Software\\Microsoft\\Windows\\CurrentVersion\\Run", 
                               0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "TEx", 0, winreg.REG_SZ, 
                            f'"{sys.executable}" "{os.path.abspath("main.py")}"')
            winreg.CloseKey(key)
            return True, "Autostart enabled for Windows"
        except Exception as e:
            return False, f"Failed to setup autostart: {e}"
    
    @staticmethod
    def _setup_macos_autostart():
        """Setup macOS autostart via LaunchAgent"""
        try:
            import plistlib
            
            plist_content = {
                'Label': 'com.tex.textexpander',
                'ProgramArguments': [sys.executable, os.path.abspath('main.py')],
                'RunAtLoad': True,
                'KeepAlive': False
            }
            
            launch_agents_dir = os.path.expanduser('~/Library/LaunchAgents')
            os.makedirs(launch_agents_dir, exist_ok=True)
            
            plist_path = os.path.join(launch_agents_dir, 'com.tex.textexpander.plist')
            
            with open(plist_path, 'wb') as f:
                plistlib.dump(plist_content, f)
            
            return True, "Autostart enabled for macOS"
        except Exception as e:
            return False, f"Failed to setup autostart: {e}"
    
    @staticmethod
    def _setup_linux_autostart():
        """Setup Linux autostart via .desktop file"""
        try:
            autostart_dir = os.path.expanduser('~/.config/autostart')
            os.makedirs(autostart_dir, exist_ok=True)
            
            desktop_content = f"""[Desktop Entry]
            Type=Application
            Name=TEx Text Expander
            Exec={sys.executable} {os.path.abspath('main.py')}
            Hidden=false
            NoDisplay=false
            X-GNOME-Autostart-enabled=true
            """
            
            desktop_path = os.path.join(autostart_dir, 'tex-textexpander.desktop')
            
            with open(desktop_path, 'w') as f:
                f.write(desktop_content)
            
            return True, "Autostart enabled for Linux"
        except Exception as e:
            return False, f"Failed to setup autostart: {e}"

if __name__ == "__main__":
    setup = PlatformSetup()
    
    print("=== TEx Platform Compatibility Check ===")
    print(f"Platform: {setup.get_platform_info()}")
    print()
    
    has_perms, perm_msg = setup.check_permissions()
    print(f"Permissions: {'✓' if has_perms else '✗'} {perm_msg}")
    print()
    
    if input("Setup autostart? (y/n): ").lower() == 'y':
        success, msg = setup.setup_autostart()
        print(f"Autostart: {'✓' if success else '✗'} {msg}")
