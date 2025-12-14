#!/bin/bash

# 1. Start App (Run in background)
osacompile -o "작전 개시.app" -e '
tell application "Finder"
    set myDir to parent of (path to me) as text
end tell
set posixDir to POSIX path of myDir
do shell script "cd " & quoted form of posixDir & " && ./venv/bin/python3 src/main.py >/dev/null 2>&1 &"
'

# 2. Settings App
osacompile -o "환경설정.app" -e '
tell application "Finder"
    set myDir to parent of (path to me) as text
end tell
set posixDir to POSIX path of myDir
do shell script "cd " & quoted form of posixDir & " && ./venv/bin/python3 src/settings.py >/dev/null 2>&1 &"
'

# 3. Test UI App
osacompile -o "UI 테스트.app" -e '
tell application "Finder"
    set myDir to parent of (path to me) as text
end tell
set posixDir to POSIX path of myDir
do shell script "cd " & quoted form of posixDir & " && ./venv/bin/python3 src/debug/test_ui.py >/dev/null 2>&1 &"
'

echo "App creation complete."
