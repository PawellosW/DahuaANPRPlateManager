import tkinter as tk
from tkinter import ttk, messagebox
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import requests
from requests.auth import HTTPDigestAuth


from camera_gui import (
    add_camera, edit_camera, delete_camera,
    select_camera, change_camera, refresh_tree, toggle_buttons, on_select
)
from gui_components import create_selection_frame, create_management_frame
from list_management import dodaj_tablice, pobierz_liste, usun_tablice

from camera_storage import load_cameras, save_cameras, cameras
import config


# Globalne referencje do widgetów GUI (ustawiane przy starcie)
INPUT_TABLICA = None
INPUT_WLASCICIEL = None
WYBRANA_LISTA = None
LABEL_STATUS = None
TREEVIEW_ALLOW = None
LABEL_EMPTY_ALLOW = None
TREEVIEW_BLACK = None
LABEL_EMPTY_BLACK = None






# --- Główne okno aplikacji ---
root = tk.Tk()
root.title("Wybór kamery")
root.geometry("400x500")
root.resizable(False, False)

#przycisk "Zmień kamerę"
def change_camera_main():
    """Powrót do okna wyboru kamery"""
    global frame_selection, frame_management
    frame_management.pack_forget()
    frame_selection.pack(fill='both', expand=True)
    root.title("Wybór kamery")


frame_management, input_tablica, input_wlasciciel, wybrana_lista, label_status, treeview_allow, label_empty_allow, treeview_black, label_empty_black = create_management_frame(
    root,
    lambda: dodaj_tablice(INPUT_TABLICA, INPUT_WLASCICIEL, WYBRANA_LISTA, LABEL_STATUS),
    lambda lista, tree, lbl: pobierz_liste(lista, tree, lbl),
    change_camera_main
)

# Przypisanie globali (referencje do widgetów)
INPUT_TABLICA = input_tablica
INPUT_WLASCICIEL = input_wlasciciel
WYBRANA_LISTA = wybrana_lista
LABEL_STATUS = label_status
TREEVIEW_ALLOW = treeview_allow
LABEL_EMPTY_ALLOW = label_empty_allow
TREEVIEW_BLACK = treeview_black
LABEL_EMPTY_BLACK = label_empty_black


# Callback wywoływany po poprawnym zalogowaniu w oknie hasła
def on_camera_selected(ip, user, password, cam_name):
    import config  # Import całego modułu config
    config.IP_KAMERY = ip
    config.USERNAME = user
    config.PASSWORD = password
    # Odśwież listy w panelu zarządzania
    pobierz_liste('TrafficRedList', TREEVIEW_ALLOW, LABEL_EMPTY_ALLOW)
    pobierz_liste('TrafficBlackList', TREEVIEW_BLACK, LABEL_EMPTY_BLACK)

# Wrapper dla select_camera - wywołuje funkcję w camera_manager z callbackiem on_camera_selected
def select_camera_main(tree, frame_selection_arg, frame_management_arg):
    # Przekierowanie do camera_manager.select_camera z callbackiem
    select_camera(tree, frame_selection_arg, frame_management_arg, root, on_success=on_camera_selected)


# Tworzenie frame_selection (przekazujemy wrapper select_camera_main)
frame_selection, tree, btn_frame, btn_add, btn_edit, btn_delete, btn_select = create_selection_frame(
    root,
    frame_management,
    select_camera_main,
    add_camera,
    edit_camera,
    delete_camera,
    on_select
)

# Pokazujemy wybór kamery na start
frame_selection.pack(fill='both', expand=True)

# Ukryj zarządzanie kamerą na start
frame_management.pack_forget()

# Odśwież tree na start (puste lub z kamer z pliku)
refresh_tree(tree)

# Start aplikacji
root.mainloop()
