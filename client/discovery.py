import socket
import json

DISCOVERY_PORT = 37020
MESSAGE = "DISCOVER_REMOTE_AGENT"
CLIENT_MESSAGE = "DISCOVER_CLIENT"  # Nouveau message pour identifier le client

def discover(timeout=3, is_agent=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    # Choisir le message selon le type (agent ou client)
    message = MESSAGE if is_agent else CLIENT_MESSAGE
    
    # Utiliser 255.255.255.255 au lieu de "<broadcast>" pour Windows
    sock.sendto(message.encode(), ("255.255.255.255", DISCOVERY_PORT))
    print(f"📡 Broadcast envoyé sur port {DISCOVERY_PORT} - Type: {'Agent' if is_agent else 'Client'}")

    devices = []

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            print(f"📨 Réponse reçue de {addr}")
            info = json.loads(data.decode())
            info["ip"] = addr[0]
            devices.append(info)
    except socket.timeout:
        print("⏰ Timeout, aucune réponse")
        pass
    finally:
        sock.close()

    return devices
