# PRZECHOWUJE I ZARZĄDZA LISTAMI KAMER
# BAZĄ DANYCH JEST PLIK cameras.json

import os
import json

CAMERAS_FILE = os.path.join(os.path.dirname(__file__), "cameras.json")


cameras = []

def _ensure_cameras_structure(data):
    out = []
    for item in data:
        if isinstance(item, dict):
            name = item.get('name') or item.get('Nazwa') or ''
            ip = item.get('ip') or item.get('IP') or item.get('address') or ''
            user = item.get('user') or item.get('login') or item.get('username') or ''
            password = item.get('password', '')
            out.append({'name': name, 'ip': ip, 'user': user, 'password': password})
    return out

def load_cameras():
    """
    Ładuje kamery z pliku i **modyfikuje listę 'cameras' w miejscu**,
    dzięki czemu inne moduły (które zaimportowały 'cameras') zobaczą zmiany.
    """
    global cameras
    try:
        if os.path.isfile(CAMERAS_FILE):
            with open(CAMERAS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            loaded = _ensure_cameras_structure(data)
            # zamiast: cameras = loaded   <- to przebindowuje nazwę
            cameras.clear()
            cameras.extend(loaded)
        else:
            cameras.clear()
    except Exception as e:
        print(f"[camera_storage] Błąd odczytu {CAMERAS_FILE}: {e}")
        cameras.clear()

def save_cameras():
    try:
        with open(CAMERAS_FILE, 'w', encoding='utf-8') as f:
            json.dump(cameras, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[camera_storage] Błąd zapisu {CAMERAS_FILE}: {e}")