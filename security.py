from cryptography.fernet import Fernet
import os

KEY_FILE = os.path.join(os.path.dirname(__file__), "secret.key")


def generate_key():

    if not os.path.isfile(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as key_file:
            key_file.write(key)




def load_key():
    """
    Ładuje klucz szyfrowania z pliku.
    """
    with open(KEY_FILE, "rb") as key_file:
        return key_file.read()


def encrypt_password(password: str) -> str:
    """
    Szyfruje hasło i zwraca zakodowany tekst.
    """
    generate_key()  # upewniamy się, że klucz istnieje
    key = load_key()
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()


def decrypt_password(token: str) -> str:
    """
    Odszyfrowuje hasło z zakodowanego tekstu.
    """
    key = load_key()
    f = Fernet(key)
    return f.decrypt(token.encode()).decode()
