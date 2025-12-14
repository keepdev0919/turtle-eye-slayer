import schedule
import time
import sys
import os
import subprocess
import utils

# Global variable for popup process
current_popup_process = None
last_trigger_time = 0

def launch_popup():
    """Launches the health reminder popup in a separate process."""
    global last_trigger_time, current_popup_process
    
    current_time = time.time()
    # Cooldown check: Prevent multiple launches within 60 seconds
    if current_time - last_trigger_time < 60:
        print(f"Skipping alert (Cooldown active). Current: {current_time}, Last: {last_trigger_time}")
        return

    print(f"Health check triggered at {time.strftime('%H:%M:%S')}")
    
    # Auto-close previous popup if it exists
    if current_popup_process is not None:
        if current_popup_process.poll() is None: # Still running
            print("Terminating previous popup...")
            try:
                current_popup_process.terminate()
                current_popup_process.wait(timeout=1)
            except Exception as e:
                print(f"Error terminating previous popup: {e}")
    
    # Update last trigger time
    last_trigger_time = current_time
    
    # Determine python executable
    python_exe = sys.executable
    popup_script = os.path.join(utils.BASE_DIR, "src", "popup.py")
    
    # Launch without waiting (non-blocking)
    try:
        current_popup_process = subprocess.Popen([python_exe, popup_script])
    except Exception as e:
        print(f"Failed to launch popup: {e}")

def apply_schedule(minutes_list):
    """Clears and re-applies schedule based on list of minutes"""
    schedule.clear()
    print(f"Applying schedule for minutes: {minutes_list}")
    for m in minutes_list:
        minute_str = f":{m:02d}"
        schedule.every().hour.at(minute_str).do(launch_popup)
    
def get_config_mtime():
    """Returns modification time of config file"""
    if os.path.exists(utils.CONFIG_FILE):
        return os.path.getmtime(utils.CONFIG_FILE)
    return 0

def load_config():
    """Loads selected minutes from config.json"""
    default_config = [50]
    data = utils.load_json(utils.CONFIG_FILE, {"selected_minutes": default_config})
    return data.get("selected_minutes", default_config)

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
