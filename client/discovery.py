import socket
import json
import threading
import time

DISCOVERY_PORT = 37020
MESSAGE = "DISCOVER_REMOTE_AGENT"

def get_local_ip():
    """Obtient l'IP locale réelle (pas 169.254.x.x)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "0.0.0.0"

def get_broadcast_ip(local_ip):
    """Calcule l'adresse broadcast à partir de l'IP locale"""
    parts = local_ip.split(".")
    parts[3] = "255"
    return ".".join(parts)

def discover(timeout=8):
    devices = []
    
    local_ip = get_local_ip()
    broadcast_ip = get_broadcast_ip(local_ip)
    print(f"🌐 IP locale détectée: {local_ip}")
    print(f"📍 Broadcast cible: {broadcast_ip}")
    
    # Socket pour ÉCOUTER les réponses
    listen_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_sock.bind((local_ip, DISCOVERY_PORT))  # Écouter sur le port
    listen_sock.settimeout(timeout)
    
    # Socket pour ENVOYER le broadcast
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
    try:
        time.sleep(0.1)  # Petit délai pour s'assurer que le socket écoute
        # Envoyer le broadcast
        send_sock.sendto(MESSAGE.encode(), (broadcast_ip, DISCOVERY_PORT))
        print(f"📡 Broadcast envoyé à {broadcast_ip}")
        
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
