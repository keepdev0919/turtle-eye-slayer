# 전집중 호흡 : 안구와 경추 (Turtle Eye Slayer)

개발자의 거북목 및 안구 건조증 방지를 위한 '귀살대(Demon Slayer)' 컨셉의 헬스 알림 프로그램입니다.

## 📖 프로젝트 개요
장시간 모니터를 보며 작업하는 개발자들을 위해, 정해진 시간마다 귀살대 캐릭터들이 등장하여 스트레칭을 독려합니다.
심플하고 세련된 다크 테마 UI를 적용하여 작업 방해를 최소화하면서도 눈길을 끄는 디자인을 제공합니다.

## ✨ 주요 기능
- **정기 알림**: 매 시 정해진 분(예: 50분)에 전체 화면 알림 팝업.
- **랜덤 캐릭터**: 렌고쿠, 시노부, 탄지로 등 12명 이상의 캐릭터와 무작위 명대사 출력.
- **심플 & 다크 테마**: 복잡한 장식을 배제한 Modern & Borderless UI.
- **사용자 커스텀**: 설정 메뉴를 통해 직접 원하는 이미지와 대사를 추가/수정/삭제 가능.
- **드래그 이동**: 타이틀바가 없어도 창을 드래그하여 이동 가능.

## 🛠 기술 스택
- **Language**: Python 3.x
- **GUI**: Tkinter (Standard Library)
- **Image Processing**: Pillow (PIL)
- **Scheduling**: schedule
- **Build**: PyInstaller (for macOS .app bundle)

## 🚀 실행 방법 (개발 환경)

### 1. 필수 라이브러리 설치
```bash
pip install -r requirements.txt
```

### 2. 실행
```bash
python main.py
```
> 실행 시 백그라운드에서 스케줄러가 동작하며, 다가오는 알림 시간에 맞춰 팝업이 뜹니다.

## 📦 앱 빌드 (macOS)
터미널에서 제공된 스크립트를 실행하여 `.app` 형태로 빌드할 수 있습니다. `PyInstaller`가 필요합니다.

```bash
sh build_apps.sh
```
빌드가 완료되면 프로젝트 루트 폴더에 다음 앱들이 생성됩니다:
- **작전 개시.app**: 메인 알림 프로그램
- **환경설정.app**: 캐릭터 및 설정 관리
- **UI 테스트.app**: UI 확인용 테스트 프로그램

## 📂 프로젝트 구조
```text
.
├── assets/             # 캐릭터 이미지 및 리소스
├── docs/               # 문서 파일
├── main.py             # 메인 프로그램 (알림 스케줄러 & 팝업)
├── settings.py         # 설정 데이터 관리 및 UI
├── build_apps.sh       # macOS 앱 빌드 스크립트
├── config.json         # 알림 시간 설정
└── characters.json     # 캐릭터 데이터
```

## ⚠️ 문제 해결
- **"응용 프로그램을 열 수 없습니다" (macOS)**: 앱 실행 시 보안 경고가 뜨는 경우 아래 명령어를 실행하세요.
  ```bash
  xattr -cr "작전 개시.app"
  ```
