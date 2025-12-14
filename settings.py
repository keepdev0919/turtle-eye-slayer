import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from PIL import Image, ImageTk
import json
import os
import shutil
import time

import sys
import utils

# Constants
BASE_DIR = utils.BASE_DIR
CONFIG_FILE = utils.CONFIG_FILE
CHARACTERS_FILE = utils.CHARACTERS_FILE
ASSETS_DIR = utils.ASSETS_DIR

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 650

def load_json(filepath, default_value):
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return default_value

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

class MissionBoardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("환경설정")
        
        # Center Window
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int(screen_width/2 - WINDOW_WIDTH/2)
        y = int(screen_height/2 - WINDOW_HEIGHT/2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")
        self.root.configure(bg="#f5e6d3") 

        # Title
        tk.Label(
            self.root, 
            text="환경설정", 
            font=("Malgun Gothic", 24, "bold"), 
            bg="#f5e6d3", 
            fg="black"
        ).pack(pady=10)

        # Notebook (Tabs)
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background="#f5e6d3")
        style.configure('TNotebook.Tab', font=("Malgun Gothic", 10, "bold"), padding=[10, 5])
        
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Tab 1: Schedule
        self.tab_schedule = tk.Frame(self.notebook, bg="#f5e6d3")
        self.notebook.add(self.tab_schedule, text="시간 설정")
        self.setup_schedule_tab()

        # Tab 2: Characters
        self.tab_characters = tk.Frame(self.notebook, bg="#f5e6d3")
        self.notebook.add(self.tab_characters, text="캐릭터 관리")
        self.setup_character_tab()

    def setup_schedule_tab(self):
        tk.Label(
            self.tab_schedule,
            text="임무 수행 시간 선택 (매 시)",
            font=("Malgun Gothic", 12),
            bg="#f5e6d3",
            fg="#555555"
        ).pack(pady=20)

        # Checkboxes
        self.vars = {}
        config_data = load_json(CONFIG_FILE, {"selected_minutes": [50]})
        current_selection = config_data.get("selected_minutes", [50])
        
        checkbox_frame = tk.Frame(self.tab_schedule, bg="#f5e6d3")
        checkbox_frame.pack(pady=10)

        minutes_options = [0, 10, 20, 30, 40, 50]
        for idx, minute in enumerate(minutes_options):
            var = tk.BooleanVar(value=(minute in current_selection))
            self.vars[minute] = var
            
            row = idx // 2
            col = idx % 2
            
            chk = tk.Checkbutton(
                checkbox_frame, 
                text=f"{minute:02d} 분", 
                variable=var, 
                font=("Malgun Gothic", 16, "bold"),
                bg="#f5e6d3",
                activebackground="#f5e6d3",
                selectcolor="white"
            )
            chk.grid(row=row, column=col, padx=20, pady=10, sticky="w")

        # Save Button
        start_btn = tk.Button(
            self.tab_schedule,
            text="시간 설정 저장",
            command=self.save_schedule,
            font=("Malgun Gothic", 14, "bold"),
            bg="#8B0000", fg="white",
            highlightbackground="#8B0000"
        )
        start_btn.pack(side="bottom", pady=40, ipadx=20, ipady=10)

    def save_schedule(self):
        new_selection = []
        for minute, var in self.vars.items():
            if var.get():
                new_selection.append(minute)
        
        if not new_selection:
            messagebox.showwarning("주의", "최소 하나의 시간은 선택해야 합니다!")
            return

        save_json(CONFIG_FILE, {"selected_minutes": sorted(new_selection)})
        messagebox.showinfo("완료", "임무 스케줄이 변경되었습니다.")

    # --- Character Tab ---
    def setup_character_tab(self):
        # List Frame
        self.char_list_frame = tk.Frame(self.tab_characters, bg="white")
        self.char_list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = tk.Scrollbar(self.char_list_frame)
        scrollbar.pack(side="right", fill="y")
        
        self.char_listbox = tk.Listbox(
            self.char_list_frame, 
            font=("Malgun Gothic", 11),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.char_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.char_listbox.yview)
        
        # Bind Double Click
        self.char_listbox.bind('<Double-1>', self.on_list_double_click)
        
        self.load_character_list()
        
        # Buttons Frame
        btn_frame = tk.Frame(self.tab_characters, bg="#f5e6d3")
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Button(btn_frame, text="캐릭터 추가", command=lambda: self.open_character_dialog(None)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="선택 삭제", command=self.delete_character).pack(side="left", padx=5)
        
        tk.Label(btn_frame, text="* 목록을 더블클릭하면 수정할 수 있습니다.", bg="#f5e6d3", fg="#666").pack(side="left", padx=10)

    def load_character_list(self):
        self.char_listbox.delete(0, tk.END)
        self.characters = load_json(CHARACTERS_FILE, [])
        for char in self.characters:
            self.char_listbox.insert(tk.END, f"{char['name']} ({char['image']})")

    def on_list_double_click(self, event):
        selection = self.char_listbox.curselection()
        if selection:
            index = selection[0]
            self.open_character_dialog(index)

    def open_character_dialog(self, index=None):
        # Mode check
        is_edit = (index is not None)
        mode_title = "캐릭터 수정" if is_edit else "캐릭터 추가"
        
        if is_edit:
            current_data = self.characters[index]
            original_image = current_data["image"]
        else:
            current_data = {}
            original_image = None

        # New Window
        top = tk.Toplevel(self.root)
        top.title(mode_title)
        top.geometry("400x650") # Height increased for image preview
        
        # Image Section
        tk.Label(top, text="1. 이미지 선택").pack(pady=5)
        
        # Preview Label
        preview_lbl = tk.Label(top, text="(이미지 미리보기)", bg="#eee", width=20, height=10)
        preview_lbl.pack(pady=5)
        
        self.img_path_var = tk.StringVar()
        if is_edit:
            self.img_path_var.set(original_image)
            
        entry_img = tk.Entry(top, textvariable=self.img_path_var, state="readonly")
        entry_img.pack(padx=20, fill="x")
        
        def update_preview(path):
            if not path:
                return
            
            # Check if it's absolute or relative to assets
            if os.path.exists(path):
                full_path = path
            else:
                full_path = os.path.join(ASSETS_DIR, path)
            
            if os.path.exists(full_path):
                try:
                    pil_img = Image.open(full_path)
                    # Resize for preview (keep aspect ratio, max height 150)
                    base_height = 150
                    h_percent = (base_height / float(pil_img.size[1]))
                    w_size = int((float(pil_img.size[0]) * float(h_percent)))
                    pil_img = pil_img.resize((w_size, base_height), Image.Resampling.LANCZOS)
                    
                    tk_img = ImageTk.PhotoImage(pil_img)
                    preview_lbl.config(image=tk_img, text="", width=0, height=0)
                    preview_lbl.image = tk_img # Keep reference
                except Exception as e:
                    preview_lbl.config(text=f"이미지 로드 실패\n{e}", image="", width=30, height=10)
            else:
                preview_lbl.config(text="이미지 없음", image="", width=30, height=10)

        def browse_and_preview():
            file_path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.gif")])
            if file_path:
                self.img_path_var.set(file_path)
                update_preview(file_path)

        tk.Button(top, text="찾아보기...", command=browse_and_preview).pack(pady=5)
        
        # Initial Preview
        if is_edit and original_image:
            update_preview(original_image)
            
        # Name
        tk.Label(top, text="2. 이름").pack(pady=5)
        name_entry = tk.Entry(top)
        name_entry.pack(padx=20, fill="x")
        if is_edit:
            name_entry.insert(0, current_data.get("name", ""))
        
        # Quotes
        tk.Label(top, text="3. 대사 (한 줄에 하나씩)").pack(pady=5)
        quotes_text = tk.Text(top, height=8)
        quotes_text.pack(padx=20, fill="x")
        if is_edit:
            quotes_joined = "\n".join(current_data.get("quotes", []))
            quotes_text.insert("1.0", quotes_joined)
        
        def save_char():
            src_path = self.img_path_var.get()
            name = name_entry.get().strip()
            raw_quotes = quotes_text.get("1.0", tk.END).strip()
            
            if not src_path or not name or not raw_quotes:
                messagebox.showwarning("에러", "모든 항목을 입력해주세요.")
                return
            
            final_filename = src_path
            
            # Image Processing
            need_copy = True
            if is_edit and src_path == original_image:
                 need_copy = False
                 final_filename = original_image
            
            if need_copy:
                 if os.path.exists(src_path):
                     ext = os.path.splitext(src_path)[1]
                     new_filename = f"custom_{int(time.time())}{ext}"
                     dst_path = os.path.join(ASSETS_DIR, new_filename)
                     try:
                        shutil.copy2(src_path, dst_path)
                        final_filename = new_filename
                     except Exception as e:
                        messagebox.showerror("에러", f"이미지 복사 실패: {e}")
                        return
                 else:
                     messagebox.showerror("에러", "이미지 파일을 찾을 수 없습니다.")
                     return

            # Construct Data
            quotes_list = [q.strip() for q in raw_quotes.split('\n') if q.strip()]
            new_char_data = {
                "image": final_filename,
                "name": name,
                "quotes": quotes_list
            }
            
            if is_edit:
                self.characters[index] = new_char_data
            else:
                self.characters.append(new_char_data)
            
            save_json(CHARACTERS_FILE, self.characters)
            
            action_text = "수정" if is_edit else "추가"
            messagebox.showinfo("완료", f"캐릭터가 {action_text}되었습니다!")
            self.load_character_list()
            top.destroy()
            
        tk.Button(top, text="저장하기", command=save_char, bg="blue", fg="white", font=("Malgun Gothic", 12, "bold")).pack(pady=20)

    # Removed old browse_image helper as it is now local function browse_and_preview


    def delete_character(self):
        sel = self.char_listbox.curselection()
        if not sel:
            return
        
        idx = sel[0]
        char = self.characters[idx]
        
        if messagebox.askyesno("삭제 확인", f"'{char['name']}' 캐릭터를 삭제하시겠습니까?"):
            del self.characters[idx]
            save_json(CHARACTERS_FILE, self.characters)
            self.load_character_list()
            messagebox.showinfo("삭제", "삭제되었습니다.")

def run_settings_standalone():
    root = tk.Tk()
    app = MissionBoardApp(root)
    root.mainloop()

if __name__ == "__main__":
    run_settings_standalone()
