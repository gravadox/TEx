import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import json
import os
import keyboard
from tray import TrayIcon

class TEx:
    def __init__(self, master):
        self.master = master
        self.master.title("TEx")
        self.data_file = "abbreviations.json"
        self.current_tag = "emoji"
        self.abbrev_dict = {}
        self.abbrev_hooks = {}
        self.editing_item_id = None
        self.tray_icon = TrayIcon(self)

        self.setup_ui()
        self.switch_page("emoji")

    def setup_ui(self):
        self.setup_styles()
        self.create_main_frame()
        self.create_sidebar()
        self.create_page_frame()
        self.create_treeview()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("classic")
        style.configure("Treeview", background="#151515", foreground="white", fieldbackground="#151515", borderwidth=0, highlightthickness=0, rowheight=30)
        style.configure("Treeview.Heading", background="#151515", foreground="white", fieldbackground="#151515", relief="flat", font=('Poppins', 12), padding=[0, 15])
        style.map("Treeview", background=[("selected", "#353535")], foreground=[("selected", "white")])
        style.map("Treeview.Heading", background=[('pressed', '#121212'), ('active', '#353535')], foreground=[('pressed', 'white'), ('active', 'white')])

    def create_main_frame(self):
        self.mainFrame = ctk.CTkFrame(master=self.master, fg_color="#151515")
        self.mainFrame.pack(fill="both", expand=True)
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(0, weight=0)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.grid_columnconfigure(2, weight=0)

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(master=self.mainFrame, width=50, fg_color="#151515")
        self.sidebar.grid(row=0, column=2, sticky="ns", pady=5)
        for tag in ["emoji", "sticker", "text", "link"]:
            self.create_sidebar_button(tag)

    def create_sidebar_button(self, tag_name):
        button = ctk.CTkButton(master=self.sidebar, text=tag_name.capitalize(), fg_color="transparent", 
                               text_color="white", hover_color="#353535", command=lambda: self.switch_page(tag_name))
        button.pack(fill="x", pady=5, padx=10)

    def create_page_frame(self):
        self.page_frame = ctk.CTkFrame(master=self.mainFrame, fg_color="#151515")
        self.page_frame.grid(row=0, column=0, sticky="nsew")
        self.create_entries_frame()

    def create_entries_frame(self):
        self.entries_frame = ctk.CTkFrame(master=self.page_frame, fg_color="#151515")
        self.entries_frame.pack(side="top", fill="x", padx=20, pady=(20, 0))
        self.nameEntry = ctk.CTkEntry(master=self.entries_frame, fg_color="transparent", border_color="white", placeholder_text="Name", placeholder_text_color="white", width=200, height=40, font=("Poppins", 12))
        self.nameEntry.grid(row=0, column=0, padx=5, pady=5)
        self.replacementEntry = ctk.CTkEntry(master=self.entries_frame, fg_color="transparent", border_color="white", placeholder_text="Replacement", placeholder_text_color="white", width=200, height=40, font=("Poppins", 12))
        self.replacementEntry.grid(row=1, column=0, padx=5, pady=5)
        self.button = ctk.CTkButton(master=self.entries_frame, text="Insert", fg_color="white", text_color="black", hover_color="#E8E8E8", width=200, height=40, font=("Poppins", 12), command=self.add_or_edit_abbreviation)
        self.button.grid(row=2, column=0, padx=5, pady=5)

    def create_treeview(self):
        self.tree_frame = ctk.CTkFrame(master=self.mainFrame, fg_color="#151515")
        self.tree_frame.grid(row=0, column=1, sticky="nsew")

        tree_scroll = ctk.CTkScrollbar(self.tree_frame, width=5)
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(master=self.tree_frame, yscrollcommand=tree_scroll.set, selectmode="none")

        # Define columns
        self.tree['columns'] = ("#", "Name", "Replacement", "Ignore", "Edit", "Delete")

        # Configure the #0 column to be hidden
        self.tree.column("#0", width=0, stretch=tk.NO)  # Hide the default #0 column

        # Configure other columns
        self.tree.column("#", anchor=tk.W, width=20)
        self.tree.column("Name", anchor=tk.W, width=80)
        self.tree.column("Replacement", anchor=tk.W, width=275)
        self.tree.column("Ignore", anchor=tk.W, width=50)
        self.tree.column("Edit", anchor=tk.W, width=20)
        self.tree.column("Delete", anchor=tk.W, width=20)

        # Set column headings
        self.tree.heading("#", text="#", anchor=tk.W)
        self.tree.heading("Name", text="Name", anchor=tk.W)
        self.tree.heading("Replacement", text="Replacement", anchor=tk.W)
        self.tree.heading("Ignore", text="Ignore", anchor=tk.W)
        self.tree.heading("Edit", text="Edit", anchor=tk.W)
        self.tree.heading("Delete", text="Delete", anchor=tk.W)

        self.tree.pack(side="left", fill="both", expand=True)
        tree_scroll.configure(command=self.tree.yview)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_item_click)

    def switch_page(self, tag_name):
        self.current_tag = tag_name
        self.load_abbreviations()
        self.apply_abbreviations()
        self.update_abbreviation_listbox()

    def load_abbreviations(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.abbrev_dict = json.load(f)
                    self.abbrev_hooks.clear()
                    for key, value in self.abbrev_dict.items():
                        if isinstance(value, dict) and not value.get('ignored', False):
                            self.abbrev_hooks[key] = keyboard.add_abbreviation(key, value['replacement'], timeout=5)
            except (json.JSONDecodeError, IOError):
                self.abbrev_dict = {}
        else:
            self.abbrev_dict = {}
        self.update_abbreviation_listbox()

    def save_abbreviations(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.abbrev_dict, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Failed to save abbreviations: {e}")

    def update_abbreviation_listbox(self):
        self.tree.delete(*self.tree.get_children())
        for source, data in self.abbrev_dict.items():
            if isinstance(data, dict) and data.get('tag') == self.current_tag:
                item_id = self.tree.insert("", "end", values=(len(self.tree.get_children()) + 1, source, data['replacement'], 
                                          "Unignored" if not data.get('ignored', False) else "Ignored"))
                self.tree.set(item_id, "Edit", "Edit")
                self.tree.set(item_id, "Delete", "Delete")
                self.tree.item(item_id, tags=("ignored",) if data.get('ignored', False) else ("unignored",))
        self.tree.tag_configure("ignored", foreground="#737373")
        self.tree.tag_configure("unignored", foreground="white")

    def apply_abbreviations(self):
        for hook in self.abbrev_hooks.values():
            keyboard.remove_word_listener(hook)
        self.abbrev_hooks.clear()
        for source, data in self.abbrev_dict.items():
            if not data.get('ignored', False):
                self.abbrev_hooks[source] = keyboard.add_abbreviation(source, data['replacement'], timeout=5)

    def add_or_edit_abbreviation(self):
        source = self.nameEntry.get().strip()
        replacement = self.replacementEntry.get().strip()
        if source == "" or replacement == "":
            return
        if self.editing_item_id:
            original_source = self.tree.item(self.editing_item_id)['values'][1]
            if original_source in self.abbrev_hooks:
                keyboard.remove_abbreviation(original_source)
                del self.abbrev_hooks[original_source]
            if original_source in self.abbrev_dict:
                del self.abbrev_dict[original_source]
            self.abbrev_dict[source] = {'replacement': replacement, 'ignored': False, 'tag': self.current_tag}
            self.abbrev_hooks[source] = keyboard.add_abbreviation(source, replacement, timeout=5)
            self.editing_item_id = None
        else:
            self.abbrev_dict[source] = {'replacement': replacement, 'ignored': False, 'tag': self.current_tag}
            self.abbrev_hooks[source] = keyboard.add_abbreviation(source, replacement, timeout=5)
        self.save_abbreviations()
        self.update_abbreviation_listbox()
        self.reset_ui()

    def reset_ui(self):
        self.button.configure(text="Insert", fg_color="white", text_color="black", hover_color="#E8E8E8")
        self.nameEntry.configure(border_color="white", placeholder_text_color="white")
        self.replacementEntry.configure(border_color="white", placeholder_text_color="white")
        self.nameEntry.delete(0, tk.END)
        self.replacementEntry.delete(0, tk.END)

    def edit_item(self, item_id):
        source = self.tree.item(item_id)['values'][1]
        data = self.abbrev_dict[source]
        self.nameEntry.delete(0, tk.END)
        self.nameEntry.insert(0, source)
        self.replacementEntry.delete(0, tk.END)
        self.replacementEntry.insert(0, data['replacement'])
        self.button.configure(text="Edit", fg_color="#55FF8E", hover_color="#55FF8E")
        self.nameEntry.configure(border_color="#55FF8E", placeholder_text_color="#55FF8E")
        self.replacementEntry.configure(border_color="#55FF8E", placeholder_text_color="#55FF8E")
        self.editing_item_id = item_id

    def delete_item(self, item_id):
        source = self.tree.item(item_id)['values'][1]
        if source in self.abbrev_dict:
            del self.abbrev_dict[source]
            self.save_abbreviations()
            self.update_abbreviation_listbox()
            self.apply_abbreviations()

    def toggle_ignore_item(self, item_id):
        source = self.tree.item(item_id)['values'][1]
        if source in self.abbrev_dict:
            self.abbrev_dict[source]['ignored'] = not self.abbrev_dict[source].get('ignored', False)
            self.save_abbreviations()
            self.update_abbreviation_listbox()
            self.apply_abbreviations()

    def on_tree_item_click(self, event):
        item_id = self.tree.identify_row(event.y)
        col = self.tree.identify_column(event.x)
        if item_id:
            if col == '#4':
                self.toggle_ignore_item(item_id)
            elif col == '#5':
                self.edit_item(item_id)
            elif col == '#6':
                self.delete_item(item_id)

    def run(self):
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)
        self.master.mainloop()

    def on_close(self):
        self.master.destroy()

    def minimize_to_tray(self):
        self.hide_main_window()
        self.tray_icon.create_tray_icon()

    def hide_main_window(self):
        self.master.withdraw()

    def show_main_window(self, icon=None, item=None):
        self.master.deiconify()
        self.tray_icon.destroy_tray_icon()

    def quit_application(self, icon=None, item=None):
        self.tray_icon.destroy_tray_icon()
        self.master.quit()

