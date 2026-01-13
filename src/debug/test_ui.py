import sys
import os

# Add src directory to sys.path to allow imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)
if src_dir not in sys.path:
    sys.path.append(src_dir)

from main import launch_popup

if __name__ == "__main__":
    print("UI 테스트 모드: 팝업을 강제로 실행합니다.")
    launch_popup()
