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
    print(f"🌐 Agent IP locale: {local_ip}:{DISCOVERY_PORT}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", DISCOVERY_PORT))

    print("Écoute discovery UDP sur toutes les interfaces...")

    while True:
        data, addr = sock.recvfrom(1024)
        message = data.decode()
        print(f"📥 Message reçu de {addr}: {message}")
        
        if message.startswith("DISCOVER_REMOTE_AGENT"):
            client_port = 37020
            try:
                client_port = int(message.split(":")[1])
            except:
                pass
            
            config = load_config()
            response = {
                "name": config["name"],
                "mac": get_mac(),
                "port": 5000,
                "ip": local_ip
            }
            response_json = json.dumps(response).encode()
            reply_addr = (addr[0], client_port)
            sock.sendto(response_json, reply_addr)
            print(f"📤 Réponse envoyée à {reply_addr}: {response_json.decode()}")
