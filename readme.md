### <img alt="Icon" width="21" style="vertical-align: middle;" src="https://raw.githubusercontent.com/gravadox/TEx/refs/heads/main/icon.png"> TEx

simple text expander ( keyboard abbreviation application) using python.

pay attention to the tray when you close the app.

---

## Installation (Linux)

### One-liner (recommended)

Installs TEx to your system and adds it to your app launcher:

```bash
curl -fsSL https://raw.githubusercontent.com/gravadox/TEx/main/install.sh | bash
```

This downloads the latest binary from GitHub releases, installs it to `~/.local/share/TEx/`, and adds TEx to your app launcher and terminal.

> If `TEx` is not found in terminal after install, add this to your `~/.bashrc` or `~/.zshrc`:
> ```bash
> export PATH="$HOME/.local/bin:$PATH"
> ```

To **uninstall**:
```bash
rm -rf ~/.local/share/TEx && rm -f ~/.local/bin/TEx ~/.local/share/applications/TEx.desktopapplications/TEx.desktop
```

---

### AppImage (no install, works on any distro)

1. Download `TEx-x86_64.AppImage` from the [latest release](https://github.com/gravadox/TEx/releases/latest)
2. Run it:

```bash
chmod +x TEx-x86_64.AppImage
./TEx-x86_64.AppImage
```

Nothing is installed on your system.

---

### Run from source

```bash
git clone https://github.com/gravadox/TEx.git
cd TEx
pip install customtkinter pystray pynput cryptography keyring psutil notify-py
python main.py
```

---

  

the expanding functionality is totaly achieved by the pynput library:

```bash

TEx/
└──  Expander/
     └──  text_expander.py

```
check: [text_expander.py](https://github.com/gravadox/TEx/blob/main/Expander/Text_expander.py) file

<img src="https://github.com/gravadox/TEx/blob/main/screenshots/image.png">

the app comes with 7 default abbreviations, typeof emoji you can find in the abbreviations.json file:

```json

{
"--wink":  {
"replacement":  "😉",
"ignored":  false,
"tag":  "emoji"
},

"--laugh":  {
"replacement":  "😂",
"ignored":  false,
"tag":  "emoji"

},

"--sunglasses":  {
"replacement":  "😎",
"ignored":  false,
"tag":  "emoji"

},

"--cry":  {
"replacement":  "😢",
"ignored":  false,
"tag":  "emoji"
},

"--heart":  {
"replacement":  "❤️",
"ignored":  false,
"tag":  "emoji"
},

"--thumbs_up":  {
"replacement":  "👍",
"ignored":  false,
"tag":  "emoji"
},

"--middle_finger":  {
"replacement":  "🖕",
"ignored":  false,
"tag":  "emoji"
}
}

```

you have the freedom to create categoires and delete them.<br>
you can also create an encrypted category by checking the checkbox for encryption.<br>
you can store passwords and secret data in it although caution is required.<br>
all data stored in an encrypted category is decrypted using keyring token, if that token is lost your data can not be retrieved.<br>
I advice you keep a copy of data you don't want to lose just in case.<br>
I recommend you don't change the app files unless you know what you're doing.

**better CLI based version is planned to be developed**

**note this app is tested on windows and linux on wayland**

**feedback is appreciated**
