import socket
import json
import threading
import pynput
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController

keyboard = KeyboardController()
mouse = MouseController()

def handle_client(client_socket, addr):
    """Traite les commandes d'un client connecté"""
    print(f"✅ Client connecté: {addr}")
    
    try:
        buffer = ""
        while True:
            data = client_socket.recv(1024).decode()
            if not data:
                break
            
            buffer += data
            while '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                if not line:
                    continue
                
                try:
                    cmd = json.loads(line)
                    process_command(cmd, addr)
                except json.JSONDecodeError as e:
                    print(f"❌ Erreur JSON: {e}")
    
    except Exception as e:
        print(f"❌ Erreur client {addr}: {e}")
    finally:
        client_socket.close()
        print(f"❌ Client déconnecté: {addr}")

def process_command(cmd, addr):
    """Exécute les commandes reçues"""
    cmd_type = cmd.get("type")
    data = cmd.get("data", {})
    
    if cmd_type == "keyboard":
        action = data.get("action")
        key = data.get("key", "")
        
        if not key:
            return
        
        try:
            key_obj = parse_key(key)
            
            if action == "press":
                keyboard.press(key_obj)
                print(f"⌨️ Press: {key}")
            elif action == "release":
                keyboard.release(key_obj)
                print(f"⌨️ Release: {key}")
        except Exception as e:
            print(f"❌ Erreur clavier ({key}): {type(e).__name__}")
    
    elif cmd_type == "mouse":
        action = data.get("action")
        try:
            if action == "move":
                x = data.get("x", 0)
                y = data.get("y", 0)
                mouse.position = (x, y)
                print(f"🖱️ Move: ({x}, {y})")
            
            elif action == "click":
                button = data.get("button", "left")
                btn = pynput.mouse.Button.left
                if button.lower() == "right":
                    btn = pynput.mouse.Button.right
                elif button.lower() == "middle":
                    btn = pynput.mouse.Button.middle
                mouse.click(btn)
                print(f"🖱️ Click: {button}")
            
            elif action == "scroll":
                delta = data.get("delta", 0)
                mouse.scroll(0, delta)
                print(f"🖱️ Scroll: {delta}")
        except Exception as e:
            print(f"❌ Erreur souris: {e}")

def parse_key(key_str):
    """Convertit les noms de touches en objets Key - envoie tout en natif"""
    key_str_lower = key_str.lower()
    
    # Mapping des touches spéciales uniquement
    special_keys = {
        "shift_l": Key.shift,
        "shift_r": Key.shift,
        "shift": Key.shift,
        "control_l": Key.ctrl,
        "control_r": Key.ctrl,
        "control": Key.ctrl,
        "alt_l": Key.alt,
        "alt_r": Key.alt,
        "alt": Key.alt,
        "win_l": Key.cmd,
        "win_r": Key.cmd,
        "windows": Key.cmd,
        "cmd": Key.cmd,
        "return": Key.enter,
        "enter": Key.enter,
        "space": " ",
        "tab": Key.tab,
        "backspace": Key.backspace,
        "back": Key.backspace,
        "delete": Key.delete,
        "del": Key.delete,
        "escape": Key.esc,
        "esc": Key.esc,
        "up": Key.up,
        "down": Key.down,
        "left": Key.left,
        "right": Key.right,
        "home": Key.home,
        "end": Key.end,
        "page_up": Key.page_up,
        "pageup": Key.page_up,
        "page_down": Key.page_down,
        "pagedown": Key.page_down,
        "insert": Key.insert,
        "ins": Key.insert,
        "f1": Key.f1,
        "f2": Key.f2,
        "f3": Key.f3,
        "f4": Key.f4,
        "f5": Key.f5,
        "f6": Key.f6,
        "f7": Key.f7,
        "f8": Key.f8,
        "f9": Key.f9,
        "f10": Key.f10,
        "f11": Key.f11,
        "f12": Key.f12,
        "caps_lock": Key.caps_lock,
        "num_lock": Key.num_lock,
        "scroll_lock": Key.scroll_lock,
        "print": Key.print_screen,
        "print_screen": Key.print_screen,
        "pause": Key.pause,
        "menu": Key.alt_gr,
        "context_menu": Key.alt_gr,
    }
    
    # Si c'est dans le mapping, retourner l'objet Key
    if key_str_lower in special_keys:
        return special_keys[key_str_lower]
    
    # Sinon, envoyer la touche telle quel (une lettre, un chiffre, un symbole, etc.)
    return key_str

def start_server(host="0.0.0.0", port=5000):
    """Lance le serveur TCP"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print(f"🚀 Serveur écoute sur {host}:{port}")
    
    try:
        while True:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr), daemon=True)
            thread.start()
    except KeyboardInterrupt:
        print("\n⛔ Serveur arrêté")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
