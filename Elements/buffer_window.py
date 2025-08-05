import customtkinter as ctk
import webbrowser

def show_buffer_window(self, icon=None, item=None):
    """Open a small CTk window displaying the live buffer"""
    try:
        if hasattr(self, 'buffer_window') and self.buffer_window and self.buffer_window.winfo_exists():
            self.buffer_window.lift()
            return
        

        # Dark theme
        ctk.set_appearance_mode("dark")

        # Create window, but keep it hidden during setup
        self.buffer_window = ctk.CTkToplevel(self.app)
        self.buffer_window.withdraw()  # Hide initially
        self.buffer_window.title("TEx Buffer")
        self.buffer_window.geometry("500x300")
        self.buffer_window.configure(fg_color="#151515")
        self.buffer_window.resizable(False, False)
 
        # Layout
        frame = ctk.CTkFrame(self.buffer_window, fg_color="#151515")
        frame.pack(expand=True, fill="both", padx=10, pady=10)

        # Live buffer display
        self.buffer_text = ctk.CTkTextbox(frame, wrap="word", font=("Consolas", 12), height=8)
        self.buffer_text.pack(expand=True, fill="both", padx=0, pady=(0, 10))
        self.buffer_text.configure(state="disabled")

        # Privacy text
        info_text = (
            "🔒 Your keyboard input is not shared.\n"
            "It's stored only on your device in a local buffer of 50 characters to activate the expansion.\n"
            "You can verify this in the source code:"
        )

        info_label = ctk.CTkLabel(
            frame,
            text=info_text,
            text_color="#AAAAAA",
            font=("Segoe UI", 10),
            justify="left",
            anchor="w",
            wraplength=480
        )
        info_label.pack(fill="x", padx=2, pady=(0, 0))  # no extra space below

        # GitHub clickable link
        link_url = "https://github.com/gravadox/TEx/blob/main/Expander/Text_expander.py"
        link_label = ctk.CTkLabel(
            frame,
            text="https://github.com/gravadox/TEx/",
            text_color="#E0E0E0",
            font=("Segoe UI", 10, "underline"),
            cursor="hand2"
        )
        link_label.pack(anchor="w", padx=2, pady=(0, 0))  # tight spacing
        link_label.bind("<Button-1>", lambda e: webbrowser.open(link_url))

        # Update buffer every 500ms
        def update_buffer():
            if self.buffer_window and self.buffer_window.winfo_exists():
                current = self.app.text_expander.buffer
                self.buffer_text.configure(state="normal")
                self.buffer_text.delete("1.0", "end")
                self.buffer_text.insert("end", current)
                self.buffer_text.configure(state="disabled")
                self.buffer_window.after(500, update_buffer)

        update_buffer()

        # Now show the window after setup is complete
        self.buffer_window.deiconify()
        self.buffer_window.lift()
        self.buffer_window.focus_force()

    except Exception as e:
        print(f"Error showing buffer window: {e}")
