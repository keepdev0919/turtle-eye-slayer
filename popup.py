import tkinter as tk
import random
import sys
import os
from PIL import Image, ImageTk
import utils

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 600

def show_popup():
    # Reload characters
    character_data_list = utils.load_characters()
    if not character_data_list:
        print("No characters found")
        sys.exit(1)

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
        full_path = utils.get_asset_path(image_file)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Image not found: {full_path}")
        pil_image = Image.open(full_path)
        pil_image = pil_image.resize((WINDOW_WIDTH, WINDOW_HEIGHT), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
    except Exception as e:
        print(f"Asset Error: {e}")
        root.destroy()
        sys.exit(1)

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
        # Open settings using utils
        utils.open_settings_ui()

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

if __name__ == "__main__":
    show_popup()
