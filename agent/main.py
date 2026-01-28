import threading
from discovery import discovery_listener
from server import start_server

if __name__ == "__main__":
    print("🚀 Agent de contrôle à distance démarré")
    
    # Lancer discovery en thread
    discovery_thread = threading.Thread(target=discovery_listener, daemon=True)
    discovery_thread.start()
    
    # Lancer le serveur TCP
    start_server()
