### <img alt="Icon" width="21" style="vertical-align: middle;" src="https://raw.githubusercontent.com/gravadox/TEx/refs/heads/main/icon.png"> TEx

simple text expander ( keyboard abbreviation application) using python.

clone and install dependencies </br>

**run:**

```bash

$  pip  install  customtkinter  pystray  pynput  cryptography  keyring  psutil  notify-py

```

  

**then run:**

```bash

$  python  main.py

```

  

pay attention to the tray when you close the app.

  

the expanding functionality is totaly achieved by the pynput library:

```bash

TEx/
└──  Expander/
     └──  text_expander.py

```
check: [text_expander.py](https://github.com/gravadox/TEx/blob/main/Expander/Text_expander.py) file

<img src="https://github.com/gravadox/TEx/blob/main/screenshots/image.png?raw=true">

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
