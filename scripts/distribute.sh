#!/bin/bash

# Define directories
DIST_DIR="Release_Package"
mkdir -p "$DIST_DIR"

echo "=== 1. Building Applications ==="
# Run the existing build script
./scripts/build_apps.sh

echo "=== 2. Organizing Files ==="
# 1. Access the build script's output (apps are in root now)
mv "작전 개시.app" "$DIST_DIR/"
mv "환경설정.app" "$DIST_DIR/"
mv "UI 테스트.app" "$DIST_DIR/"

# 2. Copy Resources (Assets & Data)
# We copy them so the user can edit them in the distributed folder
echo "Copying assets and data..."
cp -r "assets" "$DIST_DIR/"
cp -r "data" "$DIST_DIR/"

# Remove .DS_Store garbage if exists
find "$DIST_DIR" -name ".DS_Store" -delete

echo "=== 3. Creating Zip Archive ==="
# Zip the folder for easy sharing
ZIP_NAME="DemonSlayer_Health_Mac.zip"
rm -f "$ZIP_NAME"
zip -r "$ZIP_NAME" "$DIST_DIR"

echo "=== Done! ==="
echo "Created: $ZIP_NAME"
echo "You can send this zip file to your friends."
