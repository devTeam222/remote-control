from pynput.keyboard import Controller as Keyboard
from pynput.mouse import Controller as Mouse, Button

keyboard = Keyboard()
mouse = Mouse()

def handle_command(cmd):
    action = cmd.get("action")

    if action == "move":
        mouse.position = (cmd["x"], cmd["y"])

    elif action == "click":
        mouse.click(Button.left)

    elif action == "type":
        keyboard.type(cmd["text"])
    