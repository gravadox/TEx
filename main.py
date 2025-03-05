import customtkinter as ctk
from app import TEx

if __name__ == "__main__":
    root = ctk.CTk()
    root.iconbitmap('icon.ico')
    root.resizable(True, True)
    
    root.minsize(width=1000, height=400) 
    
    app = TEx(master=root)
    root.protocol("WM_DELETE_WINDOW", app.minimize_to_tray)
    root.geometry("1100x600")
    root.mainloop()