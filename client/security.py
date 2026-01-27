from cryptography.fernet import Fernet

def load_key():
    with open("secret.key", "rb") as f:
        return Fernet(f.read())

def encrypt(fernet, data: bytes) -> bytes:
    return fernet.encrypt(data)

def decrypt(fernet, data: bytes) -> bytes:
    return fernet.decrypt(data)
