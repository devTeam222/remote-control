import tkinter as tk
from tkinter import ttk, scrolledtext
import socket
import json
import threading
from discovery import discover

class RemoteControlGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Remote Control Client")
        self.root.geometry("900x700")
        self.server_socket = None
        self.server_ip = None
        self.server_port = None
        self.keyboard_input = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame découverte
        discover_frame = ttk.LabelFrame(self.root, text="Découverte", padding=10)
        discover_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(discover_frame, text="🔍 Rechercher Agents", command=self.discover_agents).pack(side=tk.LEFT, padx=5)
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(discover_frame, textvariable=self.device_var, state="readonly", width=40)
        self.device_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(discover_frame, text="Connecter", command=self.connect_server).pack(side=tk.LEFT, padx=5)
        self.status_label = ttk.Label(discover_frame, text="❌ Déconnecté", foreground="red")
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Frame contrôle clavier
        keyboard_frame = ttk.LabelFrame(self.root, text="Contrôle Clavier", padding=10)
        keyboard_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.keyboard_label = ttk.Label(keyboard_frame, text="🎯 Prêt à capturer (cliquez ici pour activer)", 
                                        background="lightgray", padding=10, relief=tk.SUNKEN)
        self.keyboard_label.pack(fill=tk.X, pady=5)
        self.keyboard_label.bind("<Button-1>", self.activate_keyboard_capture)
        
        ttk.Label(keyboard_frame, text="Cliquez sur la zone grise pour capturer clavier/souris (Échap pour arrêter)").pack(anchor=tk.W)
        
        # Frame contrôle souris
        mouse_frame = ttk.LabelFrame(self.root, text="Contrôle Souris", padding=10)
        mouse_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.canvas = tk.Canvas(mouse_frame, bg="gray20", cursor="cross", height=300)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Motion>", self.on_mouse_move)
        self.canvas.bind("<Button-1>", lambda e: self.on_mouse_click(e, "left"))
        self.canvas.bind("<Button-3>", lambda e: self.on_mouse_click(e, "right"))
        self.canvas.bind("<Button-2>", lambda e: self.on_mouse_click(e, "middle"))
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)
        
        # Frame log
        log_frame = ttk.LabelFrame(self.root, text="Activité", padding=10)
        log_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=6, state=tk.DISABLED)
        self.log_text.pack(fill=tk.X)
        
        self.devices = []
        
    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        
    def discover_agents(self):
        self.log("🔍 Recherche d'agents...")
        def discover_thread():
            try:
                self.devices = discover()
                if self.devices:
                    device_list = [f"{d.get('name', 'Unknown')} ({d['ip']})" for d in self.devices]
                    self.device_combo['values'] = device_list
                    self.log(f"✅ {len(self.devices)} agent(s) trouvé(s)")
                else:
                    self.log("❌ Aucun agent trouvé")
            except Exception as e:
                self.log(f"❌ Erreur: {e}")
        
        threading.Thread(target=discover_thread, daemon=True).start()
        
    def connect_server(self):
        idx = self.device_combo.current()
        if idx < 0 or idx >= len(self.devices):
            self.log("❌ Sélectionnez un agent")
            return
        
        device = self.devices[idx]
        self.server_ip = device['ip']
        self.server_port = device['port']
        
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.server_ip, self.server_port))
            self.status_label.config(text=f"✅ Connecté à {self.server_ip}", foreground="green")
            self.log(f"✅ Connecté à {device.get('name', 'Agent')} ({self.server_ip}:{self.server_port})")
        except Exception as e:
            self.log(f"❌ Erreur connexion: {e}")
            self.status_label.config(text="❌ Erreur", foreground="red")
            
    def activate_keyboard_capture(self, event=None):
        self.keyboard_label.config(text="⏺️ CAPTURE ACTIVE - Appuyez sur Échap pour arrêter", 
                                   background="lightgreen")
        self.keyboard_label.focus_set()
        self.keyboard_label.bind("<KeyPress>", self.on_key_press)
        self.keyboard_label.bind("<KeyRelease>", self.on_key_release)
        self.keyboard_label.bind("<Escape>", self.deactivate_keyboard_capture)
        
    def deactivate_keyboard_capture(self, event=None):
        self.keyboard_label.config(text="🎯 Prêt à capturer (cliquez ici pour activer)", 
                                   background="lightgray")
        self.keyboard_label.unbind("<KeyPress>")
        self.keyboard_label.unbind("<KeyRelease>")
        self.keyboard_label.unbind("<Escape>")
        
    def send_command(self, command_type, data):
        if not self.server_socket:
            self.log("❌ Non connecté au serveur")
            return
        
        try:
            msg = json.dumps({"type": command_type, "data": data})
            self.server_socket.sendall(msg.encode() + b'\n')
        except ConnectionResetError:
            self.log("❌ Connexion perdue avec le serveur")
            self.server_socket = None
            self.status_label.config(text="❌ Déconnecté", foreground="red")
        except Exception as e:
            self.log(f"❌ Erreur envoi: {e}")
            
    def on_key_press(self, event):
        modifiers = []
        if event.state & 0x0001:
            modifiers.append("shift")
        if event.state & 0x0004:
            modifiers.append("ctrl")
        if event.state & 0x0008:
            modifiers.append("alt")
        
        key = event.keysym
        self.send_command("keyboard", {"action": "press", "key": key, "modifiers": modifiers})
        self.log(f"⌨️ Touche: {'+'.join(modifiers + [key]) if modifiers else key}")
        return "break"
        
    def on_key_release(self, event):
        if event.keysym == "Escape":
            return
        key = event.keysym
        self.send_command("keyboard", {"action": "release", "key": key})
        return "break"
        
    def on_mouse_move(self, event):
        x = event.x
        y = event.y
        self.send_command("mouse", {"action": "move", "x": x, "y": y})
        
    def on_mouse_click(self, event, button):
        self.send_command("mouse", {"action": "click", "button": button, "x": event.x, "y": event.y})
        self.log(f"🖱️ Clic {button} à ({event.x}, {event.y})")
        
    def on_mouse_wheel(self, event):
        delta = 1 if event.num == 4 or event.delta > 0 else -1
        self.send_command("mouse", {"action": "scroll", "delta": delta})
        self.log(f"🖱️ Scroll: {delta}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RemoteControlGUI(root)
    root.mainloop()
