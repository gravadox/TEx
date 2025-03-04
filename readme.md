![](https://i.imghippo.com/files/wMQo7503Jls.jpg)
### TEx
simple text expander ( keyboard abbreviation application) using python.
clone and install dependencies
**run:**
```$ pip install customtkinter pystray keyboard```

**then run:**
```$ python main.py```

pay attention to the tray when you close the app.

the expanding functionality is totaly by the keyboard library:
```py
self.abbrev_hooks[key] = keyboard.add_abbreviation(key, value, timeout=5)
```

the app comes with 7 default abbreviations, typeof emoji you can find in the abbreviations.json file:
```json
{
    "--wink": {
        "replacement": "😉",
        "ignored": false,
        "tag": "emoji"
    },
    "--laugh": {
        "replacement": "😂",
        "ignored": false,
        "tag": "emoji"
    },
    "--sunglasses": {
        "replacement": "😎",
        "ignored": false,
        "tag": "emoji"
    },
    "--cry": {
        "replacement": "😢",
        "ignored": false,
        "tag": "emoji"
    },
    "--heart": {
        "replacement": "❤️",
        "ignored": false,
        "tag": "emoji"
    },
    "--thumbs_up": {
        "replacement": "👍",
        "ignored": false,
        "tag": "emoji"
    },
    "--middle_finger": {
        "replacement": "🖕",
        "ignored": false,
        "tag": "emoji"
    }
}
```
you can clear the file or remove manually if you want to delete them,
anyways just wanted to say if you are ever serious about using this application pay attention also to the catigories of text you add, make sure you have a unique prefix for every one of them
