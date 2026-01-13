#!/bin/bash
# Consolidated build script for "귀살대 건강 관리"

# 1. Clean up old builds
echo "Cleaning up..."
rm -rf "작전 개시.app" "환경설정.app" "UI 테스트.app" "귀살대 건강 관리.app"
rm -rf build dist *.spec

# 2. Icon Handling
ICON_OPT=""
if [ -f "assets/app_icon.icns" ]; then
    ICON_OPT="--icon=assets/app_icon.icns"
    echo "Using custom icns: assets/app_icon.icns"
elif [ -f "assets/app_icon.png" ]; then
    # Try using PNG directly (some PyInstaller versions/platforms support it)
    ICON_OPT="--icon=assets/app_icon.png"
    echo "Using custom png as icon: assets/app_icon.png"
fi

# 3. Build Single App
echo "Building consolidated application: 귀살대 건강 관리..."
python3 -m PyInstaller --noconsole --windowed $ICON_OPT \
    --add-data "assets:assets" \
    --add-data "data:data" \
    --name "귀살대 건강 관리" src/dashboard.py

# 4. Move to root
echo "Moving app to project root..."
mv dist/*.app .

# 5. Final Cleanup
rm -rf build dist *.spec

echo "Build complete. '귀살대 건강 관리.app' is ready."
