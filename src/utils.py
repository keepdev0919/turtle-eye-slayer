import os
import sys
import json
import copy
import shutil
import plistlib
import time
from pathlib import Path

# Application Constants
APP_NAME = "DemonSlayerHealth"
BUNDLE_ID = "com.demon_slayer.health"
DEFAULT_MINUTES = [0, 30]

# 팝업 프로세스가 "설정 열기"를 요청할 때 사용하는 종료 코드
POPUP_EXIT_OPEN_SETTINGS = 3

# 플랫폼별 한글 글꼴 (Tk는 없는 글꼴명을 주면 기본 글꼴로 대체하지만, 명시적으로 지정)
if sys.platform == "darwin":
    FONT_FAMILY = "Apple SD Gothic Neo"
elif sys.platform == "win32":
    FONT_FAMILY = "Malgun Gothic"
else:
    FONT_FAMILY = "DejaVu Sans"

def get_resource_base_path():
    """Returns the base path for resources (source assets)."""
    if getattr(sys, 'frozen', False):
        # PyInstaller temp folder
        return sys._MEIPASS
    else:
        # Project root (one level up from src)
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_app_data_path():
    """Returns the persistent user data path (Application Support)."""
    home = Path.home()
    if sys.platform == "darwin":
        path = home / "Library" / "Application Support" / APP_NAME
    elif sys.platform == "win32":
        path = home / "AppData" / "Local" / APP_NAME
    else:
        path = home / ".local" / "share" / APP_NAME
    return str(path)

# 1. Paths
PROJECT_ROOT = get_resource_base_path()
APP_DATA_DIR = get_app_data_path()

# Determine where to READ/WRITE data
# All runtime data reading/writing happens in APP_DATA_DIR
ASSETS_DIR = os.path.join(APP_DATA_DIR, "assets")
DATA_DIR = os.path.join(APP_DATA_DIR, "data")
CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
CHARACTERS_FILE = os.path.join(DATA_DIR, "characters.json")
BUNDLED_ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")

def get_asset_path(filename):
    return os.path.join(ASSETS_DIR, filename)

# 1. 캐릭터 데이터 (기본값 - 초기 실행 시 사용)
DEFAULT_CHARACTERS = [
    {"name": "렌고쿠 쿄쥬로", "image": "rengoku.png", "quotes": ["마음을 불태워라!! 지금이 기회다!!", "힘든가? 하지만 이겨내야 기둥이 될 수 있다!", "맛있다!! 건강해지는 기분이 맛있다!!"]},
    {"name": "토키토 무이치로", "image": "muichiro.png", "quotes": ["어라? 방금 뭐 하려고 했더라.. 아, 운동.", "구름처럼 둥둥 떠다니는 목 디스크.. 싫지?", "빨리 해. 기억에서 잊혀지기 전에."]},
    {"name": "우즈이 텐겐", "image": "tengen.png", "quotes": ["화려하게 움직여라!! 수수한 자세는 질색이다!", "축제다!! 근육이 기뻐하는 축제야!!", "내 아내들도 너보단 자세가 좋을 거다!"]},
    {"name": "코쵸우 시노부", "image": "shinobu.png", "quotes": ["어라~ 몸이 꽤 뻣뻣하시네요. 독이라도 놔드릴까요?", "웃으면서 운동해요~ 화내면 주름 생겨요.", "부디 제발, 제 말 좀 들어주세요."]},
    {"name": "아카자", "image": "akaza.png", "quotes": ["약한 자는 싫어한다.. 자세가 구부정한 자는 더 싫다!", "너도 도깨비가 되겠다고 말해라! (건강해지겠다고!)", "파괴살! 라운드 숄더 멸살!"]},
    {"name": "이구로 오바나이", "image": "obanai.png", "quotes": ["신용할 수 없군.. 그따위 자세로 코딩이라니.", "내 뱀이 너를 조르기 전에 스트레칭해라.", "쥐구멍에라도 숨고 싶은 자세군."]},
    {"name": "토미오카 기유", "image": "giyu.png", "quotes": ["나는 너희들과 다르다... (자세가 너무 좋다)", "녹슬어 버리면 베이지 않는다. 몸도 마찬가지다.", "집중해라. 그딴 자세로는 아무것도 지킬 수 없다."]},
    {"name": "히메지마 교메이", "image": "gyomei.png", "quotes": ["나무아미타불... 어찌하여 저런 구부정한 자세를...", "가여운 아이로구나. 스트레칭을 가르쳐주마.", "바른 자세는 바른 마음에서 나오는 법."]},
    {"name": "하시비라 이노스케", "image": "inosuke.png", "quotes": ["저돌맹진!! 스트레칭도 저돌맹진이다!!", "내 유연함을 봐라! 너는 못하겠지!", "산의 왕은 거북목 따위 걸리지 않아!"]},
    {"name": "칸로지 미츠리", "image": "mitsuri.png", "quotes": ["꺄아~ 뻣뻣한 모습도 귀여워! 하지만 펴면 더 멋질거야!", "사랑의 호흡! 척추 펴기!", "유연한 사람이 강한 사람이에요♡"]},
    {"name": "시나즈가와 사네미", "image": "sanemi.png", "quotes": ["어이, 그게 스트레칭이냐? 장난해?", "비실비실한 놈들은 질색이다. 똑바로 펴!", "오니보다 네 자세가 더 흉측하군."]},
    {"name": "카마도 탄지로", "image": "tanjiro.png", "quotes": ["장남이니까 참을 수 있어! 스트레칭의 고통도!", "전집중 호흡! 바른 자세의 호흡!", "네즈코도 따라할 수 있는 쉬운 운동이야!"]},
    {"name": "아카츠마 젠이츠", "image": "zenitsu.png", "quotes": ["으아악! 아파! 근육이 찢어질 것 같아!!", "이거 안 하면 죽는거야? 거북목으로 죽는거냐고!!", "네즈코 쨩~ 봐봐! 나 운동하는 거 봐봐!"]}
]

# 2. 운동 데이터 (Neck / Eye 카테고리 분리)
exercise_data = [
    # [Category: Neck]
    {
        "category": "Neck",
        "title": "🐢 제1형 : 턱 집어넣기",
        "description": "1. 허리를 펴고 검지를 턱에 댄다.\n2. 턱을 수평으로 뒤로 밀어 '투턱'을 만든다.\n3. 뒷목이 당기는 느낌으로 10초 버텨!"
    },
    {
        "category": "Neck",
        "title": "🦋 제2형 : 날개뼈 조이기",
        "description": "1. 팔을 양옆으로 벌려 'W'자를 만든다.\n2. 날개뼈가 서로 닿는 느낌으로 등 뒤를 꽉 조인다.\n3. 가슴을 천장으로 발사하며 10초 유지!"
    },
    {
        "category": "Neck",
        "title": "🪵 제3형 : 승모근 늘리기",
        "description": "1. 한 손으로 의자 밑을 잡아 어깨를 고정한다.\n2. 반대 손으로 머리를 잡고 옆으로 지그시 당긴다.\n3. 목 옆선이 찢어지는 시원함을 느껴라. (좌우 10초씩)"
    },
    {
        "category": "Neck",
        "title": "🌪️ 제4형 : 천장 뚫기",
        "description": "1. 양손을 쇄골(목 아래 뼈) 위에 포개서 얹고 꾹 누른다.\n2. 손으로 피부를 고정한 채, 천천히 고개를 뒤로 젖혀 천장을 본다.\n3. 입을 다물고 목 앞쪽이 팽팽하게 당기는 걸 느끼며 10초 유지!"
    },
    # [Category: Eye]
    {
        "category": "Eye",
        "title": "👁️ 제1형 : 암전과 온기",
        "description": "1. 양손바닥을 싹싹 비벼서 뜨겁게 마찰열을 낸다.\n2. 따뜻해진 손바닥을 오목하게 만들어 눈을 덮는다 (누르지 마!).\n3. 빛을 완벽히 차단하고 칠흑 같은 어둠 속에서 10초 휴식."
    },
    {
        "category": "Eye",
        "title": "👀 제2형 : 극한의 눈 굴리기",
        "description": "1. 고개는 고정. 눈동자만 움직인다.\n2. 위 -> 오른쪽 -> 아래 -> 왼쪽 순서로 극한까지 굴려라.\n3. 시계방향 5회, 반대방향 5회 실시."
    },
    {
        "category": "Eye",
        "title": "⚡ 제3형 : 강력 깜빡임",
        "description": "1. 눈을 4초간 '꽉!!' 감는다. (눈물샘을 짜낸다는 느낌)\n2. 눈을 '팟!' 하고 크게 뜬다.\n3. 5번 반복. 안구 건조증에 직빵이다."
    },
    {
        "category": "Eye",
        "title": "🎱 제4형 : 무한대(∞) 그리기",
        "description": "1. 눈앞에 거대한 숫자 8이 누워있다고 상상한다.\n2. 눈동자로 그 선을 따라 천천히 움직인다.\n3. 멍청해 보이지만 초점 조절 근육 푸는 데 최고다."
    }
]

def load_json(filepath, default_value):
    """Reads a JSON file. Returns default_value if the file is missing or unreadable."""
    if not os.path.exists(filepath):
        return default_value
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON ({filepath}): {e}")
        return default_value

def save_json(filepath, data):
    try:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving JSON: {e}")

def sync_default_assets():
    """Copies bundled default images that are missing from the user's assets folder.

    Existing files are never overwritten, so user-modified images are preserved.
    This also restores images the user deleted and adds images introduced by app updates.
    """
    os.makedirs(ASSETS_DIR, exist_ok=True)
    if not os.path.exists(BUNDLED_ASSETS_DIR):
        print(f"Warning: Source assets not found at {BUNDLED_ASSETS_DIR}")
        return
    for item in os.listdir(BUNDLED_ASSETS_DIR):
        if not item.lower().endswith(".png"):
            continue
        dst = os.path.join(ASSETS_DIR, item)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(BUNDLED_ASSETS_DIR, item), dst)

def initialize_app_data():
    """Checks and initializes the Application Support folder."""
    print(f"Checking data integrity in: {APP_DATA_DIR}")

    sync_default_assets()
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(CHARACTERS_FILE):
        print("Characters file missing. Initializing...")
        save_json(CHARACTERS_FILE, DEFAULT_CHARACTERS)

    if not os.path.exists(CONFIG_FILE):
        print("Config file missing. Initializing...")
        save_json(CONFIG_FILE, {"selected_minutes": list(DEFAULT_MINUTES)})

def get_default_characters():
    """Returns a fresh copy so callers can never mutate the module-level defaults."""
    return copy.deepcopy(DEFAULT_CHARACTERS)

def get_character_data():
    """Loads the user's character list.

    - Missing file  -> defaults are written and returned.
    - Corrupt file  -> the broken file is backed up (never silently overwritten), then defaults are written.
    - Empty list    -> defaults are returned without touching the user's file.
    """
    if not os.path.exists(CHARACTERS_FILE):
        save_json(CHARACTERS_FILE, DEFAULT_CHARACTERS)
        return get_default_characters()

    try:
        with open(CHARACTERS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("characters.json must contain a list")
    except Exception as e:
        backup = f"{CHARACTERS_FILE}.corrupt-{int(time.time())}"
        print(f"characters.json is unreadable ({e}). Backing up to {backup} and restoring defaults.")
        try:
            shutil.move(CHARACTERS_FILE, backup)
        except Exception as move_err:
            print(f"Backup failed: {move_err}")
        save_json(CHARACTERS_FILE, DEFAULT_CHARACTERS)
        return get_default_characters()

    if not data:
        return get_default_characters()
    return data

def get_schedule_minutes():
    """Returns the list of minutes (0-59) at which the reminder fires every hour."""
    config = load_json(CONFIG_FILE, {"selected_minutes": list(DEFAULT_MINUTES)})
    minutes = config.get("selected_minutes") if isinstance(config, dict) else None
    if not isinstance(minutes, list):
        return list(DEFAULT_MINUTES)
    valid = sorted({int(m) for m in minutes if isinstance(m, int) and 0 <= m < 60})
    return valid or list(DEFAULT_MINUTES)

def get_config_mtime():
    """Modification time of config.json (0 if missing). Used to detect schedule changes."""
    try:
        return os.path.getmtime(CONFIG_FILE)
    except OSError:
        return 0

def get_exercise_data():
    return exercise_data

def get_random_exercises():
    """Returns one random neck and one random eye exercise."""
    import random

    neck_exercises = [ex for ex in exercise_data if ex["category"] == "Neck"]
    eye_exercises = [ex for ex in exercise_data if ex["category"] == "Eye"]

    # Fallback if empty (though lists are hardcoded above)
    selected_neck = random.choice(neck_exercises) if neck_exercises else None
    selected_eye = random.choice(eye_exercises) if eye_exercises else None

    return {
        "neck": selected_neck,
        "eye": selected_eye
    }

# ==========================================
# Auto-Launch (Login Item) Logic
# ==========================================
LAUNCH_AGENT_Label = BUNDLE_ID
LAUNCH_AGENT_DIR = os.path.join(Path.home(), "Library", "LaunchAgents")
LAUNCH_AGENT_PATH = os.path.join(LAUNCH_AGENT_DIR, f"{LAUNCH_AGENT_Label}.plist")

def _autolaunch_program_args():
    """Command line launchd should run to start the dashboard."""
    if getattr(sys, 'frozen', False):
        # Production: the bundled executable itself (inside the .app)
        return [sys.executable]
    # Development: python + dashboard.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.py")
    return [sys.executable, script_path]

def _read_autolaunch_args():
    try:
        with open(LAUNCH_AGENT_PATH, "rb") as f:
            return plistlib.load(f).get("ProgramArguments")
    except Exception:
        return None

def get_autolaunch_status():
    """Returns True if the plist exists."""
    return os.path.exists(LAUNCH_AGENT_PATH)

def set_autolaunch(enable: bool):
    """Creates or deletes the Launch Agent plist. Takes effect from the next login."""
    if enable:
        plist = {
            "Label": LAUNCH_AGENT_Label,
            "ProgramArguments": _autolaunch_program_args(),
            "RunAtLoad": True,
        }
        try:
            os.makedirs(LAUNCH_AGENT_DIR, exist_ok=True)
            with open(LAUNCH_AGENT_PATH, "wb") as f:
                plistlib.dump(plist, f)
            print(f"Auto-launch enabled. Plist created at {LAUNCH_AGENT_PATH}")
        except Exception as e:
            print(f"Failed to enable auto-launch: {e}")
    else:
        if os.path.exists(LAUNCH_AGENT_PATH):
            try:
                os.remove(LAUNCH_AGENT_PATH)
                print("Auto-launch disabled. Plist removed.")
            except Exception as e:
                print(f"Failed to disable auto-launch: {e}")

def sync_autolaunch():
    """If auto-launch is enabled but the plist points at an old location (the app was moved),
    rewrite it so it keeps working. Returns the current enabled state."""
    if not get_autolaunch_status():
        return False
    if _read_autolaunch_args() != _autolaunch_program_args():
        print("Auto-launch plist is stale (app moved?). Rewriting...")
        set_autolaunch(True)
    return True
