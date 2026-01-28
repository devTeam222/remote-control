import socket
import json
from utils import get_mac, load_config

DISCOVERY_PORT = 37020

def get_local_ip():
    """Obtient l'IP locale réelle"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "0.0.0.0"

def discovery_listener():
    local_ip = get_local_ip()
    print(f"🌐 Agent écoute sur: {local_ip}:{DISCOVERY_PORT}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((local_ip, DISCOVERY_PORT))

    print("Écoute discovery UDP...")

    while True:
        data, addr = sock.recvfrom(1024)
        print(f"📥 Message reçu de {addr}: {data.decode()}")
        if data.decode() == "DISCOVER_REMOTE_AGENT":
            config = load_config()
            response = {
                "name": config["name"],
                "mac": get_mac(),
                "port": 5000
            }
            response_json = json.dumps(response).encode()
            sock.sendto(response_json, addr)
            print(f"📤 Réponse envoyée à {addr}: {response_json.decode()}")
