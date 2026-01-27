import socket
import json
import uuid
from discovery import discover
from security import load_key, encrypt

TCP_PORT = 5000

def get_mac():
    mac = uuid.getnode()
    return ':'.join(f'{(mac >> ele) & 0xff:02x}' for ele in range(40, -1, -8))

class RemoteCLI:
    def __init__(self):
        self.devices = []
        self.sock = None
        self.fernet = load_key()

    def discover(self):
        print("🔍 Recherche d'agents...")
        self.devices = discover()
        if not self.devices:
            print("❌ Aucun agent trouvé")
            return

        for i, d in enumerate(self.devices):
            print(f"[{i}] {d['name']} ({d['ip']})")

    def connect(self, idx):
        try:
            device = self.devices[idx]
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((device["ip"], device["port"]))

            hello = {"mac": get_mac()}
            self.sock.send(encrypt(self.fernet, json.dumps(hello).encode()))
            self.sock.recv(4096)

            print(f"✅ Connecté à {device['name']}")
        except Exception as e:
            print("❌ Connexion échouée :", e)
            self.sock = None

    def send(self, cmd):
        if not self.sock:
            print("⚠️ Non connecté")
            return
        self.sock.send(encrypt(self.fernet, json.dumps(cmd).encode()))

    def loop(self):
        print("💡 Tape 'help' pour la liste des commandes")

        while True:
            try:
                command = input("remote> ").strip()
                if not command:
                    continue

                parts = command.split(" ", 1)

                if parts[0] == "help":
                    print("""
list                 → rechercher les agents
connect <id>         → se connecter
type <texte>         → écrire du texte
move <x> <y>         → déplacer la souris
click                → clic gauche
exit                 → quitter
""")

                elif parts[0] == "list":
                    self.discover()

                elif parts[0] == "connect":
                    self.connect(int(parts[1]))

                elif parts[0] == "type":
                    self.send({
                        "action": "type",
                        "text": parts[1]
                    })

                elif parts[0] == "move":
                    x, y = map(int, parts[1].split())
                    self.send({
                        "action": "move",
                        "x": x,
                        "y": y
                    })

                elif parts[0] == "click":
                    self.send({"action": "click"})

                elif parts[0] == "exit":
                    print("👋 Déconnexion")
                    if self.sock:
                        self.sock.close()
                    break

                else:
                    print("❓ Commande inconnue")

            except Exception as e:
                print("⚠️ Erreur :", e)

if __name__ == "__main__":
    cli = RemoteCLI()
    cli.discover()
    cli.loop()
