PaperBanana — Windows Setup Guide
===================================
Windows 11 환경에서 PaperBanana를 처음 설치하는 사용자를 위한 가이드입니다.
Ubuntu 기준의 README.md 대신 이 문서를 참고하세요.


Step 1. Google AI Studio — API Key 발급
----------------------------------------
1. https://aistudio.google.com 에 Google 계정으로 로그인합니다.
2. 좌측 메뉴 "Get API key" > "Create API key" 를 클릭합니다.
3. GCP 프로젝트를 선택하거나 새로 생성합니다.
   - 이 프로젝트가 이후 Step 3에서 사용할 GCP 프로젝트입니다.
4. 생성된 API Key (형식: AIza...) 를 기록해 둡니다.


Step 2. Google Cloud SDK (gcloud CLI) 설치
-------------------------------------------
1. 아래 링크에서 GoogleCloudSDKInstaller.exe 를 다운로드합니다.
   https://cloud.google.com/sdk/docs/install#windows

2. 설치 마법사를 실행하고 기본 옵션으로 설치합니다.

3. 설치 완료 후 시작 메뉴에서 "Google Cloud SDK Shell" 을 실행합니다.
   - 주의: 일반 cmd 또는 PowerShell 에서는 PATH가 아직 적용되지 않아
     권한 오류가 발생할 수 있습니다. Google Cloud SDK Shell 사용을 권장합니다.


Step 3. gcloud 인증
--------------------
아래 명령어를 모두 "Google Cloud SDK Shell" 에서 실행합니다.

1. gcloud 계정 로그인:
   > gcloud auth login
   - 브라우저가 열리면 Google 계정으로 로그인합니다.

2. Application Default Credentials (ADC) 설정:
   > gcloud auth application-default login
   - 브라우저에서 동일 계정으로 로그인합니다.
   - 인증 파일이 아래 경로에 저장됩니다:
     C:\Users\<USERNAME>\AppData\Roaming\gcloud\application_default_credentials.json

3. 사용 가능한 프로젝트 목록 확인:
   > gcloud projects list

4. Quota project 및 기본 프로젝트 설정:
   > gcloud auth application-default set-quota-project <PROJECT_ID>
   > gcloud config set project <PROJECT_ID>
   - <PROJECT_ID> 는 위 목록에서 확인한 프로젝트 ID로 대체합니다.
   - 예: gen-lang-client-0054836708


Step 4. 설정 파일 구성 (configs/model_config.yaml)
---------------------------------------------------
1. 템플릿 파일을 복사합니다:
   > copy configs\model_config.template.yaml configs\model_config.yaml

2. configs\model_config.yaml 을 텍스트 에디터로 열고 아래 항목을 입력합니다:

   defaults:
     model_name: "gemini-2.5-flash-preview-05-20"
     image_model_name: "gemini-2.0-flash-exp-image-generation"

   api_keys:
     google_api_key: "AIza..."      <- Step 1에서 발급한 API Key
     openai_api_key: ""             <- 선택 (사용 시 입력)
     anthropic_api_key: ""          <- 선택 (사용 시 입력)

   google_cloud:
     project_id: "your-project-id"  <- Step 3에서 확인한 프로젝트 ID
     location: "global"

   주의: model_config.yaml 은 .gitignore 에 등록되어 있어 커밋되지 않습니다.
         API Key를 안전하게 보관하세요.


Step 5. Python 환경 설정 (uv)
------------------------------
uv 는 빠른 Python 패키지 관리자입니다.

1. uv 설치 (pip 방식, 시스템 Python 사용):
   > pip install uv

   또는 공식 설치 스크립트:
   https://docs.astral.sh/uv/getting-started/installation/

2. PaperBanana 디렉토리로 이동:
   > cd e:\PaperBanana

3. 가상환경 생성:
   > uv venv

4. Python 3.12 설치:
   > uv python install 3.12

5. 의존성 설치:
   > uv pip install -r requirements.txt

6. 가상환경 활성화:
   - cmd:        .venv\Scripts\activate
   - PowerShell: .venv\Scripts\Activate.ps1

   주의: Linux/Mac의 "source .venv/bin/activate" 는 Windows에서 사용하지 않습니다.


Step 6. 데이터셋 다운로드 (선택)
----------------------------------
데이터셋 없이도 Retriever Agent를 제외한 기능은 동작합니다.
벤치마크 평가가 필요한 경우 아래 절차를 따릅니다.

requirements.txt 에 huggingface_hub 가 포함되어 있으므로
Step 5의 uv pip install 로 이미 설치되어 있습니다.

1. 아래 Python 스크립트를 실행하여 데이터셋을 다운로드합니다:

   python -c "
   from huggingface_hub import snapshot_download
   snapshot_download(
       repo_id='dwzhu/PaperBananaBench',
       repo_type='dataset',
       local_dir='data/PaperBananaBench'
   )
   "

2. ZIP 파일 압축 해제:

   python -c "
   import zipfile
   with zipfile.ZipFile('data/PaperBananaBench/PaperBananaBench.zip', 'r') as z:
       z.extractall('data')
   "

3. 완료 후 디렉토리 구조:
   data/
   └── PaperBananaBench/
       ├── diagram/
       │   ├── images/
       │   ├── test.json
       │   └── ref.json
       └── plot/
           ├── images/
           ├── test.json
           └── ref.json


Step 7. Streamlit 데모 실행
-----------------------------
1. 가상환경이 활성화된 상태에서 실행합니다:
   > streamlit run demo.py

2. 브라우저에서 접속합니다:
   http://localhost:8501

3. 정상 실행 시 터미널에 아래와 같은 메시지가 출력됩니다:
   Initialized Gemini Client with Vertex AI (project: your-project-id)


Environment Variables (선택)
------------------------------
config 파일 대신 환경변수로 설정할 수도 있습니다 (환경변수가 우선 적용됨):

   > set GOOGLE_CLOUD_PROJECT=your-project-id
   > set GOOGLE_API_KEY=AIza...

| 환경변수                  | config 파일 위치               |
|--------------------------|-------------------------------|
| GOOGLE_CLOUD_PROJECT     | google_cloud.project_id       |
| GOOGLE_CLOUD_LOCATION    | google_cloud.location         |
| GOOGLE_API_KEY           | api_keys.google_api_key       |


Troubleshooting
----------------
- "Permission denied: adc.json" 오류
  → 일반 cmd 대신 "Google Cloud SDK Shell" 에서 gcloud 명령어를 실행하세요.

- "quota exceeded" 또는 "API not enabled" 오류
  → gcloud auth application-default set-quota-project <PROJECT_ID> 를 실행하세요.

- "streamlit: command not found" 오류
  → .venv\Scripts\activate 로 가상환경을 먼저 활성화하세요.

- "ModuleNotFoundError" 오류
  → uv pip install -r requirements.txt 를 다시 실행하세요.

- "Warning: Could not initialize Anthropic/OpenAI Client"
  → Gemini만 사용하는 경우 정상 메시지입니다. 무시해도 됩니다.
