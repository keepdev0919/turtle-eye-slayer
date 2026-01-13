import tkinter as tk
from tkinter import ttk, messagebox
import threading
import schedule
import time
import subprocess
import sys
import os
import utils
import settings
import popup # Ensure popup is imported
# Global control flags
is_running = False
scheduler_thread = None
stop_event = threading.Event()
current_popup_process = None
last_trigger_time = 0


class CanvasButton:
    def __init__(self, canvas, x, y, width, height, text, command, base_color="#2ecc71", hover_color="#27ae60", font=("Malgun Gothic", 16, "bold")):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.command = command
        self.base_color = base_color
        self.hover_color = hover_color
        self.font = font
        
        # Ghost Style: transparent fill, colored outline
        self.rect_id = self.create_rounded_rect(x - width/2, y - height/2, x + width/2, y + height/2, 15, fill="", outline=base_color, width=2)
        self.text_id = canvas.create_text(x, y, text=text, fill=base_color, font=font)
        
        canvas.tag_bind(self.rect_id, "<Button-1>", lambda e: self.command())
        canvas.tag_bind(self.text_id, "<Button-1>", lambda e: self.command())
        canvas.tag_bind(self.rect_id, "<Enter>", lambda e: self.on_enter())
        canvas.tag_bind(self.rect_id, "<Leave>", lambda e: self.on_leave())
        canvas.tag_bind(self.text_id, "<Enter>", lambda e: self.on_enter())
        canvas.tag_bind(self.text_id, "<Leave>", lambda e: self.on_leave())

    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [x1+r, y1, x1+r, y1, x2-r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y1+r, x2, y2-r, x2, y2-r, x2, y2, x2-r, y2, x2-r, y2, x1+r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y2-r, x1, y1+r, x1, y1+r, x1, y1]
        return self.canvas.create_polygon(points, **kwargs, smooth=True)

    def on_enter(self):
        # Hover effect: brighter outline/text
        self.canvas.itemconfig(self.rect_id, outline=self.hover_color, width=3)
        self.canvas.itemconfig(self.text_id, fill=self.hover_color)
        self.canvas.config(cursor="hand2")

    def on_leave(self):
        self.canvas.itemconfig(self.rect_id, outline=self.base_color, width=2)
        self.canvas.itemconfig(self.text_id, fill=self.base_color)
        self.canvas.config(cursor="")

    def config(self, text=None, base_color=None, hover_color=None):
        if text: self.canvas.itemconfig(self.text_id, text=text)
        if base_color: 
            self.base_color = base_color
            self.canvas.itemconfig(self.rect_id, outline=base_color)
            self.canvas.itemconfig(self.text_id, fill=base_color)
        if hover_color: self.hover_color = hover_color

# VER: 1.0.1 - FIXED PREVIEW COOLDOWN
def launch_popup(force=False):
    """Triggers the popup script via subprocess (Single Binary Mode)."""
    global current_popup_process, last_trigger_time
    
    try:
        # 1. Cooldown & duplicate check
        now = time.time()
        cooldown_remains = 30 - (now - last_trigger_time)
        
        if not force and cooldown_remains > 0:
            print(f"Skipping popup: Cooldown active ({cooldown_remains:.1f}s remains).")
            return

        if force:
            print(">>> Force launch requested (Preview mode) <<<")

        # 2. Terminate previous popup if it's still running
        if current_popup_process is not None:
            if current_popup_process.poll() is None: # Still alive
                print("Terminating existing popup to prevent accumulation...")
                current_popup_process.terminate()
                try:
                    current_popup_process.wait(timeout=1)
                except:
                    pass

        # 3. Determine how to call the popup based on execution mode
        if getattr(sys, 'frozen', False):
            # Production: The executable is the app itself
            cmd = [sys.executable, "--popup"]
        else:
            # Development: Run this script again with --popup
            cmd = [sys.executable, __file__, "--popup"]

        if sys.platform == "win32":
            current_popup_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            current_popup_process = subprocess.Popen(cmd)
            
        last_trigger_time = now
        print(f"Popup launched at {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"Error launching popup: {e}")

def load_schedule_config():
    """Loads selected minutes from config."""
    config = utils.load_json(utils.CONFIG_FILE, {"selected_minutes": [0, 30]})
    return config.get("selected_minutes", [0, 30])

def run_scheduler():
    """Background thread loop for scheduler."""
    global is_running
    print("Scheduler started.")
    schedule.clear()
    minutes = load_schedule_config()
    for m in minutes:
        schedule.every().hour.at(f":{m:02d}").do(launch_popup)
        
    while not stop_event.is_set():
        if is_running:
            schedule.run_pending()
        time.sleep(1)
    print("Scheduler thread exited.")

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("귀살대 작전 본부")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Set Window Icon
        self.set_window_icon()
        
        # Load Assets
        self.load_assets()
        
        # Main Canvas (Background)
        self.canvas = tk.Canvas(root, width=800, height=600, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Draw Background
        if self.img_bg:
            self.canvas.create_image(0, 0, image=self.img_bg, anchor="nw")
        else:
            self.canvas.configure(bg="#2c3e50")
            
        # UI Layout using Place
        
        # Override Close Protocol
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # 1. Header/Status Area (Text directly on background)
        self.status_var = tk.StringVar(value="SYSTEM READY")
        self.lbl_status = tk.Label(root, textvariable=self.status_var, font=("Malgun Gothic", 24, "bold"), fg="#aaffaa", bg="black")
        # Placing label is tricky on canvas transparently. 
        # Better to use canvas.create_text for transparency illusion if background is complex
        self.status_text_id = self.canvas.create_text(400, 100, text="작전 준비 완료", font=("Malgun Gothic", 28, "bold"), fill="#00ff00", justify="center")

        # 2. Main Button (Mission Toggle)
        self.btn_toggle = CanvasButton(self.canvas, 400, 280, 320, 80, "임무 시작", self.toggle_scheduler, 
                                       base_color="#2ecc71", hover_color="#45e683", font=("Malgun Gothic", 22, "bold"))
        
        # 3. Sub Buttons
        self.btn_preview = CanvasButton(self.canvas, 260, 420, 160, 60, "미리보기", lambda: launch_popup(force=True), 
                                        base_color="#ffffff", hover_color="#cccccc", font=("Malgun Gothic", 14, "bold"))
        
        self.btn_settings = CanvasButton(self.canvas, 540, 420, 160, 60, "환경 설정", self.open_settings, 
                                         base_color="#ffffff", hover_color="#cccccc", font=("Malgun Gothic", 14, "bold"))

        # Removed default hover binds as they are handled by CanvasButton class

        # 4. Auto-Launch Checkbox
        # We'll make a custom frame or just use text with checkbutton
        self.auto_launch_var = tk.BooleanVar(value=utils.get_autolaunch_status())
        # Use a contrasting Frame or just white text
        chk = tk.Checkbutton(root, text="맥북 시작 시 본부 자동 연결", variable=self.auto_launch_var, command=self.toggle_autolaunch,
                             font=("Malgun Gothic", 12, "bold"), fg="white", bg="black", selectcolor="black",
                             activebackground="black", activeforeground="white", highlightthickness=0)
        self.canvas.create_window(400, 520, window=chk)

        # 5. Quit Link (Small text at bottom)
        lbl_quit = tk.Label(root, text="본부 완전 종료", font=("Malgun Gothic", 9, "underline"), fg="#666666", bg="black", cursor="hand2")
        lbl_quit.bind("<Button-1>", lambda e: self.quit_app())
        self.canvas.create_window(740, 570, window=lbl_quit)

        # macOS Reopen Handler (Restores window when Dock icon is clicked)
        if sys.platform == "darwin":
            try:
                root.createcommand('tk::mac::ReopenApplication', self.show_window)
            except:
                pass

        # Initial Logic
        self.check_initial_state()

    def load_assets(self):
        """Loads images using PIL."""
        from PIL import Image, ImageTk
        
        def load_img(name, size=None):
            try:
                # Try local assets folder first
                path = os.path.join(utils.PROJECT_ROOT, "assets", name)
                if not os.path.exists(path):
                    # Try APP_DATA_DIR
                    path = os.path.join(utils.APP_DATA_DIR, "assets", name)
                
                img = Image.open(path)
                if size:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load {name}: {e}")
                return None

        self.img_bg = load_img("bg_dojo.png", (800, 600))
        # Removed image-based buttons as they are now code-styled

    def set_window_icon(self):
        """Sets the window icon if app_icon.png exists."""
        try:
            from PIL import Image, ImageTk
            icon_path = os.path.join(utils.PROJECT_ROOT, "assets", "app_icon.png")
            if not os.path.exists(icon_path):
                # Use a default character icon if app_icon.png is missing
                icon_path = os.path.join(utils.PROJECT_ROOT, "assets", "tanjiro.png")
            
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                # Keep a reference to prevent garbage collection
                self._icon_ref = photo
        except Exception as e:
            print(f"Failed to set window icon: {e}")

    def check_initial_state(self):
        self.toggle_scheduler()

    def toggle_scheduler(self):
        global is_running, scheduler_thread, stop_event
        
        if is_running:
            is_running = False
            self.canvas.itemconfig(self.status_text_id, text="⚠️ 작전 중지 ⚠️", fill="#ff4444")
            self.btn_toggle.config(text="임무 시작", base_color="#2ecc71", hover_color="#45e683")
        else:
            is_running = True
            self.canvas.itemconfig(self.status_text_id, text="⚔️ 작전 수행 중 ⚔️", fill="#44ff44")
            self.btn_toggle.config(text="임무 중지", base_color="#e74c3c", hover_color="#ff5e4d")
            
            if scheduler_thread is None or not scheduler_thread.is_alive():
                stop_event.clear()
                scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
                scheduler_thread.start()
                schedule.clear()
                minutes = load_schedule_config()
                for m in minutes:
                    schedule.every().hour.at(f":{m:02d}").do(launch_popup)

    def toggle_autolaunch(self):
        enabled = self.auto_launch_var.get()
        utils.set_autolaunch(enabled)

    def hide_window(self):
        """Hides the window instead of closing it."""
        self.root.withdraw()
        print("Dashboard hidden to background. Scheduler is still running.")

    def show_window(self):
        """Shows the window and brings it to front."""
        self.root.deiconify()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        print("Dashboard restored.")

    def quit_app(self):
        """Completely terminates the application."""
        if messagebox.askokcancel("종료", "귀살대 건강 관리 본부를 완전히 종료하시겠습니까?\n(종료 시 알림이 더 이상 뜨지 않습니다)"):
            self.cleanup_and_exit()

    def cleanup_and_exit(self):
        global stop_event
        stop_event.set()
        self.root.destroy()
        sys.exit(0)


    def on_bg_click(self, event):
        pass
    # Removed on_hover as it's handled by CanvasButton class

    def open_settings(self):
        top = tk.Toplevel(self.root)
        app = settings.MissionBoardApp(top)

if __name__ == "__main__":
    try:
        if "--popup" in sys.argv:
            # Popup Mode
            popup.show_popup()
        else:
            # Dashboard Mode
            utils.initialize_app_data()
            root = tk.Tk()
            app = DashboardApp(root)
            root.mainloop()
            stop_event.set()
    except Exception as e:
        print(f"Error: {e}")
