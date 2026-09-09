import tkinter as tk
from tkinter import messagebox
import urllib3
from security import encrypt_password, decrypt_password
from camera_utils import validate_ip, test_connection 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from camera_storage import load_cameras, save_cameras, cameras


def refresh_tree(tree):
    # Oczyszczenie i wstawienie kamer z pamięci
    for item in tree.get_children():
        tree.delete(item)
    for cam in cameras:
        tree.insert('', 'end', values=(cam['name'], cam['ip']))


def toggle_buttons(tree, btn_edit, btn_delete):
    if tree.selection():
        btn_edit.config(state='normal')
        btn_delete.config(state='normal')
    else:
        btn_edit.config(state='disabled')
        btn_delete.config(state='disabled')


def add_camera(tree, btn_edit, btn_delete):
    
    def save():
        name = entry_name.get().strip()
        ip = entry_ip.get().strip()
        user = entry_user.get().strip()
        pw = entry_pw.get().strip()

        if not all([name, ip, user, pw]):
            messagebox.showerror("Błąd", "Wypełnij wszystkie")
            return

        if not validate_ip(ip):
            messagebox.showerror("Błąd", "Niepoprawny format adresu IP! Wprowadź cztery bloki cyfr, oddzielone kropkami.")
            return

       
        cameras.append({'name': name, 'ip': ip, 'user': user, 'password': encrypt_password(pw)})
        save_cameras()
        refresh_tree(tree)
        add_win.destroy()

    add_win = tk.Toplevel()
    add_win.title("Dodaj kamerę")
    add_win.geometry("320x280")
    add_win.resizable(False, False)

    tk.Label(add_win, text="Nazwa kamery:").pack(pady=4)
    entry_name = tk.Entry(add_win)
    entry_name.pack(pady=4, fill='x', padx=10)

    tk.Label(add_win, text="Adres IP:").pack(pady=4)
    entry_ip = tk.Entry(add_win)
    entry_ip.pack(pady=4, fill='x', padx=10)

    tk.Label(add_win, text="Login:").pack(pady=4)
    entry_user = tk.Entry(add_win)
    entry_user.pack(pady=4, fill='x', padx=10)

    
    tk.Label(add_win, text="Hasło:").pack(pady=4)
    entry_pw = tk.Entry(add_win, show="*")
    entry_pw.pack(pady=4, fill='x', padx=10)

    tk.Button(add_win, text="Zapisz", command=save).pack(pady=8)


def edit_camera(tree, btn_edit, btn_delete):
    sel = tree.selection()
    if not sel:
        return

    idx = tree.index(sel[0])
    cam = cameras[idx]

    def save():
        name = entry_name.get().strip()
        ip = entry_ip.get().strip()
        user = entry_user.get().strip()

        if not all([name, ip, user]):
            messagebox.showerror("Błąd", "Wypełnij wszystkie pola!")
            return

        if not validate_ip(ip):
            messagebox.showerror("Błąd", "Niepoprawny format adresu IP!")
            return

        existing_pw = cam.get('password', '')
        cameras[idx] = {'name': name, 'ip': ip, 'user': user, 'password': existing_pw}
        save_cameras()
        refresh_tree(tree)
        edit_win.destroy()

    edit_win = tk.Toplevel()
    edit_win.title("Edytuj kamerę")
    edit_win.geometry("320x220")
    edit_win.resizable(False, False)

    tk.Label(edit_win, text="Nazwa kamery:").pack(pady=4)
    entry_name = tk.Entry(edit_win)
    entry_name.insert(0, cam['name'])
    entry_name.pack(pady=4, fill='x', padx=10)

    tk.Label(edit_win, text="Adres IP:").pack(pady=4)
    entry_ip = tk.Entry(edit_win)
    entry_ip.insert(0, cam['ip'])
    entry_ip.pack(pady=4, fill='x', padx=10)

    tk.Label(edit_win, text="Login:").pack(pady=4)
    entry_user = tk.Entry(edit_win)
    entry_user.insert(0, cam.get('user', ''))
    entry_user.pack(pady=4, fill='x', padx=10)

    tk.Button(edit_win, text="Zapisz", command=save).pack(pady=8)


def delete_camera(tree, btn_edit, btn_delete):
    sel = tree.selection()
    if not sel:
        return

    idx = tree.index(sel[0])
    cam_name = cameras[idx]['name']
    if messagebox.askyesno("Potwierdź", f"Czy na pewno usunąć kamerę '{cam_name}'?"):
        del cameras[idx]
        save_cameras()
        refresh_tree(tree)


def select_camera(tree, frame_selection, frame_management, root, on_success):
    """
    Wywoływane gdy użytkownik klika "Wybierz kamerę".
    Po poprawnym połączeniu wywołujemy on_success(ip, user, password, name).
    """
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Ostrzeżenie", "Zaznacz kamerę z listy!")
        return

    idx = tree.index(sel[0])
    cam = cameras[idx]

    ip = cam['ip']
    pre_user = cam.get('user', '')

    stored_password = cam.get('password', '')
    try:
        pre_password = decrypt_password(stored_password) if stored_password else ''
    except Exception:
        pre_password = ''
        
    
    if pre_user and pre_password:
        ok = test_connection(ip, pre_user, pre_password)
        if ok:
            frame_selection.pack_forget()
            frame_management.pack(fill='both', expand=True)
            root.title(f"Zarządzanie tablicami - {cam['name']}")
            if callable(on_success):
                on_success(ip, pre_user, pre_password, cam['name'])
            return

    pw_win = tk.Toplevel(root)
    pw_win.title(f"Logowanie — {cam['name']}")
    pw_win.geometry("320x170")
    pw_win.transient(root)
    pw_win.grab_set()

    tk.Label(pw_win, text=f"Kamera: {cam['name']}").pack(pady=6)
    tk.Label(pw_win, text="Login:").pack(anchor='w', padx=10)
    entry_user = tk.Entry(pw_win)
    entry_user.insert(0, pre_user)
    entry_user.pack(fill='x', padx=10, pady=2)

    tk.Label(pw_win, text="Hasło:").pack(anchor='w', padx=10)
    entry_pw = tk.Entry(pw_win, show="*")
    entry_pw.insert(0, pre_password)
    entry_pw.pack(fill='x', padx=10, pady=2)

    status_lbl = tk.Label(pw_win, text="")
    status_lbl.pack(pady=6)

    def try_connect():
        user = entry_user.get().strip()
        password = entry_pw.get().strip()
        if not user or not password:
            status_lbl.config(text="Wprowadź login i hasło!")
            return

        status_lbl.config(text="Łączenie...")
        pw_win.update_idletasks()

        ok = test_connection(ip, user, password)
        if ok:
            
            pw_win.destroy()
            frame_selection.pack_forget()
            frame_management.pack(fill='both', expand=True)
            root.title(f"Zarządzanie tablicami - {cam['name']}")
            
            if callable(on_success):
                on_success(ip, user, password, cam['name'])
        else:
            status_lbl.config(text="Błąd logowania / połączenia. Sprawdź dane.")

    tk.Button(pw_win, text="Połącz", command=try_connect).pack(pady=6)
    tk.Button(pw_win, text="Anuluj", command=pw_win.destroy).pack()



    


def change_camera(frame_selection, frame_management, root):
    
    frame_management.pack_forget()
    frame_selection.pack(fill='both', expand=True)
    root.title("Wybór kamery")


def on_select(event, tree, btn_edit, btn_delete):
    toggle_buttons(tree, btn_edit, btn_delete)


# Wczytaj kamery przy imporcie modułu
load_cameras()
