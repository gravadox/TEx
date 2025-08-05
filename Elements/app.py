import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
import json
import os
from Tray.tray import TrayIcon
from Elements.category_manager import CategoryManager
from Elements.category_dialog import CategoryManagerDialog
from Encryption.encryption_util import EncryptionUtil
from Expander.Text_expander import TextExpander

""""Main TEx application class"""

class TEx(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TEx")
        self.data_file = "user/Expansions.json"
        self.current_tag = "emoji"
        self.abbrev_dict = {}
        self.editing_item_id = None
        self.category_manager = CategoryManager()
        self.encryption_key = self.get_or_create_key()
        self.text_expander = TextExpander()
        self.text_expander.start_listening()
        self.tray_icon = TrayIcon(self)
        self.setup_ui()

        initial_category = "emoji"
        if not self.category_manager.category_exists("emoji"):
            non_encrypted_cats = [
                cid for cid, cdata in self.category_manager.get_all_categories().items()
                if not cdata.get("is_encrypted", False)
            ]
            if non_encrypted_cats:
                initial_category = non_encrypted_cats[0]
            else:
                initial_category = None
                self.abbrev_dict = {}  
                self.tree.delete(*self.tree.get_children())

        if initial_category:
            self.switch_page(initial_category)
        else:
            self.current_tag = None

    def get_or_create_key(self) -> str:
        token_name = "TExEncryptionKey"
        key = EncryptionUtil.load_key_from_keyring(token_name)
        # print(f"🔑 Loaded encryption key: {key}")
        if key is None:
            key = EncryptionUtil.generate_key()
            EncryptionUtil.save_key_to_keyring(token_name, key)
            # print(f"🔑 Generated new encryption key: {key}")
        return key

    def setup_ui(self):
        self.setup_styles()
        self.create_main_frame()
        self.create_sidebar()
        self.create_page_frame()
        self.create_treeview()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("classic")
        
        style.configure("Treeview", 
                       background="#151515", 
                       foreground="white", 
                       fieldbackground="#151515", 
                       borderwidth=0, 
                       highlightthickness=0, 
                       rowheight=30)
        
        style.configure("Treeview.Heading", 
                       background="#151515", 
                       foreground="white", 
                       fieldbackground="#151515", 
                       relief="flat", 
                       font=('Poppins', 12), 
                       padding=[0, 15])
        
        style.map("Treeview", 
                 background=[("selected", "#353535")], 
                 foreground=[("selected", "white")])
        
        style.map("Treeview.Heading", 
                 background=[('pressed', '#0d0d0d'), ('active', '#333333')], 
                 foreground=[('pressed', 'white'), ('active', 'white')])

    def create_main_frame(self):
        self.mainFrame = ctk.CTkFrame(master=self, fg_color="#151515")
        self.mainFrame.pack(fill="both", expand=True)
        self.mainFrame.grid_rowconfigure(0, weight=1)
        self.mainFrame.grid_columnconfigure(0, weight=0)
        self.mainFrame.grid_columnconfigure(1, weight=1)
        self.mainFrame.grid_columnconfigure(2, weight=0)

    def create_sidebar(self):
        self.sidebar = ctk.CTkFrame(master=self.mainFrame, width=50, fg_color="#151515")
        self.sidebar.grid(row=0, column=2, sticky="ns", pady=5)
        
        manage_btn = ctk.CTkButton(
            master=self.sidebar, 
            text="⚙️ Manage", 
            fg_color="#333333", 
            text_color="white", 
            hover_color="#555555", 
            command=self.open_category_manager,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        manage_btn.pack(fill="x", padx=20, pady=10)
        
        separator = ctk.CTkFrame(master=self.sidebar, height=2, fg_color="#333333")
        separator.pack(fill="x", padx=10, pady=5)
        
        self.refresh_sidebar()

    def refresh_sidebar(self):
        """Refresh sidebar with current categories"""
        children = list(self.sidebar.winfo_children())
        for child in children[2:]:
            child.destroy()
        
        categories = self.category_manager.get_all_categories()
        for category_id, category_data in categories.items():
            self.create_dynamic_sidebar_button(category_id, category_data)

    def create_dynamic_sidebar_button(self, category_id, category_data):
        """Create a dynamic sidebar button for a category"""
        icon = category_data.get("icon", "📁")
        name = category_data.get("name", category_id.capitalize())
        color = category_data.get("color", "#808080")
        
        display_name = f"{icon} {name}"
        if category_data.get("is_encrypted", False):
            display_name += " 🔒"

        button = ctk.CTkButton(
            master=self.sidebar, 
            text=display_name, 
            fg_color="transparent",
            text_color="white", 
            hover_color=color,
            command=lambda cat_id=category_id: self.switch_page(cat_id),
            font=ctk.CTkFont(size=12)
        )
        button.pack(fill="x", padx=10, pady=2)

    def open_category_manager(self):
        """Open the category management dialog"""
        CategoryManagerDialog(self, self.category_manager, self)

    def create_page_frame(self):
        self.page_frame = ctk.CTkFrame(master=self.mainFrame, fg_color="#151515")
        self.page_frame.grid(row=0, column=0, sticky="nsew")
        self.create_entries_frame()

    def create_entries_frame(self):
        self.entries_frame = ctk.CTkFrame(master=self.page_frame, fg_color="#151515")
        self.entries_frame.pack(fill="x", padx=20, pady=(20, 0), side="top")
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
        tree_scroll.pack(fill="y", side="right")

        self.tree = ttk.Treeview(master=self.tree_frame, yscrollcommand=tree_scroll.set, selectmode="none",)

        self.tree['columns'] = ("#", "Name", "Replacement", "Ignore", "Edit", "Delete")

        self.tree.column("#0", width=0, stretch=tk.NO)

        self.tree.column("#", anchor=tk.W, width=20)
        self.tree.column("Name", anchor=tk.W, width=80)
        self.tree.column("Replacement", anchor=tk.W, width=275)
        self.tree.column("Ignore", anchor=tk.W, width=50)
        self.tree.column("Edit", anchor=tk.W, width=20)
        self.tree.column("Delete", anchor=tk.W, width=20)

        self.tree.heading("#", text="#", anchor=tk.W)
        self.tree.heading("Name", text="Name", anchor=tk.W)
        self.tree.heading("Replacement", text="Replacement", anchor=tk.W)
        self.tree.heading("Ignore", text="Ignore", anchor=tk.W)
        self.tree.heading("Edit", text="Edit", anchor=tk.W)
        self.tree.heading("Delete", text="Delete", anchor=tk.W)

        self.tree.pack(expand=True, fill="both", side="left")
        tree_scroll.configure(command=self.tree.yview)
        self.tree.bind("<ButtonRelease-1>", self.on_tree_item_click)

    def switch_page(self, tag_name):
        if not self.category_manager.category_exists(tag_name):
            available_categories = self.category_manager.get_category_list()
            if available_categories:
                tag_name = available_categories[0]
            else:
                tag_name = "emoji" 
                if not self.category_manager.category_exists("emoji"):
                    self.category_manager.add_category("emoji", "Emojis", "😀", "#FFD700", is_encrypted=False)
                
        category_data = self.category_manager.get_category(tag_name)

        if category_data and category_data.get("is_encrypted", False):
            if not self.encryption_key:
                
                non_encrypted_categories = [
                    cat_id for cat_id, data in self.category_manager.get_all_categories().items()
                    if not data.get("is_encrypted", False)
                ]
                if non_encrypted_categories:
                    self.current_tag = non_encrypted_categories[0]
                else:
                    self.current_tag = None
                    self.tree.delete(*self.tree.get_children())
                    self.abbrev_dict = {}
                return 

        self.current_tag = tag_name
        self.load_abbreviations()
        self.apply_abbreviations()
        self.update_abbreviation_listbox()

    def load_abbreviations(self):
        self.abbrev_dict = {}
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    for source, data in loaded_data.items():
                        if isinstance(data, dict) and 'tag' in data:
                            category_data = self.category_manager.get_category(data['tag'])
                            
                            if category_data and category_data.get('is_encrypted', False):
                                original_encrypted_value = data['replacement'] 
                                
                                if self.encryption_key:
                                    decrypted_replacement = EncryptionUtil.decrypt_data(original_encrypted_value, self.encryption_key)
                                    self.abbrev_dict[source] = {
                                        'replacement': decrypted_replacement,
                                        'original_encrypted': original_encrypted_value, 
                                        'ignored': data.get('ignored', False),
                                        'tag': data['tag']
                                    }
                                else:
                                    self.abbrev_dict[source] = {
                                        'replacement': "[ENCRYPTED - LOCKED]",
                                        'original_encrypted': original_encrypted_value,
                                        'ignored': data.get('ignored', False),
                                        'tag': data['tag']
                                    }
                            else:
                                self.abbrev_dict[source] = data
                        else:
                            self.abbrev_dict[source] = {'replacement': data, 'ignored': False, 'tag': 'text'}
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading abbreviations: {e}")
                self.abbrev_dict = {}
        self.update_abbreviation_listbox()

    def save_abbreviations(self):
        data_to_save = {}
        for source, data in self.abbrev_dict.items():
            category_data = self.category_manager.get_category(data['tag'])
            if category_data and category_data.get('is_encrypted', False):
                if self.encryption_key:
                    encrypted_replacement = EncryptionUtil.encrypt_data(data['replacement'], self.encryption_key)
                    data_to_save[source] = {
                        'replacement': encrypted_replacement,
                        'ignored': data.get('ignored', False),
                        'tag': data['tag']
                    }
                else:
                    if 'original_encrypted' in data and data['original_encrypted'] is not None:
                        data_to_save[source] = {
                            'replacement': data['original_encrypted'],
                            'ignored': data.get('ignored', False),
                            'tag': data['tag']
                        }
                    else:
  
                        print(f"Warning: Skipping save for new/unencryptable item '{source}' in locked category '{data['tag']}'.")
                        continue
            else:
                data_to_save[source] = data
        
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except IOError as e:
            print(f"Failed to save abbreviations: {e}")

    def update_abbreviation_listbox(self):
        self.tree.delete(*self.tree.get_children())
        if self.current_tag is None:
            return

        for source, data in self.abbrev_dict.items():
            if isinstance(data, dict) and data.get('tag') == self.current_tag:
                item_id = self.tree.insert("", "end", values=(len(self.tree.get_children()) + 1, source, data['replacement'], 
                                                              "Unignored" if not data.get('ignored', False) else "Ignored"))
                self.tree.set(item_id, "Edit", "Edit")
                self.tree.set(item_id, "Delete", "Delete")
                self.tree.item(item_id, tags=("ignored",) if data.get('ignored', False) else ("unignored",))
    
        self.tree.tag_configure("ignored", foreground="#888888", background="#2b2b2b")
        self.tree.tag_configure("unignored", foreground="white", background="#151515")

    def apply_abbreviations(self):
        """Apply all active and decrypted abbreviations to the text expander"""
        self.text_expander.clear_abbreviations()
    
        for source, data in self.abbrev_dict.items():
            if isinstance(data, dict) and not data.get('ignored', False):
                if not data['replacement'].startswith("[DECRYPTION FAILED") and \
                   not data['replacement'].startswith("[ENCRYPTED - LOCKED]"):
                    self.text_expander.add_abbreviation(source, data['replacement'])
    
    def add_or_edit_abbreviation(self):
        source = self.nameEntry.get().strip()
        replacement = self.replacementEntry.get().strip()
        if source == "" or replacement == "":
            return
        
        category_data = self.category_manager.get_category(self.current_tag)
        is_current_category_encrypted = category_data and category_data.get("is_encrypted", False)

        if is_current_category_encrypted and not self.encryption_key:
            return

        original_encrypted_to_preserve = None

        if self.editing_item_id:
            original_source = self.tree.item(self.editing_item_id)['values'][1]
            if original_source in self.abbrev_dict:
                if self.abbrev_dict[original_source].get('tag') == self.current_tag and \
                   self.category_manager.get_category(self.current_tag).get("is_encrypted", False):
                    original_encrypted_to_preserve = self.abbrev_dict[original_source].get('original_encrypted')

                if not self.abbrev_dict[original_source].get('ignored', False) and self.abbrev_dict[original_source].get('tag') == self.current_tag:
                    self.text_expander.remove_abbreviation(original_source)
                del self.abbrev_dict[original_source]
            self.editing_item_id = None
        
        self.abbrev_dict[source] = {
            'replacement': replacement,
            'ignored': False,
            'tag': self.current_tag,
            'original_encrypted': original_encrypted_to_preserve
        }
        self.save_abbreviations()
        self.apply_abbreviations()
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

        category_data = self.category_manager.get_category(data['tag'])
        if category_data and category_data.get("is_encrypted", False):
            if not self.encryption_key:
                return
            elif data['replacement'].startswith("[DECRYPTION FAILED"):
                return
            elif data['replacement'].startswith("[ENCRYPTED - LOCKED]"):
                return

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
        data = self.abbrev_dict[source]

        category_data = self.category_manager.get_category(data['tag'])
        if category_data and category_data.get("is_encrypted", False):
            if not self.encryption_key:
                return

        if source in self.abbrev_dict:
            if not self.abbrev_dict[source].get('ignored', False) and self.abbrev_dict[source].get('tag') == self.current_tag:
                self.text_expander.remove_abbreviation(source)
            del self.abbrev_dict[source]
            self.save_abbreviations()
            self.update_abbreviation_listbox()

    def toggle_ignore_item(self, item_id):
        source = self.tree.item(item_id)['values'][1]
        data = self.abbrev_dict[source]

        category_data = self.category_manager.get_category(data['tag'])
        if category_data and category_data.get("is_encrypted", False):
            if not self.encryption_key:
                return

        if source in self.abbrev_dict:
            self.abbrev_dict[source]['ignored'] = not self.abbrev_dict[source].get('ignored', False)
            self.save_abbreviations()
            self.apply_abbreviations()
            self.update_abbreviation_listbox()

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

    def on_close(self):
        self.text_expander.stop_listening()
        self.destroy()

    def minimize_to_tray(self):
        """Minimize to tray"""
        self.withdraw()
        self.tray_icon.create_tray_icon()

    def Show_tray(self):
        """Minimize to tray"""
        self.tray_icon.create_tray_icon()

    def hide_main_window(self):
        """Hide the main window"""
        self.withdraw()

    def show_main_window(self, icon=None, item=None):
        """Show the main window and bring it to front"""
        self.deiconify()
        self.lift()
        self.focus_force()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        if self.tray_icon:
            self.tray_icon.destroy_tray_icon()

    def quit_application(self, icon=None, item=None):
        """Quit the application"""
        self.text_expander.stop_listening()
        if self.tray_icon:
            self.tray_icon.destroy_tray_icon()
        self.quit()