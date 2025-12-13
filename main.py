import schedule
import time
import random
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import sys
import json
import subprocess

# Configuration
def get_base_dir():
    if getattr(sys, 'frozen', False):
        # If run as a bundle: .../Appname.app/Contents/MacOS/Appname
        # We want the folder containing Appname.app
        return os.path.abspath(os.path.join(os.path.dirname(sys.executable), "../../.."))
    else:
        return os.path.dirname(__file__)

BASE_DIR = get_base_dir()
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
CHARACTERS_FILE = os.path.join(BASE_DIR, "characters.json")
# Path to the sibling "환경설정.app"
SETTINGS_APP = os.path.join(BASE_DIR, "환경설정.app")

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 600

# ... (omitted imports or other constants if any) ...

def load_characters():
    """Loads character data from JSON file."""
    if not os.path.exists(CHARACTERS_FILE):
        return []
    try:
        with open(CHARACTERS_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading characters: {e}")
        return []

def get_asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)

def load_config():
    """Lads selected minutes from config.json"""
    default_config = [50]
    if not os.path.exists(CONFIG_FILE):
        return default_config
    try:
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("selected_minutes", default_config)
    except:
        return default_config

def open_settings_ui():
    """Launches the settings UI."""
    if os.path.exists(SETTINGS_APP):
        subprocess.Popen(["open", SETTINGS_APP])
    else:
        # Fallback for dev mode
        dev_settings = os.path.join(BASE_DIR, "settings.py")
        subprocess.Popen([sys.executable, dev_settings])

def show_visual_popup():
    """Creates and displays the health reminder popup (Minimal UI)."""
    print(f"Health check triggered at {time.strftime('%H:%M:%S')}")
    
    # Reload characters
    character_data_list = load_characters()
    if not character_data_list:
        print("No characters found")
        return

    data = random.choice(character_data_list)
    image_file = data["image"]
    character_name = data["name"]
    quote = random.choice(data["quotes"])
    
    root = tk.Tk()
    root.title(f"귀살대 건강 관리")
    
    # FRAMELESS WINDOW SETUP
    root.overrideredirect(True) # Remove Title Bar
    root.attributes('-topmost', True)
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_cordinate = int((screen_width / 2) - (WINDOW_WIDTH / 2))
    y_cordinate = int((screen_height / 2) - (WINDOW_HEIGHT / 2))
    root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x_cordinate}+{y_cordinate}")

    # Drag Logic
    def start_move(event):
        root.x = event.x
        root.y = event.y

    def stop_move(event):
        root.x = None
        root.y = None

    def do_move(event):
        deltax = event.x - root.x
        deltay = event.y - root.y
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")

    root.bind("<ButtonPress-1>", start_move)
    root.bind("<ButtonRelease-1>", stop_move)
    root.bind("<B1-Motion>", do_move)
    
    try:
        # 1. Character Image
        full_path = get_asset_path(image_file)
        if not os.path.exists(full_path):
            raise FileNotFoundError
        pil_image = Image.open(full_path)
        pil_image = pil_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
    except Exception as e:
        print(f"Asset Error: {e}")
        root.destroy()
        return

    canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)
    
    # Layer 1: Character (Full Screen)
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    
    # Layer 2: Minimal Text Bar (Bottom 30%)
    text_height = 180
    text_y_start = WINDOW_HEIGHT - text_height
    
    # Solid dark bar for high readability
    canvas.create_rectangle(0, text_y_start, WINDOW_WIDTH, WINDOW_HEIGHT, fill="#1a1a1a", outline="")
    
    # Text Content
    text_padding = 25
    name_y = text_y_start + text_padding
    quote_y = name_y + 35
    
    # Name (Golden Yellow)
    canvas.create_text(text_padding, name_y, anchor=tk.NW, text=character_name, fill="#FFC107", font=("Malgun Gothic", 14, "bold"))
    
    # Quote (White)
    canvas.create_text(text_padding, quote_y, anchor=tk.NW, text=f'"{quote}"', fill="#FFFFFF", font=("Malgun Gothic", 12), width=WINDOW_WIDTH - (text_padding*2))
    
    # --- Custom Hover Button Logic ---
    class HoverButton(tk.Label):
        def __init__(self, parent, text, command=None, bg="#333333", fg="white", hover_bg="#555555", **kwargs):
            super().__init__(parent, text=text, bg=bg, fg=fg, cursor="hand2", **kwargs)
            self.default_bg = bg
            self.hover_bg = hover_bg
            self.command = command
            self.bind("<Enter>", self.on_enter)
            self.bind("<Leave>", self.on_leave)
            self.bind("<Button-1>", self.on_click)

        def on_enter(self, e):
            self.config(bg=self.hover_bg)

        def on_leave(self, e):
            self.config(bg=self.default_bg)

        def on_click(self, e):
            if self.command:
                self.command()

    # Buttons
    def on_confirm():
        root.destroy()
    def on_settings():
        root.destroy()
        open_settings_ui()

    # Settings Button
    # Dark grey minimal style
    btn_settings = HoverButton(
        root, 
        text="⚙️ 설정", 
        command=on_settings, 
        bg="#1a1a1a", # Matches text bar
        fg="#888888", 
        hover_bg="#333333",
        font=("Malgun Gothic", 11),
        padx=10, pady=5
    )

    # Complete Button
    # Stylish Borderless, slightly distinct grey
    btn_confirm = HoverButton(
        root, 
        text="✓ 임무 완료", 
        command=on_confirm, 
        bg="#2D2D2D", 
        fg="#FFFFFF", 
        hover_bg="#404040", 
        font=("Malgun Gothic", 12, "bold"),
        padx=20, pady=8
    )

    # Placement
    # Settings: Bottom Left
    canvas.create_window(30, WINDOW_HEIGHT - 35, window=btn_settings, anchor=tk.W)
    
    # Confirm: Bottom Right
    canvas.create_window(WINDOW_WIDTH - 30, WINDOW_HEIGHT - 35, window=btn_confirm, anchor=tk.E)

    # Keep references
    root.tk_image = tk_image 
    
    root.mainloop()

def apply_schedule(minutes_list):
    """Clears and re-applies schedule based on list of minutes"""
    schedule.clear()
    print(f"Applying schedule for minutes: {minutes_list}")
    for m in minutes_list:
        minute_str = f":{m:02d}"
        schedule.every().hour.at(minute_str).do(show_visual_popup)
    
def get_config_mtime():
    """Returns modification time of config file"""
    if os.path.exists(CONFIG_FILE):
        return os.path.getmtime(CONFIG_FILE)
    return 0

def main():
    print("귀살대 건강 관리 프로그램이 시작되었습니다. (백그라운드 실행 중)")
    print("설정된 시간마다 알림이 울립니다.")
    
    # 1. Initial Load
    current_minutes = load_config()
    apply_schedule(current_minutes)
    
    last_mtime = get_config_mtime()

    # Main Loop
    try:
        while True:
            # Check for config changes
            current_mtime = get_config_mtime()
            if current_mtime != last_mtime:
                print("Configuration change detected. Reloading schedule...")
                current_minutes = load_config()
                apply_schedule(current_minutes)
                last_mtime = current_mtime
            
            schedule.run_pending()
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")
        sys.exit(0)

if __name__ == "__main__":
    main()
