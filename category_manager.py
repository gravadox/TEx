import json
import os
from typing import Dict, List, Optional

class CategoryManager:
    def __init__(self, categories_file="categories.json"):
        self.categories_file = categories_file
        self.categories = {}
        self.load_categories()
    
    def load_categories(self):
        """Load categories from JSON file"""
        if os.path.exists(self.categories_file):
            try:
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    self.categories = json.load(f)
                for cat_id, cat_data in self.categories.items():
                    if "deletable" not in cat_data:
                        cat_data["deletable"] = True
                    if "is_encrypted" not in cat_data:
                        cat_data["is_encrypted"] = False
                    if "salt" in cat_data:
                        del cat_data["salt"]
            except (json.JSONDecodeError, IOError):
                self.categories = self.get_default_categories()
        else:
            self.categories = self.get_default_categories()
            self.save_categories()
    
    def get_default_categories(self) -> Dict:
        """Get default categories"""
        
        return {
            "emoji": {
                "name": "Emoji",
                "icon": "😀",
                "description": "Emoji shortcuts and emoticons",
                "color": "#FFD700",
                "deletable": True,
                "is_encrypted": False 
            },
            "sticker": {
                "name": "Sticker", 
                "icon": "🎯",
                "description": "Stickers and reaction images",
                "color": "#FF6B6B",
                "deletable": True,
                "is_encrypted": False
            },
            "text": {
                "name": "Text",
                "icon": "📝", 
                "description": "Text snippets and templates",
                "color": "#4ECDC4",
                "deletable": True,
                "is_encrypted": False
            },
            "link": {
                "name": "Link",
                "icon": "🔗",
                "description": "URLs and web links", 
                "color": "#45B7D1",
                "deletable": True,
                "is_encrypted": False
            },
            "passwords": { 
                "name": "Passwords",
                "icon": "🔑",
                "description": "Securely stored passwords and sensitive data",
                "color": "#FF4500",
                "deletable": True, 
                "is_encrypted": True 
            }
        }
    
    def save_categories(self):
        """Save categories to JSON file"""
        try:
            with open(self.categories_file, 'w', encoding='utf-8') as f:
                json.dump(self.categories, f, ensure_ascii=False, indent=4)
            return True
        except IOError as e:
            print(f"Failed to save categories: {e}")
            return False
    
    def add_category(self, category_id: str, name: str, icon: str = "📁", 
                    description: str = "", color: str = "#808080", is_encrypted: bool = False) -> bool:
        """Add a new category"""
        if category_id in self.categories:
            return False
        
        self.categories[category_id] = {
            "name": name,
            "icon": icon,
            "description": description,
            "color": color,
            "deletable": True, 
            "is_encrypted": is_encrypted
        }
        return self.save_categories()
    
    def edit_category(self, category_id: str, name: str = None, icon: str = None,
                     description: str = None, color: str = None, is_encrypted: bool = None) -> bool:
        """Edit an existing category"""
        if category_id not in self.categories:
            return False
        
        if name is not None:
            self.categories[category_id]["name"] = name
        if icon is not None:
            self.categories[category_id]["icon"] = icon
        if description is not None:
            self.categories[category_id]["description"] = description
        if color is not None:
            self.categories[category_id]["color"] = color
        if is_encrypted is not None:
            self.categories[category_id]["is_encrypted"] = is_encrypted
        
        return self.save_categories()
    
    def delete_category(self, category_id: str) -> bool:
        """Delete a category if it's deletable"""
        if category_id not in self.categories:
            return False
        
        if not self.categories[category_id].get("deletable", True):
            return False
        
        del self.categories[category_id]
        return self.save_categories()
    
    def get_category(self, category_id: str) -> Optional[Dict]:
        """Get a specific category"""
        return self.categories.get(category_id)
    
    def get_all_categories(self) -> Dict:
        """Get all categories"""
        return self.categories.copy()
    
    def get_category_list(self) -> List[str]:
        """Get list of category IDs"""
        return list(self.categories.keys())
    
    def category_exists(self, category_id: str) -> bool:
        """Check if category exists"""
        return category_id in self.categories
    
    def validate_category_id(self, category_id: str) -> bool:
        """Validate category ID format"""
        if not category_id or len(category_id) < 2:
            return False
        
        return category_id.replace('_', '').isalnum()
