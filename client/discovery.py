import socket
import json

DISCOVERY_PORT = 37020
MESSAGE = "DISCOVER_REMOTE_AGENT"

def discover(timeout=3):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(timeout)

    sock.sendto(MESSAGE.encode(), ("<broadcast>", DISCOVERY_PORT))

    devices = []

    try:
        while True:
            data, addr = sock.recvfrom(1024)
            info = json.loads(data.decode())
            info["ip"] = addr[0]
            devices.append(info)
    except socket.timeout:
        pass

    return devices
