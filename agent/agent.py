import socket
import json
import threading
from discovery import discovery_listener
from control import handle_command

TCP_PORT = 5000

from security import load_or_create_key, decrypt, encrypt, is_trusted, trust_device

fernet = load_or_create_key()

def tcp_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", TCP_PORT))
    sock.listen(1)

    print("🔐 Serveur sécurisé prêt")

    while True:
        conn, addr = sock.accept()
        print("Connexion entrante", addr)

        try:
            hello = decrypt(fernet, conn.recv(4096))
            hello = json.loads(hello.decode())

            client_mac = hello.get("mac")

            if not is_trusted(client_mac):
                print(f"⚠️ Appareil non approuvé : {client_mac}")
                trust_device(client_mac)
                print("✅ Appareil approuvé")

            conn.send(encrypt(fernet, b"OK"))

            while True:
                data = conn.recv(4096)
                if not data:
                    break

                command = json.loads(decrypt(fernet, data).decode())
                handle_command(command)

        except Exception as e:
            print("❌ Connexion refusée :", e)

        conn.close()

if __name__ == "__main__":
    threading.Thread(target=discovery_listener, daemon=True).start()
    threading.Thread(target=tcp_server, daemon=True).start()

    print("Agent actif en arrière-plan")
    while True:
        pass