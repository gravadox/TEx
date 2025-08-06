import os
import base64
from user_files.icon import ICON

def setup_icon():
    ico_path = os.path.abspath("icon.ico")
    if os.path.exists(ico_path):
        return

    try:
        with open(ico_path, "wb") as f:
            f.write(base64.b64decode(ICON))
        print("icon.ico created from embedded data.")
    except Exception as e:
        print(f"Failed to write icon.ico: {e}")
