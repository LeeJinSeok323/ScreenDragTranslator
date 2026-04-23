# 화면 캡쳐 번역기

게임 화면의 영역을 선택해 Gemini AI로 즉시 번역하는 Windows 트레이 앱입니다.

## 주요 기능

- **화면 드래그 번역** (`Alt+Q`): 영역을 드래그하면 OCR → 자동 언어 감지 → 번역 결과 팝업
- **텍스트 입력 번역** (`Alt+E`): 입력창에 텍스트를 직접 입력해 번역, 결과는 클립보드로 복사
  - 도착어 실시간 선택: EN / ID / ES / KO
  - 출발어는 AI 자동 감지, 설정 언어가 영어면 기본 도착어를 인도네시아어로 설정
- **API 키 이중화**: Key 1이 Rate Limit에 걸리면 Key 2로 자동 전환 (무료티어 계정 2개 활용)
- **시스템 트레이 상주**: 백그라운드 실행, 트레이 아이콘에서 설정/종료
- **Windows 시작 시 자동 실행** 옵션

## 설정

| 항목 | 설명 |
|------|------|
| API Key 1 / 2 | Google AI Studio에서 발급한 Gemini API 키 |
| Gemini 모델 | 번역에 사용할 모델 선택 (기본: gemini-3.1-flash-lite-preview) |
| 언어 | UI 및 번역 도착어 기본값 (한국어 / English / Bahasa Indonesia / Español) |
| 단축키 | 화면 번역 / 텍스트 입력 번역 키 조합 자유 설정 |
| 테마 | 배경색 프리셋 + 투명도 슬라이더 |
| 결과창 닫기 | 포커스 아웃 시 자동 닫기 / X 버튼으로만 닫기 |

## 설치 및 실행

### 실행 파일 (권장)

`dist/NTKDragTranslater.exe` 를 실행하면 별도 설치 없이 바로 사용 가능합니다.

### 소스 실행

```bash
pip install -r requirements.txt
python screen_translate.py
```

### 빌드

```bash
build.bat
```

## 기술 스택

- Python 3.x
- tkinter — UI
- Google Generative AI (Gemini) — 번역 엔진
- Pillow — 화면 캡처 및 이미지 처리
- keyboard — 전역 단축키
- pystray — 시스템 트레이

## 파일 구조

```
ScreenTranslate/
├── screen_translate.py     # 앱 진입점, 메인 로직
├── core/
│   ├── config.py           # 설정 로드/저장, 프롬프트 생성
│   ├── theme.py            # 테마 색상 및 프리셋
│   └── i18n.py             # 다국어 지원
├── ui/
│   ├── settings_win.py     # 설정 창
│   ├── result_win.py       # 번역 결과 팝업
│   ├── input_win.py        # 텍스트 입력 번역 창
│   ├── overlay.py          # 드래그 선택 오버레이
│   ├── loading.py          # 번역 중 로딩 표시
│   └── widgets.py          # 공통 위젯 (HotkeyEntry 등)
├── locales/
│   ├── ko.json             # 한국어
│   ├── en.json             # English
│   ├── id.json             # Bahasa Indonesia
│   └── es.json             # Español
├── config.json             # 사용자 설정 파일 (런타임 생성)
└── requirements.txt
```

## 설정 파일 (config.json)

앱 실행 디렉터리에 자동 생성됩니다. 직접 편집하거나 설정 UI에서 변경 가능합니다.

```json
{
  "api_key": "...",
  "api_key_2": "",
  "language": "ko",
  "model": "gemini-3.1-flash-lite-preview",
  "hotkey": "alt+q",
  "hotkey_en": "alt+e",
  "close_on_focusout": true,
  "autostart": false,
  "theme_bg": "#000000",
  "theme_text": "#e8e8e8",
  "theme_card": "#1c1c1c",
  "theme_alpha": 0.95,
  "font_size": 10
}
```
