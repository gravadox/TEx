import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, colorchooser
import re

class CategoryDialog:
    def __init__(self, parent, category_manager, mode="add", category_id=None):

        ctk.set_appearance_mode("Dark") 
        
        self.parent = parent
        self.category_manager = category_manager
        self.mode = mode  
        self.category_id = category_id
        self.result = None
        
        self.setup_dialog()
        
    def setup_dialog(self):
        """Setup the category dialog window"""
        self.dialog = ctk.CTkToplevel(self.parent)
        
        self.dialog.title("Add Category" if self.mode == "add" else "Edit Category")
        self.dialog.geometry("350x637") 
        self.dialog.configure(fg_color="#151515")
        
        self.dialog.transient(self.parent)
        
        self.dialog.update_idletasks()
        self.dialog.deiconify()  # Ensure window is visible
        
        # Try to set grab with error handling for Wayland compatibility
        try:
            self.dialog.after(10, self._safe_grab_set)  # Delay grab slightly
        except Exception as e:
            print(f"Warning: Could not set window grab: {e}")
        
        x = (self.dialog.winfo_screenwidth() // 2) - (350 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (637 // 2) 
        self.dialog.geometry(f"350x637+{x}+{y}")
        
        self.create_widgets()
        
        if self.mode == "edit" and self.category_id:
            self.load_category_data()
    
    def _safe_grab_set(self):
        """Safely set window grab with error handling for Wayland"""
        try:
            if self.dialog.winfo_viewable():
                self.dialog.grab_set()
                self.dialog.focus_set()
        except Exception as e:
            print(f"Warning: Could not set window grab: {e}")
            # On Wayland, we can still focus the window even if grab fails
            try:
                self.dialog.focus_set()
                self.dialog.lift()
            except Exception:
                pass
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ctk.CTkFrame(self.dialog, fg_color="#151515")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title = ctk.CTkLabel(main_frame, text="Add New Category" if self.mode == "add" else "Edit Category",
                            font=ctk.CTkFont(size=20, weight="bold"), text_color="white")
        title.pack(pady=(0, 20))
        
        ctk.CTkLabel(main_frame, text="Category Name: *", font=ctk.CTkFont(size=14), text_color="white").pack(anchor="w", pady=(0, 5))
        self.name_entry = ctk.CTkEntry(main_frame, placeholder_text="e.g., My Custom Category", width=300,
                                      fg_color="transparent", border_color="white", text_color="white")
        self.name_entry.pack(pady=(0, 15))
        
        icon_frame = ctk.CTkFrame(main_frame, fg_color="#151515")
        icon_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(icon_frame, text="Icon: (optional)", font=ctk.CTkFont(size=14), text_color="white").pack(anchor="w", pady=5)
        
        icon_input_frame = ctk.CTkFrame(icon_frame, fg_color="#151515")
        icon_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.icon_entry = ctk.CTkEntry(icon_input_frame, placeholder_text="📁", width=60, font=ctk.CTkFont(size=20),
                                      fg_color="transparent", border_color="white", text_color="white")
        self.icon_entry.pack(side="left", padx=(0, 10))
        
        common_icons = ["📁", "⭐", "🎨", "🏠", "🎵", "📧", "🔧", "🎮", "📚", "🔑"]
        icon_buttons_frame = ctk.CTkFrame(icon_input_frame, fg_color="#151515")
        icon_buttons_frame.pack(side="left", fill="x", expand=True)
        
        for i, icon in enumerate(common_icons):
            btn = ctk.CTkButton(icon_buttons_frame, text=icon, width=25, height=25,
                               fg_color="white", text_color="black", hover_color="#E8E8E8",
                               command=lambda ic=icon: self.set_icon(ic))
            btn.grid(row=i//5, column=i%5, padx=1, pady=1)
        
        ctk.CTkLabel(main_frame, text="Description: (optional)", font=ctk.CTkFont(size=14), text_color="white").pack(anchor="w", pady=(15, 5))
        self.description_entry = ctk.CTkTextbox(main_frame, height=60, width=300,
                                               fg_color="transparent", border_color="white", text_color="white")
        self.description_entry.pack(pady=(0, 15))
        
        color_frame = ctk.CTkFrame(main_frame, fg_color="#151515")
        color_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(color_frame, text="Color:", font=ctk.CTkFont(size=14), text_color="white").pack(anchor="w", pady=5)
        
        color_input_frame = ctk.CTkFrame(color_frame, fg_color="#151515")
        color_input_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.color_entry = ctk.CTkEntry(color_input_frame, placeholder_text="#808080", width=80,
                                       fg_color="transparent", border_color="white", text_color="white")
        self.color_entry.pack(side="left", padx=(0, 10))
        
        self.color_preview = ctk.CTkFrame(color_input_frame, width=30, height=30, fg_color="#808080")
        self.color_preview.pack(side="left", padx=(0, 10))
        self.color_preview.pack_propagate(False) 
        
        color_btn = ctk.CTkButton(color_input_frame, text="Choose", width=80,
                                 fg_color="white", text_color="black", hover_color="#E8E8E8",
                                 command=self.choose_color)
        color_btn.pack(side="left")
        
        self.color_entry.bind("<KeyRelease>", self.update_color_preview)

        self.encrypted_var = ctk.BooleanVar(value=False)
        if self.mode == "add":
            self.encrypted_checkbox = ctk.CTkCheckBox(main_frame, text="Encrypted Category",
                                                      variable=self.encrypted_var,
                                                      fg_color="white", text_color="white",
                                                      hover_color="#E8E8E8",
                                                      checkbox_width=20, checkbox_height=20)
            self.encrypted_checkbox.pack(anchor="w", pady=(10, 20))
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="#151515")
        button_frame.pack(fill="x", pady=(20, 0))
        
        cancel_btn = ctk.CTkButton(button_frame, text="Cancel", width=100,
                                  fg_color="#151515", hover_color="#151515", text_color="white", border_color="white",border_width=1,
                                  command=self.cancel)
        cancel_btn.pack(side="right", padx=(10, 0))
        
        save_btn = ctk.CTkButton(button_frame, text="Save", width=100,
                                fg_color="white", text_color="black", hover_color="#E8E8E8",
                                command=self.save)
        save_btn.pack(side="right")
    
    def set_icon(self, icon):
        """Set the icon in the entry"""
        self.icon_entry.delete(0, tk.END)
        self.icon_entry.insert(0, icon)
    
    def choose_color(self):
        """Open color chooser dialog"""
        try:
            color = colorchooser.askcolor(title="Choose Category Color")
            if color and color[1]:  
                self.color_entry.delete(0, tk.END)
                self.color_entry.insert(0, color[1])
                self.update_color_preview()
        except Exception as e:
            print(f"Color chooser error: {e}")
            messagebox.showerror("Error", "Failed to open color chooser")
    
    def update_color_preview(self, event=None):
        """Update color preview"""
        color = self.color_entry.get().strip()
        if re.match(r'^#[0-9A-Fa-f]{6}$', color):
            try:
                self.color_preview.configure(fg_color=color)
            except Exception as e:
                print(f"Color preview error: {e}")
                self.color_preview.configure(fg_color="#808080")
        else:
            self.color_preview.configure(fg_color="#808080")
    
    def load_category_data(self):
        """Load existing category data for editing"""
        category = self.category_manager.get_category(self.category_id)
        if category:
            self.name_entry.insert(0, category.get("name", ""))
            self.icon_entry.insert(0, category.get("icon", "📁"))
            self.description_entry.insert("1.0", category.get("description", ""))
            self.color_entry.insert(0, category.get("color", "#808080"))
            self.update_color_preview()
            self.encrypted_var.set(category.get("is_encrypted", False))
            if not category.get("deletable", True):
                self.encrypted_checkbox.configure(state="disabled")
    
    def validate_inputs(self):
        """Validate all inputs"""
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Category name is required!")
            return False
                
        color = self.color_entry.get().strip()
        if color and not re.match(r'^#[0-9A-Fa-f]{6}$', color):
            messagebox.showerror("Error", "Invalid color format! Use #RRGGBB format or leave empty for default.")
            return False
        
        return True
    
    def save(self):
        """Save the category"""
        if not self.validate_inputs():
            return
        
        name = self.name_entry.get().strip()
        icon = self.icon_entry.get().strip() or "📁"  
        description = self.description_entry.get("1.0", tk.END).strip()
        color = self.color_entry.get().strip() or "#808080"  
        is_encrypted = self.encrypted_var.get() 
        
        if self.mode == "add":
            category_id = self.generate_category_id(name)
            success = self.category_manager.add_category(category_id, name, icon, description, color, is_encrypted)
            if success:
                self.result = category_id
                messagebox.showinfo("Success", "Category added successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add category!")
        else:
            success = self.category_manager.edit_category(self.category_id, name, icon, description, color, is_encrypted)
            if success:
                self.result = self.category_id
                messagebox.showinfo("Success", "Category updated successfully!")
                self.dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to update category!")
    
    def generate_category_id(self, name):
        """Generate a unique category ID from the name"""
        base_id = re.sub(r'[^a-zA-Z0-9_]', '', name.lower().replace(' ', '_'))
        
        if not base_id or not base_id[0].isalpha():
            base_id = 'category_' + base_id
        
        category_id = base_id
        counter = 1
        while self.category_manager.category_exists(category_id):
            category_id = f"{base_id}_{counter}"
            counter += 1
        
        return category_id
    
    def cancel(self):
        """Cancel the dialog"""
        self.dialog.destroy()

class CategoryManagerDialog:
    def __init__(self, parent, category_manager, app):
        ctk.set_appearance_mode("Dark") 
        
        self.parent = parent
        self.category_manager = category_manager
        self.app = app
        self.setup_dialog()
    
    def setup_dialog(self):
        """Setup the category manager dialog"""
        self.dialog = ctk.CTkToplevel(self.parent)

        
        self.dialog.title("Manage Categories")
        self.dialog.geometry("411x560")
        self.dialog.configure(fg_color="#151515")
        
        self.dialog.transient(self.parent)
        
        self.dialog.update_idletasks()
        self.dialog.deiconify()  # Ensure window is visible
        
        # Try to set grab with error handling for Wayland compatibility
        try:
            self.dialog.after(10, self._safe_grab_set)  # Delay grab slightly
        except Exception as e:
            print(f"Warning: Could not set window grab: {e}")
        
        x = (self.dialog.winfo_screenwidth() // 2) - (411 // 2) 
        y = (self.dialog.winfo_screenheight() // 2) - (560 // 2) 
        self.dialog.geometry(f"411x560+{x}+{y}")
        
        self.create_widgets()
        self.refresh_list()
    
    def _safe_grab_set(self):
        """Safely set window grab with error handling for Wayland"""
        try:
            if self.dialog.winfo_viewable():
                self.dialog.grab_set()
                self.dialog.focus_set()
        except Exception as e:
            print(f"Warning: Could not set window grab: {e}")
            # On Wayland, we can still focus the window even if grab fails
            try:
                self.dialog.focus_set()
                self.dialog.lift()
            except Exception:
                pass
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ctk.CTkFrame(self.dialog, fg_color="#151515")
        main_frame.pack(fill="both", expand=True, padx=0 )
        
        add_btn = ctk.CTkButton(main_frame, text="+ Add Category", 
                               fg_color="white", text_color="black", hover_color="#b5b5b5",
                               command=self.add_category)
        add_btn.pack(fill="x", padx=20, pady=10)
        
        self.categories_frame = ctk.CTkScrollableFrame(main_frame, fg_color="#151515")
        self.categories_frame.pack(fill="both", expand=True, pady=(10, 0))
        
    
    def refresh_list(self):
        """Refresh the categories list"""
        for widget in self.categories_frame.winfo_children():
            widget.destroy()
        
        categories = self.category_manager.get_all_categories()
        
        for category_id, category_data in categories.items():
            self.create_category_item(category_id, category_data)
    
    def create_category_item(self, category_id, category_data):
        """Create a category item widget"""
        item_frame = ctk.CTkFrame(self.categories_frame, fg_color="#202020")
        item_frame.pack(fill="x", pady=10, padx=10)
        
        info_frame = ctk.CTkFrame(item_frame, fg_color="#202020")
        info_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        header_frame = ctk.CTkFrame(info_frame, fg_color="#202020")
        header_frame.pack(fill="x")
        
        icon_label = ctk.CTkLabel(header_frame, text=category_data.get("icon", "📁"), 
                                 font=ctk.CTkFont(size=24), text_color="white")
        icon_label.pack(side="left", padx=10, pady=10)
        
        name_label = ctk.CTkLabel(header_frame, text=category_data.get("name", category_id),
                                 font=ctk.CTkFont(size=16, weight="bold"), text_color="white")
        name_label.pack(side="left",padx=10, pady=10)

        if category_data.get("is_encrypted", False):
            encrypted_label = ctk.CTkLabel(header_frame, text="🔒", font=ctk.CTkFont(size=16), text_color="white")
            encrypted_label.pack(side="left", padx=(0, 5), pady=10)
        
        id_label = ctk.CTkLabel(info_frame, text=f"ID: {category_id}", 
                               font=ctk.CTkFont(size=12), text_color="gray")
        id_label.pack(anchor="w", padx=10, pady=1)
        
        if category_data.get("description"):
            desc_label = ctk.CTkLabel(info_frame, text=category_data["description"],
                                     font=ctk.CTkFont(size=12), text_color="gray")
            desc_label.pack(anchor="w", padx=10, pady=1)
        
        button_frame = ctk.CTkFrame(item_frame, fg_color="#202020")
        button_frame.pack(side="right", padx=10, pady=10)
        
        edit_btn = ctk.CTkButton(button_frame, text="Edit", width=60,
                                fg_color="white", text_color="black", hover_color="#E8E8E8",
                                command=lambda: self.edit_category(category_id))
        edit_btn.pack(pady=2)
        
        if category_data.get("deletable", True):
            delete_btn = ctk.CTkButton(button_frame, text="Delete", width=60,
                                      fg_color="#202020", text_color="white", hover_color="#555555",
                                      command=lambda: self.delete_category(category_id))
            delete_btn.pack(pady=4)
    
    def add_category(self):
        """Add a new category"""
        dialog = CategoryDialog(self.dialog, self.category_manager, mode="add")
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.refresh_list()
            self.app.refresh_sidebar()
    
    def edit_category(self, category_id):
        """Edit a category"""
        dialog = CategoryDialog(self.dialog, self.category_manager, mode="edit", category_id=category_id)
        self.dialog.wait_window(dialog.dialog)
        
        if dialog.result:
            self.refresh_list()
            self.app.refresh_sidebar()
    
    def delete_category(self, category_id):
        """Delete a category"""
        category = self.category_manager.get_category(category_id)
        if not category:
            return
        
        abbrev_count = sum(1 for data in self.app.abbrev_dict.values() 
                           if isinstance(data, dict) and data.get('tag') == category_id)
        
        message = f"Are you sure you want to delete the category '{category['name']}'?"
        if abbrev_count > 0:
            message += f"\n\nThis will also delete {abbrev_count} abbreviation(s) in this category."
        
        if messagebox.askyesno("Confirm Delete", message):
            keys_to_delete = [key for key, data in self.app.abbrev_dict.items()
                             if isinstance(data, dict) and data.get('tag') == category_id]
            
            for key in keys_to_delete:
                del self.app.abbrev_dict[key]
            
            if self.category_manager.delete_category(category_id):
                self.app.save_abbreviations()
                self.app.apply_abbreviations()
                
                if self.app.current_tag == category_id:
                    available_categories = self.category_manager.get_category_list()
                    if available_categories:
                        self.app.switch_page(available_categories[0])
                
                self.refresh_list()
                self.app.refresh_sidebar()
                messagebox.showinfo("Success", "Category deleted successfully!")
            else:
                messagebox.showerror("Error", "Failed to delete category!")
