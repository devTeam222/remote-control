import socket
import json
import threading
import time

DISCOVERY_PORT = 37020
MESSAGE = "DISCOVER_REMOTE_AGENT"

def discover(timeout=8):
    devices = []
    
    # Socket pour ÉCOUTER les réponses broadcast
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind(("0.0.0.0", DISCOVERY_PORT))  # Écouter sur le port
    listen_sock.settimeout(timeout)
    
    # Socket pour ENVOYER le broadcast
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        time.sleep(0.1)  # Petit délai pour s'assurer que le socket écoute
        # Envoyer le broadcast
        send_sock.sendto(MESSAGE.encode(), ("255.255.255.255", DISCOVERY_PORT))
        print(f"📡 Broadcast envoyé: {MESSAGE}")
        
        # Écouter les réponses
        while True:
            data, addr = listen_sock.recvfrom(1024)
            print(f"✅ Réponse de {addr[0]}: {data.decode()}")
            try:
                info = json.loads(data.decode())
                info["ip"] = addr[0]
                devices.append(info)
            except:
                pass
    except socket.timeout:
        print(f"⏰ Timeout après {timeout}s")
    finally:
        listen_sock.close()
        send_sock.close()

    return devices
