import tkinter as tk
import random
import sys
import os
from PIL import Image, ImageTk
import utils

FONT = utils.FONT_FAMILY

# Visual Novel Style Dimensions
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 500

def show_popup():
    # Load Data
    character_data_list = utils.get_character_data()
    # Get both Eye and Neck exercises
    exercises = utils.get_random_exercises()
    
    # Skip characters whose image file is missing instead of crashing the popup
    available = [c for c in character_data_list if os.path.exists(utils.get_asset_path(c.get("image", "")))]
    missing = len(character_data_list) - len(available)
    if missing:
        print(f"Warning: {missing} character(s) skipped because their image is missing.")
    character_data_list = available

    if not character_data_list or not exercises["eye"]:
        print("No data found")
        sys.exit(1)

    # Random Selection
    char_data = random.choice(character_data_list)
    
    # Character Info
    image_file = char_data["image"]
    character_name = char_data["name"]
    quote = random.choice(char_data["quotes"])
    
    root = tk.Tk()
    root.title(f"귀살대 건강 관리")

    # Same bundle as the dashboard: keep this process out of the Dock as well.
    try:
        import menubar
        menubar.hide_dock_icon()
        menubar.install_dock_guard(root)
    except Exception as e:
        print(f"dock hide skipped: {e}")
    
    # Set Window Icon
    try:
        from PIL import Image, ImageTk
        icon_path = os.path.join(utils.BUNDLED_ASSETS_DIR, "app_icon.png")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(utils.BUNDLED_ASSETS_DIR, "tanjiro.png")
        
        if os.path.exists(icon_path):
            img = Image.open(icon_path)
            photo = ImageTk.PhotoImage(img)
            root.iconphoto(True, photo)
            # Keep a reference
            root._icon_ref = photo
    except Exception as e:
        print(f"Failed to set window icon: {e}")
    
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
    
    # Main Container (Split 60% Left, 40% Right)
    # Left: Character Image (Canvas)
    # Right: Info Panel (Frame)
    
    # Left Frame (Character)
    left_width = int(WINDOW_WIDTH * 0.6)
    right_width = WINDOW_WIDTH - left_width
    
    # Canvas for Character Area
    canvas = tk.Canvas(root, width=left_width, height=WINDOW_HEIGHT, bg="black", highlightthickness=0)
    canvas.place(x=0, y=0, width=left_width, height=WINDOW_HEIGHT)
    
    try:
        full_path = utils.get_asset_path(image_file)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Image not found: {full_path}")
        pil_image = Image.open(full_path)
        
        # Resize to fit height, maintain aspect ratio if possible or crop?
        # For visual novel look, valid strategy: resize height to match window, crop width if needed
        # Or simple resize to cover
        
        # Strategy: Resize ensuring height interacts well
        # Let's simple resize to filling the left area 
        # Actually better to retain aspect ratio and crop top/bottom or left/right
        # Simple implementation: Resize to (left_width, WINDOW_HEIGHT)
        pil_image = pil_image.resize((left_width, WINDOW_HEIGHT), Image.Resampling.LANCZOS)
        tk_image = ImageTk.PhotoImage(pil_image)
        
        canvas.create_image(0, 0, anchor=tk.NW, image=tk_image)
    except Exception as e:
        print(f"Asset Error: {e}")
        root.destroy()
        sys.exit(1)

    # Create gradient/overlay for text readability on the left image
    # We'll use a semi-transparent rectangle at the bottom of the canvas
    overlay_height = 120
    overlay_y_start = WINDOW_HEIGHT - overlay_height
    
    # Create a semi-transparent dark block
    # Since Tkinter Canvas doesn't support alpha directly on shapes easily without images,
    # we create a specialized image for the gradient/overlay
    overlay_image = Image.new('RGBA', (left_width, overlay_height), (0, 0, 0, 180)) # Black with ~70% opacity
    tk_overlay = ImageTk.PhotoImage(overlay_image)
    
    canvas.create_image(0, overlay_y_start, anchor=tk.NW, image=tk_overlay)
    
    # Text on Left Panel
    text_margin = 20
    name_y = overlay_y_start + 25
    quote_y = name_y + 35
    
    # Name
    canvas.create_text(text_margin, name_y, anchor=tk.NW, text=character_name, fill="#FFC107", font=(FONT, 16, "bold"))
    
    # Quote
    canvas.create_text(text_margin, quote_y, anchor=tk.NW, text=f'"{quote}"', fill="#FFFFFF", font=(FONT, 12, "italic"), width=left_width - (text_margin*2))

    # Keep references to prevent GC
    root.tk_overlay = tk_overlay
    
    # Right Frame (Info Panel)
    right_frame = tk.Frame(root, bg="#1a1a1a", width=right_width, height=WINDOW_HEIGHT)
    right_frame.place(x=left_width, y=0, width=right_width, height=WINDOW_HEIGHT)
    right_frame.pack_propagate(False)

    # --- Layout Logic: Fixed Bottom Bar + Scrollable Content ---
    
    # 1. Fixed Bottom Bar (Buttons)
    bottom_bar = tk.Frame(right_frame, bg="#1a1a1a", height=60)
    bottom_bar.pack(side="bottom", fill="x", padx=20, pady=15)
    
    # 2. Scrollable Container (Canvas)
    canvas_container = tk.Frame(right_frame, bg="#1a1a1a")
    canvas_container.pack(side="top", fill="both", expand=True)

    # Scrollbar
    scrollbar = tk.Scrollbar(canvas_container, orient="vertical", bg="#1a1a1a") # Style depends on OS, usually native
    scrollbar.pack(side="right", fill="y")

    # Canvas
    content_canvas = tk.Canvas(canvas_container, bg="#1a1a1a", highlightthickness=0, yscrollcommand=scrollbar.set)
    content_canvas.pack(side="left", fill="both", expand=True)
    
    scrollbar.config(command=content_canvas.yview)

    # Inner Frame (Holds the actual text)
    scroll_frame = tk.Frame(content_canvas, bg="#1a1a1a")
    
    # Create window inside canvas
    # We set width matches canvas width roughly (minus scrollbar space)
    canvas_window = content_canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

    def on_structure_change(event):
        # Update scrollregion
        content_canvas.configure(scrollregion=content_canvas.bbox("all"))
        # Update width to match canvas (responsive)
        content_canvas.itemconfig(canvas_window, width=event.width)

    content_canvas.bind("<Configure>", on_structure_change)
    
    # MouseWheel Scrolling
    def _on_mousewheel(event):
        if sys.platform == "darwin":
            step = -1 if event.delta > 0 else 1
        else:
            step = int(-1 * (event.delta / 120)) or (-1 if event.delta > 0 else 1)
        content_canvas.yview_scroll(step, "units")
        
    # Linux support (if needed) uses Button-4/5, but focusing on Mac/Windows
    content_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    # --- Content Population (Inside scroll_frame) ---
    PADDING_X = 20
    
    def create_exercise_block(parent, category, title, desc, color):
        block = tk.Frame(parent, bg="#1a1a1a")
        block.pack(fill="x", padx=PADDING_X, pady=(20, 10))
        
        lbl_cat = tk.Label(block, text=f"[{category}]", font=(FONT, 10, "bold"), fg=color, bg="#1a1a1a", anchor="w")
        lbl_cat.pack(fill="x")
        
        lbl_title = tk.Label(block, text=title, font=(FONT, 12, "bold"), fg="white", bg="#1a1a1a", anchor="w", wraplength=right_width-60)
        lbl_title.pack(fill="x", pady=(2, 5))
        
        lbl_desc = tk.Label(block, text=desc, font=(FONT, 10), fg="#cccccc", bg="#1a1a1a", anchor="w", justify="left", wraplength=right_width-60)
        lbl_desc.pack(fill="x")
        
        return block

    # 1. Eye Block
    if exercises["eye"]:
        create_exercise_block(scroll_frame, "눈 건강", exercises["eye"]["title"], exercises["eye"]["description"], "#1E90FF")
        
    # Separator
    tk.Frame(scroll_frame, bg="#333333", height=1).pack(fill="x", padx=PADDING_X, pady=5)

    # 2. Neck Block
    if exercises["neck"]:
        create_exercise_block(scroll_frame, "거북목 탈출", exercises["neck"]["title"], exercises["neck"]["description"], "#FF8C00")

    # Separator (Bottom padding for scroll)
    tk.Frame(scroll_frame, bg="#333333", height=1).pack(fill="x", padx=PADDING_X, pady=20)

    # --- Buttons (In Fixed Bottom Bar) ---
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

    def on_confirm():
        root.destroy()
    def on_settings():
        # The dashboard process watches our exit code and opens its settings window.
        root.destroy()
        sys.exit(utils.POPUP_EXIT_OPEN_SETTINGS)

    # Settings Button
    HoverButton(
        bottom_bar, 
        text="⚙️ 설정", 
        command=on_settings, 
        bg="#2D2D2D", 
        fg="#888888", 
        hover_bg="#3ea6ff",
        font=(FONT, 10),
        padx=12, pady=8
    ).pack(side="left")

    # Confirm Button
    HoverButton(
        bottom_bar, 
        text="✓ 임무 완료", 
        command=on_confirm, 
        bg="#4CAF50", 
        fg="white", 
        hover_bg="#45a049", 
        font=(FONT, 11, "bold"),
        padx=20, pady=8
    ).pack(side="right")

    # Keep references
    root.tk_image = tk_image 

    # The bundle is a background-only app (LSUIElement); activate so the popup shows on top.
    try:
        import menubar
        menubar.activate_app()
        menubar.hide_dock_icon()
    except Exception as e:
        print(f"activate skipped: {e}")
    root.lift()
    root.mainloop()

if __name__ == "__main__":
    show_popup()
