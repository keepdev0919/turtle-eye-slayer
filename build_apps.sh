#!/bin/bash
# Remove old apps specific to osacompile
rm -rf "작전 개시.app" "환경설정.app" "UI 테스트.app"
rm -rf build dist *.spec

# Build "작전 개시.app"
echo "Building 작전 개시..."
./venv/bin/pyinstaller --noconsole --onefile --windowed --name "작전 개시" main.py

# Build "환경설정.app"
echo "Building 환경설정..."
./venv/bin/pyinstaller --noconsole --onefile --windowed --name "환경설정" settings.py

# Build "UI 테스트.app"
echo "Building UI 테스트..."
./venv/bin/pyinstaller --noconsole --onefile --windowed --name "UI 테스트" test_ui.py

# Move apps to root
echo "Moving apps to project root..."
mv dist/*.app .

# Clean up build artifacts
rm -rf build dist *.spec

echo "Build complete. New apps have been created."
