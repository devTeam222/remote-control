import socket
import json

DISCOVERY_PORT = 37020

def discovery_listener():
    from agent import get_mac, load_config
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", DISCOVERY_PORT))

    print("Écoute discovery UDP...")

    while True:
        data, addr = sock.recvfrom(1024)
        if data.decode() == "DISCOVER_REMOTE_AGENT":
            config = load_config()
            response = {
                "name": config["name"],
                "mac": get_mac(),
                "port": 5000
            }
            sock.sendto(json.dumps(response).encode(), addr)
