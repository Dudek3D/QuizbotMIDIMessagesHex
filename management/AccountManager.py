import json
import hashlib
import os
from cryptography.fernet import Fernet

# === Costanti di configurazione ===
DEFAULT_USER_TOKENS = 10
DEFAULT_ACCOUNT_STATUS = True
ACCOUNTS_FILE_PATH = 'management/accounts.json'

class AccountManager:
    def __init__(self, filepath=ACCOUNTS_FILE_PATH):
        self.filepath = filepath
        self._load_data()

    def _load_data(self):
        if not os.path.exists(self.filepath):
            self.data = {
                "users": [],
                "accounts": {},
                "activation keys": {}
            }
            self._save_data()
        else:
            with open(self.filepath, 'r') as f:
                self.data = json.load(f)

    def _save_data(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.data, f, indent=2)

    def _hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def create_account(self, username, password, email, activation_key, email_key):
        hashed_activation_key = self._hash_password(activation_key)
        if hashed_activation_key not in self.data["activation keys"]:
            return False, "Chiave di attivazione non valida."
        elif not self.data["activation keys"][hashed_activation_key]:
            return False, "Chiave di attivazione già usata."

        if username in self.data["users"]:
            return False, "Nome utente già esistente."

        fernet = Fernet(email_key.encode())
        if email_key is None:
            raise Exception("Chiave di cifratura mancante. Assicurati che ENCRYPTION_KEY sia impostata.")
        encrypted_email = fernet.encrypt(email.encode()).decode()

        hashed_password = self._hash_password(password)
        self.data["users"].append(username)
        self.data["accounts"][username] = [
            hashed_password,
            encrypted_email,
            DEFAULT_ACCOUNT_STATUS,
            DEFAULT_USER_TOKENS
        ]
        self.data["activation keys"][hashed_activation_key] = False

        self._save_data()
        return True, "Account creato con successo."

    def verify_login(self, username, password):
        if username not in self.data["users"]:
            return False, f"{username} non trovato"
        hashed_password = self._hash_password(password)
        return self.data["accounts"][username][0] == hashed_password, f"tentativo di login di {username}"

    def is_account_active(self, username):
        return self.data["accounts"].get(username, [None, None, False])[2], f"richiesta di stato per {username}"

    def get_user_info(self, username):
        return self.data["accounts"].get(username), f"richiesta di info per {username}"

    def update_user_tokens(self, username, new_token_count):
        if username not in self.data["accounts"]:
            return False, f"Utente '{username}' non trovato."
        self.data["accounts"][username][3] = new_token_count
        self._save_data()
        return True, f"Token aggiornati per '{username}' a {new_token_count}."

    def activate_key(self, key, activated=True):
        hashed_key = self._hash_password(key)
        self.data["activation keys"][hashed_key] = activated
        self._save_data()
        return True, f"Chiave '{hashed_key}' attivata"
