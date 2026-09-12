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
# NOTE: The internal executable must have an ASCII name. macOS `codesign` crashes (SIGBUS)
# on a non-ASCII executable name, which leaves the bundle unsealed and Finder/`open`
# refuses to launch it. The user-facing name is restored below via Info.plist and the
# bundle folder name.
INTERNAL_NAME="DemonSlayerHealth"
DISPLAY_NAME="귀살대 건강 관리"

echo "Building consolidated application: $DISPLAY_NAME..."
python3 -m PyInstaller --noconsole --windowed $ICON_OPT \
    --osx-bundle-identifier "com.demon_slayer.health" \
    --add-data "assets:assets" \
    --add-data "data:data" \
    --name "$INTERNAL_NAME" src/dashboard.py

APP="dist/$INTERNAL_NAME.app"

# 4. Restore the Korean display name (Dock, menu bar, window switcher)
/usr/libexec/PlistBuddy -c "Set :CFBundleName $DISPLAY_NAME" "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Set :CFBundleDisplayName $DISPLAY_NAME" "$APP/Contents/Info.plist"

# 5. Re-sign (Info.plist changed) and verify the seal
codesign --force --deep --sign - "$APP"
if codesign --verify --deep --strict "$APP"; then
    echo "Code signature OK."
else
    echo "WARNING: code signature verification failed. Finder may refuse to open the app."
fi

# 6. Move to root under the user-facing name
echo "Moving app to project root..."
mv "$APP" "./$DISPLAY_NAME.app"

# 7. Final Cleanup
rm -rf build dist *.spec

echo "Build complete. '$DISPLAY_NAME.app' is ready."
