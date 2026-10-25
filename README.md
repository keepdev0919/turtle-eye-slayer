# 🐾 책상 동물원 (Desk Zoo)

작업하다 보면 어느새 모니터에 코를 박고 어깨는 귀에 붙어 있죠. 책상 동물원은 정해진 시간마다 **동물 한 마리가 화면 한가운데에 나타나** 한마디 던지고, 눈 운동 하나와 목·어깨 운동 하나를 알려줍니다. 목적은 딱 하나, 피식 웃고 숨 한 번 고르고 다시 으샤으샤.

맥 전용입니다.

---

## ✨ 주요 기능
- **🐾 정기 방문**: 매 시간 정한 분(기본 00분, 30분)에 화면 정가운데 팝업
- **🦥 랜덤 동물**: 모니터 응시 고양이, 이불 속 강아지, 거북목 코알라, 득도한 카피바라 등 25마리가 무작위로 등장해 한마디
- **👀 운동 2종**: 눈 쉬게 하기 1개 + 목·어깨 펴기 1개를 매번 랜덤으로
- **🖥️ 메뉴 막대 상주**: Dock 아이콘 없이 메뉴 막대 아이콘으로만 상주. 메뉴에서 순찰 시작·중지, 미리보기, 관리실, 환경 설정, 종료
- **⚙️ 커스터마이징**: 사진과 멘트를 직접 추가·수정. 알림 시간 변경은 재시작 없이 바로 적용
- **🚀 자동 개장**: 맥 시작 시 창 없이 메뉴 막대 아이콘만 조용히 뜸

## 🛠 기술 스택
- Python 3 / Tkinter / Pillow / schedule
- pyobjc (macOS 메뉴 막대 아이콘)
- PyInstaller (macOS `.app` 번들)

사진은 Wikimedia Commons에서 가져왔고 출처는 `assets/CREDITS.md`에 있습니다.

---

## 🚀 실행 (개발자용)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 src/dashboard.py
```

## 📦 빌드 (macOS)

```bash
sh scripts/build_apps.sh
```

루트에 **`책상 동물원.app`**이 생성됩니다. 생성된 앱은 `~/Applications` 또는 `/Applications`로 옮겨서 실행하세요.

> `~/Desktop` 하위 폴더에 둔 채 Finder나 `open`으로 실행하면 macOS 보호 정책 때문에 창이 뜨지 않는 경우가 있습니다(터미널에서 바이너리를 직접 실행하면 동작해 혼동하기 쉽습니다). 앱을 옮긴 뒤 한 번 실행하면 자동 실행 경로는 스스로 갱신됩니다.
> 내부 실행 파일명은 `DeskZoo`(ASCII)입니다. 한글 실행 파일명은 macOS `codesign`을 크래시시켜 서명이 깨지므로 표시 이름만 한글로 설정합니다.

---

## 📂 프로젝트 구조
```text
.
├── src/
│   ├── dashboard.py    # 관리실 창, 스케줄러 스레드, `--popup` 인자로 팝업 프로세스 실행
│   ├── menubar.py      # macOS 메뉴 막대 아이콘 (pyobjc), Dock 숨김
│   ├── popup.py        # 동물 팝업 (대시보드가 별도 프로세스로 실행)
│   ├── settings.py     # 알림 시간 / 동물 관리 설정창
│   └── utils.py        # 경로·설정·기본 동물 데이터·자동 실행·구버전 마이그레이션
├── assets/             # 동물 사진(zoo_*.jpg), 배경, 아이콘, CREDITS.md
├── data/               # 기본 config.json / characters.json
├── scripts/            # 빌드 스크립트
└── requirements.txt
```

## ⚠️ 참고
- **사용자 데이터 위치**: `~/Library/Application Support/DeskZoo/` (설정 `data/`, 사진 `assets/`). 앱을 업데이트해도 직접 추가한 동물과 멘트는 유지되며, 기본 사진이 빠져 있으면 실행 시 자동으로 채워집니다.
- **구버전(귀살대 건강 관리)에서 업데이트**: 첫 실행 때 데이터 폴더와 자동 실행 설정을 자동으로 옮기고, 옛 기본 캐릭터는 새 동물로 교체합니다. 직접 추가했던 항목은 남습니다.
- **자동 개장**: 체크 시 `~/Library/LaunchAgents/com.tenection.deskzoo.plist`가 생성되며 다음 로그인부터 적용됩니다.
- **"응용 프로그램을 열 수 없습니다"**: 보안 정책에 걸리면 터미널에서 `xattr -cr "책상 동물원.app"`.
