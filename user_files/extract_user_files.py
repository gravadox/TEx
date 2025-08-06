import os
import json

DEFAULT_CATEGORIES = {
    "emoji": {
        "name": "Emoji",
        "icon": "😀",
        "description": "Emoji shortcuts and emoticons",
        "color": "#FFE999",
        "deletable": True,
        "is_encrypted": False
    },
    "sticker": {
        "name": "Sticker",
        "icon": "🎯",
        "description": "Stickers and reaction images",
        "color": "#FF9E9E",
        "deletable": True,
        "is_encrypted": False
    },
    "text": {
        "name": "Text",
        "icon": "📝",
        "description": "Text snippets and templates",
        "color": "#9AEEFF",
        "deletable": True,
        "is_encrypted": False
    },
    "link": {
        "name": "Link",
        "icon": "🔗",
        "description": "URLs and web links",
        "color": "#9ACBFF",
        "deletable": True,
        "is_encrypted": False
    },
    "passwords": {
        "name": "Passwords",
        "icon": "🔑",
        "description": "Securely stored passwords and sensitive data",
        "color": "#212121",
        "deletable": True,
        "is_encrypted": True
    }
}
DEFAULT_EXPANSIONS = {
    "--sunglasses": {
        "replacement": "😎",
        "ignored": False,
        "tag": "emoji"
    },
    "--cry": {
        "replacement": "😢",
        "ignored": False,
        "tag": "emoji"
    },
    "--heart": {
        "replacement": "❤️",
        "ignored": False,
        "tag": "emoji"
    },
    "--thumbs_up": {
        "replacement": "👍",
        "ignored": False,
        "tag": "emoji"
    },
    "--middle_finger": {
        "replacement": "🖕",
        "ignored": False,
        "tag": "emoji"
    },
    "--wink": {
        "replacement": "😉",
        "ignored": False,
        "tag": "emoji"
    },
    "--laugh": {
        "replacement": "😂",
        "ignored": False,
        "tag": "emoji",
    }
}

def setup_user_folder():
    # Use current working directory (same as your icon code)
    user_dir = os.path.abspath(os.path.join(os.getcwd(), "user"))

    if not os.path.exists(user_dir):
        os.makedirs(user_dir)
        print(f"Created folder: {user_dir}")

    def ensure_json_file(filename, default_content=None):
        path = os.path.join(user_dir, filename)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                if default_content is None:
                    json.dump({}, f, indent=4)
                else:
                    json.dump(default_content, f, indent=4)
            print(f"Created file: {path}")
        else:
            print(f"File already exists: {path}")

    ensure_json_file("Expansions.json", DEFAULT_EXPANSIONS)
    ensure_json_file("categories.json", DEFAULT_CATEGORIES)
