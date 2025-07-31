from app import TEx
import os

if __name__ == "__main__":
    app = TEx()
    
    try:
        icon_path = os.path.abspath('icon.ico')
        if os.path.exists(icon_path):
            app.iconbitmap(icon_path)
        else:
            print(f"Warning: icon.ico not found at {icon_path}. Using default icon.")
    except Exception as e:
        print(f"Error setting icon: {e}. Using default icon.")


    app.resizable(True, True)
    app.minsize(width=1000, height=400) 
    app.geometry("1100x600")
    
    app.Show_tray()
    app.protocol("WM_DELETE_WINDOW", app.minimize_to_tray)
    
    app.mainloop()
