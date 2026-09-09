import tkinter as tk
from tkinter import messagebox
import requests
from requests.auth import HTTPDigestAuth
import urllib3
import config
from urllib.parse import quote_plus
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def dodaj_tablice(INPUT_TABLICA, INPUT_WLASCICIEL, WYBRANA_LISTA, LABEL_STATUS):
    """
    Dodaje nową tablicę rej. do białej lub czarnej listy na kamerze.
    Wysyła żądanie HTTP do API Dahua z numerem tablicy i właścicielem.
    """
    tablica = INPUT_TABLICA.get().strip()
    wlasciciel = INPUT_WLASCICIEL.get().strip()

    if not tablica:
        LABEL_STATUS.config(text="Wprowadź numer tablicy!")
        return

    if WYBRANA_LISTA.get() == 1:
        lista = 'TrafficRedList'
    elif WYBRANA_LISTA.get() == 2:
        lista = 'TrafficBlackList'
    else:
        LABEL_STATUS.config(text="Wybierz listę!")
        return

    url = f'https://{config.IP_KAMERY}/cgi-bin/recordUpdater.cgi?action=insert&name={lista}&PlateNumber={tablica}&MasterOfCar={wlasciciel}'

    try:
        response = requests.get(
            url,
            auth=HTTPDigestAuth(config.USERNAME, config.PASSWORD),
            timeout=10,
            verify=False
        )
        if response.status_code == 200 and 'RecNo' in response.text:
            LABEL_STATUS.config(text=f"Dodano tablicę {tablica} do {lista}!")
            INPUT_TABLICA.delete(0, tk.END)
            INPUT_WLASCICIEL.delete(0, tk.END)
        else:
            LABEL_STATUS.config(text=f"Błąd: {response.status_code}")
    except requests.exceptions.RequestException as e:
        LABEL_STATUS.config(text=f"Błąd połączenia: {e}")


def pobierz_liste(lista_typ, treeview, label_empty):
    """
    Pobiera listę tablic (allowlist lub blacklist) z kamery.
    Zapisuje także RecNo jako trzecią (ukrytą) wartość w treeview, żeby móc potem usuwać wpisy po recno.
    """
    if not config.IP_KAMERY or not config.USERNAME or not config.PASSWORD:
        messagebox.showerror("Błąd", "Nie wybrano kamery!")
        return

    url = f'https://{config.IP_KAMERY}/cgi-bin/recordFinder.cgi?action=find&name={lista_typ}&count=100'
    try:
        response = requests.get(url, auth=HTTPDigestAuth(config.USERNAME, config.PASSWORD), timeout=10, verify=False)
        if response.status_code == 200:
            # wyczyść treeview
            for item in treeview.get_children():
                treeview.delete(item)

            current_record = {}
            current_index = None
            has_records = False

            for line in response.text.splitlines():
                line = line.strip()
                if not line:
                    continue
                if line.startswith('records['):
                    # nowy/istniejący rekord
                    index = line.split('.')[0]  # e.g. records[0]
                    if index != current_index and current_index is not None:
                        # zakończ poprzedni rekord
                        if 'PlateNumber' in current_record:
                            plate = current_record.get('PlateNumber', 'Brak').strip()
                            owner = current_record.get('MasterOfCar', 'Brak').strip()
                            recno = current_record.get('RecNo', '')  # może być puste
                            # wstawiamy 3 wartości: plate, owner, recno (recno ukryte)
                            treeview.insert('', 'end', values=(plate, owner, recno))
                            has_records = True
                        current_record = {}
                    current_index = index

                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key_part = parts[0].strip()         # e.g. records[0].PlateNumber
                        value = parts[1].strip()
                        key_parts = key_part.split('.')
                        if len(key_parts) > 1:
                            key = key_parts[1]
                            current_record[key] = value
            # ostatni rekord
            if 'PlateNumber' in current_record:
                plate = current_record.get('PlateNumber', 'Brak').strip()
                owner = current_record.get('MasterOfCar', 'Brak').strip()
                recno = current_record.get('RecNo', '')
                treeview.insert('', 'end', values=(plate, owner, recno))
                has_records = True

            if not has_records:
                label_empty.config(text="Lista jest pusta")
            else:
                label_empty.config(text="")
        else:
            messagebox.showerror("Błąd", f"HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Błąd", f"Połączenie: {e}")
# ----------------------------------------

def usun_tablice(lista_typ, treeview, label_status, label_empty):

    
    selected = treeview.selection()
    

    if not selected:
        messagebox.showwarning("Błąd", "Nie zaznaczono pozycji!")
        return

    item = treeview.item(selected[0])
    values = item.get('values', [])

    plate = values[0] if len(values) > 0 else ''
    owner = values[1] if len(values) > 1 else ''
    recno = values[2] if len(values) > 2 else ''

    if not plate and not recno:
        messagebox.showerror("Błąd", "Brak danych rekordu do usunięcia.")
        return

    if messagebox.askyesno("Potwierdzenie", f"Czy na pewno usunąć tablicę {plate}?"):
        if recno:
            url = f'https://{config.IP_KAMERY}/cgi-bin/recordUpdater.cgi?action=remove&name={lista_typ}&recno={recno}'
        else:
            # fallback: usuń po numerze tablicy (upewnij się, że jest poprawnie zakodowane)
            url = f'https://{config.IP_KAMERY}/cgi-bin/recordUpdater.cgi?action=remove&name={lista_typ}&PlateNumber={quote_plus(plate)}'

        try:
            response = requests.get(url, auth=HTTPDigestAuth(config.USERNAME, config.PASSWORD), timeout=10, verify=False)
            
            if response.status_code == 200 and 'OK' in response.text.upper():
                label_status.config(text="Usuwanie powiodło się!")
                pobierz_liste(lista_typ, treeview, label_empty)
            else:
                label_status.config(text=f"Błąd: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            label_status.config(text=f"Błąd połączenia: {e}")
