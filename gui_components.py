import tkinter as tk
from tkinter import ttk
from list_management import usun_tablice
import config

# Zmienne globalne dla widgetów zarządzania (używane w main)
input_tablica = None
input_wlasciciel = None
wybrana_lista = None
label_status = None
treeview_allow = None
label_empty_allow = None
treeview_black = None
label_empty_black = None

def create_selection_frame(root, frame_management, select_cmd, add_cmd, edit_cmd, delete_cmd, on_select_func):
    frame_selection = ttk.Frame(root)
    
    tk.Label(frame_selection, text="Lista kamer:", font=('Arial', 12, 'bold')).pack(pady=10)

    tree = ttk.Treeview(frame_selection, columns=('Nazwa', 'IP'), show='headings', height=10)
    tree.heading('Nazwa', text='Nazwa')
    tree.heading('IP', text='IP')
    tree.column('Nazwa', width=150, stretch=False)
    tree.column('IP', width=200, stretch=False)
    tree.pack(pady=5, fill='both', expand=True)

    def block_resize(event):
        if tree.identify_region(event.x, event.y) == "separator":
            return "break"  # Zatrzymuje zdarzenie przeciągania paska rozdzielającego
    tree.bind('<Button-1>', block_resize)  # Blokuje kliknięcie na separatorze

    
    # Obsługa zaznaczenia
    tree.bind('<<TreeviewSelect>>', lambda e: on_select_func(e, tree, btn_edit, btn_delete))

    btn_frame = tk.Frame(frame_selection)
    btn_frame.pack(pady=10)

    btn_add = tk.Button(btn_frame, text="Dodaj kamerę",
                        command=lambda: add_cmd(tree, btn_edit, btn_delete))
    btn_add.pack(side='left', padx=5)

    btn_edit = tk.Button(btn_frame, text="Edytuj kamerę",
                         command=lambda: edit_cmd(tree, btn_edit, btn_delete),
                         state='disabled')
    btn_edit.pack(side='left', padx=5)

    btn_delete = tk.Button(btn_frame, text="Usuń kamerę",
                           command=lambda: delete_cmd(tree, btn_edit, btn_delete),
                           state='disabled')
    btn_delete.pack(side='left', padx=5)

    btn_select = tk.Button(btn_frame, text="Wybierz kamerę",
                           command=lambda: select_cmd(tree, frame_selection, frame_management))
    btn_select.pack(side='left', padx=5)

    return frame_selection, tree, btn_frame, btn_add, btn_edit, btn_delete, btn_select

def create_management_frame(root, dodaj_cmd, pobierz_cmd, change_cmd):
    frame_management = ttk.Frame(root)

    # Zakładka 1: Dodawanie tablicy
    notebook = ttk.Notebook(frame_management)
    notebook.pack(fill='both', expand=True)

    tab1 = ttk.Frame(notebook)
    notebook.add(tab1, text='Dodawanie tablicy')

    global input_tablica, input_wlasciciel, wybrana_lista, label_status
    input_tablica = tk.Entry(tab1)
    input_wlasciciel = tk.Entry(tab1)
    wybrana_lista = tk.IntVar(value=1)
    label_status = tk.Label(tab1, text="")

    tk.Label(tab1, text="Numer tablicy:").pack(pady=5)
    input_tablica.pack(pady=5)

    tk.Label(tab1, text="Właściciel:").pack(pady=5)
    input_wlasciciel.pack(pady=5)

    tk.Radiobutton(tab1, text="Biała lista (Allowlist)", variable=wybrana_lista, value=1).pack(anchor='w')
    tk.Radiobutton(tab1, text="Czarna lista (Blacklist)", variable=wybrana_lista, value=2).pack(anchor='w')

    tk.Button(tab1, text="Dodaj", command=dodaj_cmd).pack(pady=10)

    label_status.pack(pady=5)

    # Przycisk zmiany kamery
    tk.Button(tab1, text="Zmień kamerę", command=lambda: change_cmd()).pack(pady=5)

    # Zakładka 2: Wyświetlanie Allowlist
    tab2 = ttk.Frame(notebook)
    notebook.add(tab2, text='Allowlist')

    global treeview_allow, label_empty_allow
    treeview_allow = ttk.Treeview(tab2, columns=('Numer tablicy', 'Właściciel'), show='headings')
    treeview_allow.heading('Numer tablicy', text='Numer tablicy')
    treeview_allow.heading('Właściciel', text='Właściciel')
    treeview_allow.column('Numer tablicy', width=150, stretch=False)
    treeview_allow.column('Właściciel', width=150, stretch=False)
    treeview_allow.pack(pady=5, fill='both', expand=True)

    def block_resize_allow(event):
        if treeview_allow.identify_region(event.x, event.y) == "separator":
            return "break"
    treeview_allow.bind('<Button-1>', block_resize_allow)

    # Binding do aktywacji/deaktywacji przycisku Usuń
    treeview_allow.bind('<<TreeviewSelect>>', lambda event: btn_usun_allow.config(state="normal" if treeview_allow.selection() else "disabled"))

    label_empty_allow = tk.Label(tab2, text="")
    label_empty_allow.pack(pady=5)

    # Ramka na przyciski Odśwież i Usuń
    btn_frame_allow = ttk.Frame(tab2)
    btn_frame_allow.pack(pady=10)
    tk.Button(btn_frame_allow, text="Odśwież", command=lambda: pobierz_cmd('TrafficRedList', treeview_allow, label_empty_allow)).pack(side='left', padx=5)
    btn_usun_allow = tk.Button(
    btn_frame_allow,
    text="Usuń",
    state="disabled",
    command=lambda: usun_tablice('TrafficRedList', treeview_allow, label_status, label_empty_allow)
    )

    btn_usun_allow.pack(side='left', padx=5)

    # Zakładka 3: Wyświetlanie Blacklist
    tab3 = ttk.Frame(notebook)
    notebook.add(tab3, text='Blacklist')

    global treeview_black, label_empty_black
    treeview_black = ttk.Treeview(tab3, columns=('Numer tablicy', 'Właściciel'), show='headings')
    treeview_black.heading('Numer tablicy', text='Numer tablicy')
    treeview_black.heading('Właściciel', text='Właściciel')
    treeview_black.column('Numer tablicy', width=150, stretch=False)
    treeview_black.column('Właściciel', width=150, stretch=False)
    treeview_black.pack(pady=5, fill='both', expand=True)

    def block_resize_black(event):
        if treeview_black.identify_region(event.x, event.y) == "separator":
            return "break"
    treeview_black.bind('<Button-1>', block_resize_black)

    # Binding do aktywacji/deaktywacji przycisku Usuń
    treeview_black.bind('<<TreeviewSelect>>', lambda event: btn_usun_black.config(state="normal" if treeview_black.selection() else "disabled"))

    label_empty_black = tk.Label(tab3, text="")
    label_empty_black.pack(pady=5)

    # Ramka na przyciski Odśwież i Usuń
    btn_frame_black = ttk.Frame(tab3)
    btn_frame_black.pack(pady=10)
    tk.Button(btn_frame_black, text="Odśwież", command=lambda: pobierz_cmd('TrafficBlackList', treeview_black, label_empty_black)).pack(side='left', padx=5)
    btn_usun_black = tk.Button(
    btn_frame_black,
    text="Usuń",
    state="disabled",
    command=lambda: usun_tablice('TrafficBlackList', treeview_black, label_status, label_empty_black)
    )

    btn_usun_black.pack(side='left', padx=5)

    # Zwracamy wszystkie potrzebne widgety
    return (frame_management, input_tablica, input_wlasciciel, wybrana_lista, label_status,
            treeview_allow, label_empty_allow, treeview_black, label_empty_black)


