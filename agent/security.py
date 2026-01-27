import os
from cryptography.fernet import Fernet
import json

TRUST_FILE = "trusted.json"
KEY_FILE = "secret.key"

def is_trusted(mac):
    with open(TRUST_FILE, "r") as f:
        data = json.load(f)
    return mac in data["devices"]

def trust_device(mac):
    with open(TRUST_FILE, "r") as f:
        data = json.load(f)

    if mac not in data["devices"]:
        data["devices"].append(mac)

    with open(TRUST_FILE, "w") as f:
        json.dump(data, f, indent=2)



def load_or_create_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        print("🔑 Clé de sécurité générée")
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()

    return Fernet(key)
def encrypt(fernet, data: bytes) -> bytes:
    return fernet.encrypt(data)

def decrypt(fernet, data: bytes) -> bytes:
    return fernet.decrypt(data)
