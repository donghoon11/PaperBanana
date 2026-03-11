# PaperBanana × slides-grab 통합 가이드

## 개요

PaperBanana에서 생성한 figure 이미지를 프레젠테이션 슬라이드로 만들고, [slides-grab](https://github.com/vkehfdl1/slides-grab) 웹 편집기로 수정할 수 있습니다.

```
PaperBanana (이미지 생성)
    → 슬라이드 생성 (Claude Code 등으로 HTML 작성)
        → slides-grab edit (브라우저 편집)
            → PDF / PPTX 내보내기
```

슬라이드 생성은 이미지 생성과 **독립적으로** 실행됩니다.

---

## 설치

### 서브모듈 초기화

**Ubuntu / macOS:**
```bash
cd /path/to/PaperBanana
git submodule update --init
```

**Windows (cmd / PowerShell):**
```cmd
cd C:\path\to\PaperBanana
git submodule update --init
```

### Node.js 설치

Node.js 18 이상이 필요합니다.

**Ubuntu:**
```bash
# Node.js 공식 설치 (NodeSource)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# 설치 확인
node --version   # v20.x.x
npm --version    # 10.x.x
```

**Windows:**
- [nodejs.org](https://nodejs.org) 에서 LTS 버전 설치 파일(.msi) 다운로드 후 실행합니다.
- 설치 시 "Add to PATH" 옵션이 기본 체크되어 있으므로 그대로 진행합니다.
- 설치 후 cmd 또는 PowerShell을 **새로 열고** 확인합니다:
```cmd
node --version
npm --version
```

### slides-grab 의존성 설치

**Ubuntu / macOS:**
```bash
cd slides-grab
npm install
```

**Windows:**
```cmd
cd slides-grab
npm install
```

---

## 슬라이드 구성 예시 (3장)

### Slide 1 — Cover
- **배경**: 짙은 남색 (`#1a2744`)
- **내용**: 배지(PAPERBANANA · CANDIDATE N) + 큰 제목 + subtitle
- **텍스트 소스**: figure caption

### Slide 2 — Methodology
- **배경**: 흰색
- **내용**: METHOD 배지 + "Framework Overview" + 번호 카드 형태의 key points
- **텍스트 소스**: method section 핵심 문장 추출

### Slide 3 — Pipeline Figure
- **레이아웃**: 상단 텍스트 영역 + 하단 figure (21:9 가로형 최적화)
- **상단**: PIPELINE 배지 + 제목 + Stage 카드 가로 배치
- **하단**: 생성된 figure 이미지 전체 너비
- **이미지**: base64 임베드 (경로 문제 없이 편집기에서 즉시 표시)

> 슬라이드 규격: **720pt × 405pt** (16:9), Pretendard 폰트

---

## 생성 파일 구조

```
my_projects/
  {MMDD_HHMMSS}_{candidate_id}/
    slides/
      images/
        candidate_{id}.png            # 생성된 figure 원본
      slide-1.html                    # Cover 슬라이드
      slide-2.html                    # Methodology 슬라이드
      slide-3.html                    # Pipeline Figure 슬라이드
```

---

## slides-grab 사용법

### 웹 편집기 실행

**Ubuntu / macOS:**
```bash
cd slides-grab
node bin/ppt-agent.js edit --slides-dir ../my_projects/{폴더}/slides
# → http://localhost:3456 에서 브라우저 편집
```

**Windows:**
```cmd
cd slides-grab
node bin\ppt-agent.js edit --slides-dir ..\my_projects\{폴더}\slides
:: → http://localhost:3456 에서 브라우저 편집
```

편집기 기능:
- 슬라이드 미리보기 및 탐색
- 텍스트/스타일 직접 편집
- AI 채팅으로 수정 지시 (Claude, GPT 모델 지원)
- 영역 선택 후 bounding box 기반 편집

### PDF 내보내기

**Ubuntu / macOS:**
```bash
node bin/ppt-agent.js pdf \
  --slides-dir ../my_projects/{폴더}/slides \
  --output output.pdf
```

**Windows:**
```cmd
node bin\ppt-agent.js pdf --slides-dir ..\my_projects\{폴더}\slides --output output.pdf
```

### PPTX 내보내기

**Ubuntu / macOS:**
```bash
node bin/ppt-agent.js convert \
  --slides-dir ../my_projects/{폴더}/slides \
  --output output.pptx
```

**Windows:**
```cmd
node bin\ppt-agent.js convert --slides-dir ..\my_projects\{폴더}\slides --output output.pptx
```

---

## 주요 설계 결정

### 이미지 base64 임베드
slides-grab 편집기는 별도 서버에서 파일을 서빙하므로 상대경로 `images/...`가 깨질 수 있습니다. Slide 3의 figure는 base64 data URI로 HTML에 직접 임베드하여 경로 의존성을 제거했습니다. `images/` 폴더의 PNG는 PPTX 변환 등 다른 용도로 별도 보존합니다.

### 21:9 figure 레이아웃
생성된 figure의 가로세로 비율(21:9)을 고려해 Slide 3은 좌우 분할 대신 **상단 텍스트 + 하단 figure** 세로 레이아웃을 채택했습니다. Stage 카드를 가로로 배치하여 슬라이드 너비를 최대한 활용합니다.
