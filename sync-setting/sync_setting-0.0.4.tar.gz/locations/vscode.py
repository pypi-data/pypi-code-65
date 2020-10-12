import os

from .utils import home, platform, Platform


settings_path, shortcuts_path = None, None

if platform == Platform.windows:
    settings_path = os.path.join(
        home, 'AppData', 'Roaming', 'Code', 'User', 'settings.json')
    shortcuts_path = os.path.join(
        home, 'AppData', 'Roaming', 'Code', 'User', 'keybindings.json')
elif platform == Platform.linux:
    settings_path = os.path.join(
        home, '.config', 'Code', 'User', 'settings.json')
    shortcuts_path = os.path.join(
        home, '.config', 'Code', 'User', 'keybindins.json')
elif platform == Platform.mac:
    settings_path = os.path.join(
        home, 'Library', 'Application Support', 'Code', 'User', 'settings.json')
    shortcuts_path = os.path.join(
        home, 'Library', 'Application Support', 'Code', 'User', 'keybindings.json')


