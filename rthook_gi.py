import sys
import os
import glob

# gi (PyGObject/GTK) ships as a system library on Linux.
# Add system site-packages so PyInstaller can find it without bundling GTK.
for pattern in ['/usr/lib/python3*/site-packages', '/usr/lib/python3/dist-packages']:
    for path in sorted(glob.glob(pattern), reverse=True):
        if os.path.isdir(os.path.join(path, 'gi')) and path not in sys.path:
            sys.path.insert(0, path)
            break
    else:
        continue
    break
