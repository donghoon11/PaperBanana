# <div align="center">PaperBanana</div>
<div align="center">Dawei Zhu, Rui Meng, Yale Song, Xiyu Wei, Sujian Li, Tomas Pfister and Jinsung yoon
<br><br></div>

</div>
<div align="center">
<a href="https://huggingface.co/papers/2601.23265"><img src="assets/paper-page-xl.svg" alt="Paper page on HF"></a>
<a href="https://huggingface.co/datasets/dwzhu/PaperBananaBench"><img src="assets/dataset-on-hf-xl.svg" alt="Dataset on HF"></a>
</div>

---

**PaperBanana**는 논문의 method section과 caption을 입력하면, AI 에이전트 파이프라인이 자동으로 학술 논문용 figure를 생성해주는 프레임워크입니다.

![Examples](assets/teaser_figure.jpg)

**파이프라인 구조:** Retriever → Planner → Stylist → Visualizer → Critic (반복 개선)

![PaperBanana Framework](assets/method_diagram.png)

> 원본 프로젝트의 상세 설명, CLI 사용법, 프로젝트 구조 등은 [README_ORIGINAL.md](README_ORIGINAL.md)를 참고하세요.

---

## Quick Start (Windows 기준)

> Ubuntu/macOS 사용자는 [아래 섹션](#ubuntumacos-사용자)을 참고하세요.

### Step 1. Google Cloud 프로젝트 활성화

PaperBanana는 Google Gemini를 **Vertex AI**를 통해 호출합니다. 먼저 Google Cloud에서 프로젝트를 준비합니다.

1. [Google Cloud Console](https://console.cloud.google.com)에 접속하여 **무료 체험**을 시작합니다.
2. **$300 무료 크레딧**이 제공되며, **"My First Project"** 가 자동 생성되고 결제 계정이 연결됩니다.
3. 이 **"My First Project"** 를 그대로 사용합니다. **프로젝트 ID를 기록해 두세요** (이후 모든 단계에서 동일한 프로젝트를 사용합니다).

### Step 2. Google Cloud SDK 설치 및 로그인

1. [GoogleCloudSDKInstaller.exe](https://cloud.google.com/sdk/docs/install#windows) 다운로드 후 기본 옵션으로 설치합니다.
2. 설치 완료 후 시작 메뉴에서 **"Google Cloud SDK Shell"** 을 실행합니다.
   - 일반 cmd/PowerShell에서는 PATH가 적용되지 않아 오류가 발생할 수 있습니다.
3. 아래 명령어를 순서대로 실행합니다:

```cmd
:: 1. Google 계정 로그인 (브라우저가 열립니다)
gcloud auth login

:: 2. Application Default Credentials 설정
gcloud auth application-default login

:: 3. Step 1에서 생성된 프로젝트 설정 (프로젝트 ID를 입력하세요)
gcloud config set project YOUR_PROJECT_ID
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

:: 4. 환경변수 설정
set GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
```

> **주의**: 여기서 설정한 프로젝트 ID를 Step 4에서 API Key 발급 시에도 **동일하게** 사용해야 합니다. 프로젝트가 다르면 `Permission Denied` 에러가 발생합니다.

### Step 3. PaperBanana 설치

**PowerShell을 새로 열고** 아래 명령어를 순서대로 실행합니다.

```powershell
# 1. 저장소 클론
git clone https://github.com/donghoon11/PaperBanana.git
cd PaperBanana

# 2. uv 설치 (Python 패키지 매니저)
pip install uv

# 3. 가상환경 생성 및 활성화
uv venv
.venv\Scripts\activate

# 4. Python 3.12 설치
uv python install 3.12

# 5. 의존성 설치
uv pip install -r requirements.txt
```

### Step 4. API Key & 설정 파일

#### 4-1. Google AI Studio에서 API Key 발급

1. [aistudio.google.com](https://aistudio.google.com) 에 로그인합니다.
2. 좌측 하단 **"Get API key"** > **"키 만들기(Create API key)"** 클릭합니다.
3. **"가져온 프로젝트 선택"** 드롭다운에서 **Step 2에서 설정한 프로젝트**를 선택합니다.
   - 프로젝트 목록에 여러 개가 보일 수 있습니다 (예: Gemini Project1, My First Project 등).
   - **반드시 Step 2에서 결제 계정을 연결한 프로젝트를 선택하세요.**
4. 생성된 API Key를 복사합니다 (형식: `AIza...`).

#### 4-2. 설정 파일 생성

```powershell
copy configs\model_config.template.yaml configs\model_config.yaml
```

`configs\model_config.yaml`을 메모장 등으로 열어 아래 값을 입력합니다:

```yaml
# Default Models
defaults:
  model_name: "gemini-3.1-pro-preview"
  image_model_name: "gemini-3.1-flash-image-preview"

# API Keys
api_keys:
  google_api_key: "AIzaSy..."   # ← 발급받은 API Key 붙여넣기
  openai_api_key: ""
  anthropic_api_key: ""

# Google Cloud / Vertex AI
google_cloud:
  project_id: "YOUR_PROJECT_ID"  # ← Step 2에서 설정한 프로젝트 ID
  location: "global"
```

### Step 5. 데이터셋 다운로드

PaperBananaBench 데이터셋을 다운로드합니다. (선택사항이지만, Retriever Agent의 few-shot 학습에 필요합니다)

```powershell
# 반드시 PaperBanana 폴더 안에서 실행하세요
if (-not (Test-Path "data\PaperBananaBench")) { mkdir data\PaperBananaBench }

python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='dwzhu/PaperBananaBench', repo_type='dataset', local_dir='data/PaperBananaBench')"

# 다운로드 확인
dir data\PaperBananaBench
# diagram\  plot\  두 폴더가 보여야 합니다
```

다운로드 후 예상 경로 구조:
```
PaperBanana\
└── data\
    └── PaperBananaBench\
        ├── diagram\
        │   ├── images\
        │   ├── test.json
        │   └── ref.json
        └── plot\
            ├── images\
            ├── test.json
            └── ref.json
```

### Step 6. 실행

```powershell
streamlit run demo.py
```

브라우저에서 `http://localhost:8501` 이 자동으로 열립니다.
터미널에 `Initialized Gemini Client with Vertex AI (project: ...)` 메시지가 출력되면 정상입니다.

### Step 7. 첫 테스트 실행

처음에는 빠른 확인을 위해 최소 설정으로 테스트합니다.

1. **좌측 사이드바에서 설정**:
   - Pipeline Mode: `demo_planner_critic`
   - Number of Candidates: `1`
   - Max Critic Rounds: `1`
   - Aspect Ratio: `16:9`
   - Retrieval Setting: `auto`

2. **입력 영역에서**:
   - "Load Example" 버튼을 클릭하여 예제를 불러옵니다.
   - Method Content와 Figure Caption이 자동으로 채워집니다.

3. **"Generate Candidates"** 버튼 클릭

4. **결과 확인**:
   - 생성된 diagram이 화면에 표시됩니다.
   - Evolution Timeline에서 Planner → Visualizer → Critic 각 단계의 결과를 확인할 수 있습니다.
   - 이미지를 다운로드할 수 있습니다.

### Step 8. 나만의 논문 Figure 생성

테스트가 성공했으면, 이제 본인의 논문 figure를 생성합니다.

1. **Method Content**: 논문의 method section 내용을 Markdown 형식으로 붙여넣습니다.
2. **Figure Caption**: 생성할 figure의 caption을 입력합니다 (예: "Figure 1: Overview of the proposed framework").
3. **설정 조정**:
   - Number of Candidates를 `5~10`으로 늘려 더 많은 후보를 생성합니다.
   - Max Critic Rounds를 `3`으로 늘려 반복 개선 품질을 높입니다.
   - Pipeline Mode를 `demo_full`로 변경하면 Stylist 단계가 추가되어 더 정교한 결과를 얻을 수 있습니다.
4. **Refine Image 탭**: 생성된 후보 중 마음에 드는 이미지를 업로드하고, 수정 지시를 입력하거나 2K/4K 고해상도로 변환할 수 있습니다.

---

## Troubleshooting

| 증상 | 해결 |
|------|------|
| `Permission Denied` / `Project not found` | AI Studio API Key의 프로젝트와 `gcloud config set project`의 프로젝트 ID가 일치하는지 확인. `gcloud projects list`로 확인 |
| `Permission denied: adc.json` | 일반 cmd 대신 **Google Cloud SDK Shell** 에서 gcloud 명령어 실행 |
| `quota exceeded` / `API not enabled` | `gcloud auth application-default set-quota-project YOUR_PROJECT_ID` 실행 |
| `streamlit: command not found` | 가상환경 활성화 확인: `.venv\Scripts\activate` |
| `ModuleNotFoundError` | `uv pip install -r requirements.txt` 재실행 |
| `Warning: Could not initialize Anthropic/OpenAI Client` | Gemini만 사용하는 경우 정상. 무시 가능 |

---

<details>
<summary><strong>Ubuntu/macOS 사용자</strong></summary>

### gcloud CLI 설치 및 인증

```bash
# gcloud CLI 설치: https://cloud.google.com/sdk/docs/install 참고
# 설치 후:
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
```

### PaperBanana 설치

```bash
git clone https://github.com/donghoon11/PaperBanana.git
cd PaperBanana

pip install uv
uv venv && source .venv/bin/activate
uv python install 3.12
uv pip install -r requirements.txt
```

### 설정 파일 & 데이터셋

```bash
cp configs/model_config.template.yaml configs/model_config.yaml
# configs/model_config.yaml 편집: google_api_key, project_id 입력

mkdir -p data/PaperBananaBench
python -c "
from huggingface_hub import snapshot_download
snapshot_download(repo_id='dwzhu/PaperBananaBench', repo_type='dataset', local_dir='data/PaperBananaBench')
"
```

### 실행

```bash
streamlit run demo.py
```

</details>

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID | **필수** |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI location (default: `global`) | 선택 |
| `GOOGLE_API_KEY` | Google AI Studio API Key | config 파일 대체 가능 |

---

## License & Citation

Apache-2.0 | [원본 README](README_ORIGINAL.md) 참고

```bibtex
@article{zhu2026paperbanana,
  title={PaperBanana: Automating Academic Illustration for AI Scientists},
  author={Zhu, Dawei and Meng, Rui and Song, Yale and Wei, Xiyu and Li, Sujian and Pfister, Tomas and Yoon, Jinsung},
  journal={arXiv preprint arXiv:2601.23265},
  year={2026}
}
```
