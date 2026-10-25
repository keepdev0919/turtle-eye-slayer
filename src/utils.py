import os
import sys
import json
import copy
import shutil
import plistlib
import time
from pathlib import Path

# Application Constants
APP_NAME = "DeskZoo"
APP_DISPLAY_NAME = "책상 동물원"
BUNDLE_ID = "com.tenection.deskzoo"
DEFAULT_MINUTES = [0, 30]

# 이전 컨셉(귀살대 건강 관리)에서 넘어온 사용자 데이터를 옮기기 위한 식별자
LEGACY_APP_NAME = "DemonSlayerHealth"
LEGACY_BUNDLE_ID = "com.demon_slayer.health"
LEGACY_DEFAULT_IMAGES = {
    "rengoku.png", "muichiro.png", "tengen.png", "shinobu.png", "akaza.png", "obanai.png", "giyu.png",
    "gyomei.png", "inosuke.png", "mitsuri.png", "sanemi.png", "tanjiro.png", "zenitsu.png",
    "bg_dojo.png", "btn_main.png", "btn_sub.png", "sign_wood.png",
}
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif")

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

# 1. 동물 데이터 (기본값 - 초기 실행 시 사용). 사진 출처는 assets/CREDITS.md
def _a(name, image, *quotes):
    return {"name": name, "image": image, "quotes": list(quotes)}

DEFAULT_CHARACTERS = [
    _a("모니터 응시 고양이", "zoo_monitor_cat.jpg",
       "지금 모니터랑 거리 20cm. 내가 다 봤다.",
       "화면 속에 답 없다. 눈 떼고 멀리 봐.",
       "너 그 자세로 세 시간째야. 고개 들어."),
    _a("책상 박스 고양이", "zoo_box_cat.jpg",
       "박스에 들어가서 잠깐 쉬어. 나처럼.",
       "일은 도망 안 가. 근데 네 목은 간다.",
       "이 박스 비켜달라고? 어깨부터 펴고 말해."),
    _a("노트북 검수 고양이", "zoo_laptop_cat.jpg",
       "코드 리뷰 왔다. 1번: 거북목.",
       "이 커밋 통과. 네 자세는 반려.",
       "화면 그만 보고 나 좀 봐. 더 예뻐."),
    _a("퇴근 직전 고양이", "zoo_printer_cat.jpg",
       "이 표정이 지금 네 표정이다.",
       "다 녹았네. 기지개 한 번만 켜자.",
       "퇴근하고 싶지? 일단 눈부터 감아 10초."),
    _a("키보드 점령 고양이", "zoo_keyboard_cat.jpg",
       "키보드는 내가 맡는다. 너는 스트레칭.",
       "타이핑 중단. 이건 명령이다.",
       "손 치워. 어깨 돌리고 와서 다시 쳐."),
    _a("커피 감독관 고양이", "zoo_coffee_cat.jpg",
       "커피가 피로를 풀어주진 않는다. 목 돌려.",
       "오늘 몇 잔째야? 물 한 컵 추가.",
       "눈 밑 다크서클 보인다. 멀리 봐."),
    _a("소리 지르는 고양이", "zoo_yelling_cat.jpg",
       "야!!! 어깨!!! 내려!!!",
       "스트레칭 안 하면 계속 소리 지른다.",
       "지금 네 승모근이 이렇게 비명 중이다."),
    _a("하품 고양이", "zoo_yawn_cat.jpg",
       "하품 한 번 크게. 턱 풀린다.",
       "졸린 거 아니고 뇌에 산소 부족이야.",
       "입 크게 벌리고 쭉. 창피해도 효과 좋음."),
    _a("스트레칭 교과서 표범", "zoo_leopard.jpg",
       "스트레칭은 이렇게 하는 거다. 따라 해.",
       "등 쭉, 엉덩이 뒤로, 10초. 표범식.",
       "유연한 놈이 오래 간다. 사냥도 코딩도."),
    _a("기절한 고양이", "zoo_window_cat.jpg",
       "이게 네 척추 현재 상태.",
       "녹아내리기 전에 일어나서 한 바퀴.",
       "이렇게 누워서 10초. 진짜로. 효과 있음."),
    _a("이불 속 강아지", "zoo_bed_dog.jpg",
       "오늘 할 일 다 했다. 아, 아니구나. 그래도 쉬어.",
       "이불이 부른다. 못 가면 눈이라도 감아.",
       "퇴근 후의 나. 지금은 어깨만 좀 풀자."),
    _a("뒤집어진 강아지", "zoo_upside_dog.jpg",
       "완전 뻗음. 너도 등받이에 기대 봐.",
       "세상 편하지? 너도 10초만 이렇게.",
       "고개 뒤로 젖히고 천장 봐. 목 앞쪽 시원함."),
    _a("거북목 코알라", "zoo_koala.jpg",
       "이게 거울이다. 턱 당겨.",
       "코알라도 아는 걸 왜 몰라. 허리 펴.",
       "하루 20시간 자는 나도 자세는 챙긴다."),
    _a("쿼카", "zoo_quokka.jpg",
       "웃어. 입꼬리만 올려도 얼굴 근육 풀린다.",
       "세상에서 제일 행복한 동물이 시킨다. 스트레칭.",
       "일 잘 되고 있어. 잠깐 쉬어도 돼."),
    _a("나무늘보", "zoo_sloth.jpg",
       "천천히 해도 돼. 근데 목은 지금 펴.",
       "느리게 숨 쉬어. 4초 들이쉬고 6초 내쉬고.",
       "급할수록 한 박자 쉬는 게 빠르다."),
    _a("눈치 보는 퍼그", "zoo_pug_blanket.jpg",
       "...어깨 올라간 거 알지?",
       "나도 안다. 이 알림 귀찮은 거. 그래도 해.",
       "운동 안 하면 이 눈으로 계속 본다."),
    _a("바닥에 녹은 퍼그", "zoo_pug_floor.jpg",
       "지금 네 집중력 상태.",
       "이럴 땐 일어나서 물 한 잔. 진짜 효과 있음.",
       "바닥이 편하지? 네 허리는 아니다."),
    _a("선글라스 개", "zoo_sunglass_dog.jpg",
       "눈 쉬는 중. 너도 20초만 먼 데 봐.",
       "쿨하게 쉬자. 모니터 밝기도 좀 낮추고.",
       "눈 깜빡인 지 얼마나 됐어? 다섯 번 세게."),
    _a("버그 발견 고양이", "zoo_shocked_cat.jpg",
       "방금 네 자세 보고 놀란 표정이다.",
       "버그보다 무서운 건 거북목이다.",
       "눈 이렇게 크게 뜨고 위아래좌우. 안구 운동."),
    _a("득도한 카피바라", "zoo_capybara.jpg",
       "급할 거 없다. 숨 한 번 쉬고 가자.",
       "모든 버그는 결국 고쳐진다. 어깨 내려.",
       "물속에서 명상 중. 너는 눈 감고 10초."),
    _a("온천 원숭이", "zoo_onsen_monkey.jpg",
       "목욕탕 생각나지? 지금은 목 돌리기로 대신.",
       "따뜻한 손바닥 비벼서 눈 위에 올려 봐.",
       "쉬는 것도 실력이다. 원숭이도 안다."),
    _a("세수하는 햄스터", "zoo_hamster.jpg",
       "눈 비비지 말고 깜빡여. 세게 다섯 번.",
       "볼에 저장된 간식처럼 피로도 쌓인다. 비워.",
       "작은 손으로도 세수는 한다. 너도 해."),
    _a("감시하는 부엉이", "zoo_owl.jpg",
       "목 270도 돌아가는 나도 스트레칭한다.",
       "지켜보고 있다. 턱 당기고 등 펴.",
       "눈 크게 뜨고 멀리. 부엉이식 시력 보호."),
    _a("모래 위 물개", "zoo_seal.jpg",
       "오늘의 나. 그래도 등은 펴고 누웠다.",
       "배 깔고 상체 들기. 물개 자세 10초.",
       "물개도 쉬는데 네가 왜 안 쉬어."),
    _a("화상회의 강아지", "zoo_laptop_dog.jpg",
       "회의 중이라고? 카메라 끄고 어깨 돌려.",
       "노트북 높이 올려. 눈높이. 나처럼.",
       "집중 끝났으면 시선 멀리. 창밖 봐."),
]

# 2. 운동 데이터 (Neck / Eye)
exercise_data = [
    {"category": "Neck", "title": "🐢 턱 당기기",
     "description": "1. 허리 펴고 검지를 턱에 댄다.\n2. 턱을 수평으로 뒤로 민다. 투턱 만들기.\n3. 뒷목이 당기는 느낌으로 10초."},
    {"category": "Neck", "title": "🦋 날개뼈 모으기",
     "description": "1. 팔을 옆으로 벌려 W자.\n2. 날개뼈끼리 닿는 느낌으로 등 뒤를 꽉.\n3. 가슴을 천장으로 열고 10초."},
    {"category": "Neck", "title": "🪑 승모근 늘리기",
     "description": "1. 한 손으로 의자 밑을 잡아 어깨 고정.\n2. 반대 손으로 머리를 옆으로 지그시.\n3. 목 옆선이 늘어나는 느낌. 좌우 10초씩."},
    {"category": "Neck", "title": "☁️ 천장 보기",
     "description": "1. 양손을 쇄골 위에 포개 꾹 누른다.\n2. 피부를 고정한 채 천천히 고개를 뒤로.\n3. 입 다물고 목 앞쪽이 팽팽해지면 10초."},
    {"category": "Eye", "title": "🤲 손바닥 찜질",
     "description": "1. 손바닥을 싹싹 비벼 따뜻하게.\n2. 오목하게 만들어 눈을 덮는다. 누르지 말기.\n3. 완전한 어둠 속에서 10초 휴식."},
    {"category": "Eye", "title": "👀 눈알 굴리기",
     "description": "1. 고개는 고정, 눈동자만 움직인다.\n2. 위, 오른쪽, 아래, 왼쪽 끝까지.\n3. 시계방향 5회, 반대 5회."},
    {"category": "Eye", "title": "⚡ 세게 깜빡이기",
     "description": "1. 눈을 4초간 꽉 감는다.\n2. 크게 뜬다.\n3. 5번 반복. 안구 건조에 바로 효과."},
    {"category": "Eye", "title": "♾️ 무한대 그리기",
     "description": "1. 눈앞에 누운 8자가 있다고 상상.\n2. 눈동자로 그 선을 천천히 따라간다.\n3. 좀 멍청해 보여도 초점 근육 푸는 데 최고."},
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
        if not item.lower().endswith(IMAGE_EXTS):
            continue
        dst = os.path.join(ASSETS_DIR, item)
        if not os.path.exists(dst):
            shutil.copy2(os.path.join(BUNDLED_ASSETS_DIR, item), dst)

def migrate_legacy_data():
    """One-time migration from the old '귀살대 건강 관리' install.

    - Moves the old Application Support folder to the new name.
    - Drops the old default characters (keeps user-added custom_* ones) and their images.
    - Replaces the old LaunchAgent plist with the new label, preserving the enabled state.
    """
    legacy_dir = os.path.join(os.path.dirname(APP_DATA_DIR), LEGACY_APP_NAME)
    if os.path.isdir(legacy_dir) and not os.path.exists(APP_DATA_DIR):
        print(f"Migrating data folder {legacy_dir} -> {APP_DATA_DIR}")
        try:
            shutil.move(legacy_dir, APP_DATA_DIR)
        except Exception as e:
            print(f"Data folder migration failed: {e}")

    # old default characters / images
    data = load_json(CHARACTERS_FILE, None)
    if isinstance(data, list) and any(c.get("image") in LEGACY_DEFAULT_IMAGES for c in data if isinstance(c, dict)):
        kept = [c for c in data if isinstance(c, dict) and c.get("image") not in LEGACY_DEFAULT_IMAGES]
        print(f"Replacing {len(data) - len(kept)} legacy characters with the new defaults (kept {len(kept)} custom).")
        save_json(CHARACTERS_FILE, get_default_characters() + kept)
    if os.path.isdir(ASSETS_DIR):
        for f in os.listdir(ASSETS_DIR):
            if f in LEGACY_DEFAULT_IMAGES:
                try:
                    os.remove(os.path.join(ASSETS_DIR, f))
                except OSError:
                    pass

    # old LaunchAgent label
    legacy_plist = os.path.join(LAUNCH_AGENT_DIR, f"{LEGACY_BUNDLE_ID}.plist")
    if os.path.exists(legacy_plist):
        print("Replacing legacy LaunchAgent with the new label.")
        try:
            os.remove(legacy_plist)
        except OSError as e:
            print(f"Could not remove legacy plist: {e}")
        set_autolaunch(True)

def initialize_app_data():
    """Checks and initializes the Application Support folder."""
    print(f"Checking data integrity in: {APP_DATA_DIR}")

    migrate_legacy_data()
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
    # --hidden: start with only the menu bar icon (no dashboard window) at login
    if getattr(sys, 'frozen', False):
        # Production: the bundled executable itself (inside the .app)
        return [sys.executable, "--hidden"]
    # Development: python + dashboard.py
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.py")
    return [sys.executable, script_path, "--hidden"]

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
