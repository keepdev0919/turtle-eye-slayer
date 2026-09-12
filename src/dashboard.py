import tkinter as tk
from tkinter import messagebox
import threading
import schedule
import time
import subprocess
import sys
import os
import utils
import settings
import popup # Ensure popup is imported

FONT = utils.FONT_FAMILY

# Global control flags
is_running = False
scheduler_thread = None
stop_event = threading.Event()
current_popup_process = None
last_trigger_time = 0
POPUP_COOLDOWN_SECONDS = 30


class CanvasButton:
    def __init__(self, canvas, x, y, width, height, text, command, base_color="#2ecc71", hover_color="#27ae60", font=(FONT, 16, "bold")):
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


def launch_popup(force=False):
    """Triggers the popup script via subprocess (Single Binary Mode).

    Called from the scheduler thread (scheduled job) and from the main thread (preview)."""
    global current_popup_process, last_trigger_time
    
    try:
        # 1. Cooldown & duplicate check (preview never touches the cooldown)
        now = time.time()
        cooldown_remains = POPUP_COOLDOWN_SECONDS - (now - last_trigger_time)
        
        if not force and cooldown_remains > 0:
            print(f"Skipping popup: Cooldown active ({cooldown_remains:.1f}s remains).")
            return

        if force:
            print(">>> Force launch requested (Preview mode) <<<")

        # 2. Terminate previous popup if it's still running
        terminate_popup()

        # 3. Determine how to call the popup based on execution mode
        if getattr(sys, 'frozen', False):
            # Production: The executable is the app itself
            cmd = [sys.executable, "--popup"]
        else:
            # Development: Run this script again with --popup
            cmd = [sys.executable, os.path.abspath(__file__), "--popup"]

        if sys.platform == "win32":
            current_popup_process = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            current_popup_process = subprocess.Popen(cmd)
            
        if not force:
            last_trigger_time = now
        print(f"Popup launched at {time.strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"Error launching popup: {e}")

def terminate_popup():
    """Closes the popup window process if it is still open."""
    proc = current_popup_process
    if proc is not None and proc.poll() is None:
        print("Terminating existing popup...")
        proc.terminate()
        try:
            proc.wait(timeout=1)
        except Exception:
            pass

def apply_schedule():
    """(Scheduler thread only) Re-registers jobs from config.json."""
    schedule.clear()
    minutes = utils.get_schedule_minutes()
    for m in minutes:
        schedule.every().hour.at(f":{m:02d}").do(launch_popup)
    print(f"Schedule applied for minutes: {minutes}")

def run_scheduler():
    """Background thread loop for scheduler.

    This thread is the only place that touches the `schedule` module, so there is no
    cross-thread race. Config changes are picked up automatically via the file's mtime,
    which also covers edits made from the settings window or by hand."""
    print("Scheduler started.")
    last_mtime = None
    while not stop_event.is_set():
        mtime = utils.get_config_mtime()
        if mtime != last_mtime:
            apply_schedule()
            last_mtime = mtime
        if is_running:
            schedule.run_pending()
        stop_event.wait(1)
    print("Scheduler thread exited.")

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("귀살대 작전 본부")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.settings_window = None
        self._handled_popup = None
        
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
            
        # Override Close Protocol
        self.root.protocol("WM_DELETE_WINDOW", self.hide_window)
        
        # 1. Status text drawn directly on the background canvas
        self.status_text_id = self.canvas.create_text(400, 100, text="작전 준비 완료", font=(FONT, 28, "bold"), fill="#00ff00", justify="center")

        # 2. Main Button (Mission Toggle)
        self.btn_toggle = CanvasButton(self.canvas, 400, 280, 320, 80, "임무 시작", self.toggle_scheduler, 
                                       base_color="#2ecc71", hover_color="#45e683", font=(FONT, 22, "bold"))
        
        # 3. Sub Buttons
        self.btn_preview = CanvasButton(self.canvas, 260, 420, 160, 60, "미리보기", lambda: launch_popup(force=True), 
                                        base_color="#ffffff", hover_color="#cccccc", font=(FONT, 14, "bold"))
        
        self.btn_settings = CanvasButton(self.canvas, 540, 420, 160, 60, "환경 설정", self.open_settings, 
                                         base_color="#ffffff", hover_color="#cccccc", font=(FONT, 14, "bold"))

        # 4. Auto-Launch Checkbox (self-heals a stale plist if the app was moved)
        self.auto_launch_var = tk.BooleanVar(value=utils.sync_autolaunch())
        chk = tk.Checkbutton(root, text="맥북 시작 시 본부 자동 연결", variable=self.auto_launch_var, command=self.toggle_autolaunch,
                             font=(FONT, 12, "bold"), fg="white", bg="black", selectcolor="black",
                             activebackground="black", activeforeground="white", highlightthickness=0)
        self.canvas.create_window(400, 520, window=chk)

        # 5. Quit Link (Small text at bottom)
        lbl_quit = tk.Label(root, text="본부 완전 종료", font=(FONT, 9, "underline"), fg="#666666", bg="black", cursor="hand2")
        lbl_quit.bind("<Button-1>", lambda e: self.quit_app())
        self.canvas.create_window(740, 570, window=lbl_quit)

        # macOS Reopen Handler (Restores window when Dock icon is clicked)
        if sys.platform == "darwin":
            try:
                root.createcommand('tk::mac::ReopenApplication', self.show_window)
            except Exception:
                pass

        # Initial Logic
        self.toggle_scheduler()
        self.root.after(1000, self.poll_popup)

    def load_assets(self):
        """Loads images using PIL."""
        from PIL import Image, ImageTk
        
        def load_img(name, size=None):
            try:
                # Try bundled assets first, then the user's data folder
                path = os.path.join(utils.BUNDLED_ASSETS_DIR, name)
                if not os.path.exists(path):
                    path = utils.get_asset_path(name)
                
                img = Image.open(path)
                if size:
                    img = img.resize(size, Image.Resampling.LANCZOS)
                return ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Failed to load {name}: {e}")
                return None

        self.img_bg = load_img("bg_dojo.png", (800, 600))

    def set_window_icon(self):
        """Sets the window icon if app_icon.png exists."""
        try:
            from PIL import Image, ImageTk
            icon_path = os.path.join(utils.BUNDLED_ASSETS_DIR, "app_icon.png")
            if not os.path.exists(icon_path):
                # Use a default character icon if app_icon.png is missing
                icon_path = os.path.join(utils.BUNDLED_ASSETS_DIR, "tanjiro.png")
            
            if os.path.exists(icon_path):
                img = Image.open(icon_path)
                photo = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, photo)
                # Keep a reference to prevent garbage collection
                self._icon_ref = photo
        except Exception as e:
            print(f"Failed to set window icon: {e}")

    def toggle_scheduler(self):
        global is_running, scheduler_thread
        
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

    def poll_popup(self):
        """Watches the popup process; when it exits asking for settings, open them here."""
        proc = current_popup_process
        if proc is not None and proc is not self._handled_popup and proc.poll() is not None:
            self._handled_popup = proc
            if proc.returncode == utils.POPUP_EXIT_OPEN_SETTINGS:
                self.show_window()
                self.open_settings()
        self.root.after(1000, self.poll_popup)

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
        stop_event.set()
        terminate_popup()
        self.root.destroy()
        sys.exit(0)

    def open_settings(self):
        # Reuse the window if it is already open
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.lift()
            self.settings_window.focus_force()
            return
        top = tk.Toplevel(self.root)
        self.settings_window = top
        settings.MissionBoardApp(top)

if __name__ == "__main__":
    try:
        utils.initialize_app_data()
        if "--popup" in sys.argv:
            # Popup Mode
            popup.show_popup()
        else:
            # Dashboard Mode
            root = tk.Tk()
            app = DashboardApp(root)
            root.mainloop()
            stop_event.set()
    except Exception as e:
        print(f"Error: {e}")
