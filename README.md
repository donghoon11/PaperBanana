# <div align="center">PaperBanana 🍌</div>
<div align="center">Dawei Zhu, Rui Meng, Yale Song, Xiyu Wei, Sujian Li, Tomas Pfister and Jinsung yoon
<br><br></div>

</div>
<div align="center">
<a href="https://huggingface.co/papers/2601.23265"><img src="assets/paper-page-xl.svg" alt="Paper page on HF"></a>
<a href="https://huggingface.co/datasets/dwzhu/PaperBananaBench"><img src="assets/dataset-on-hf-xl.svg" alt="Dataset on HF"></a>
</div>

---

## Refactored Fork — Changes & Setup Guide

> This is a **sanitized and refactored fork** of [PaperBanana](https://github.com/dwzhu-pku/PaperBanana). All hardcoded API keys, project IDs, and personal information have been removed.

### Changes from the Original

| Item | Original | This Fork |
|------|----------|-----------|
| **Gemini Client** | Hardcoded Vertex AI project ID | Configurable via env var or config file |
| **Authentication** | Single mode (API Key or hardcoded Vertex AI) | **Dual mode**: Vertex AI (preferred) with API Key fallback |
| **Security** | API key present in config file | All credentials removed; template-only |
| **LLM Code Execution** | Direct `exec()` | `utils/safe_exec.py` — AST-validated sandboxed execution |

---

## Prerequisites — Google Cloud & Gemini API 준비

PaperBanana는 **Google Gemini**를 메인 LLM/이미지 생성 모델로 사용합니다.
현재 AI Studio API Key 단독 사용 시 일부 모델/기능에서 에러가 발생하므로, **Vertex AI를 통한 호출이 필수**입니다.
따라서 아래 **두 단계를 모두** 완료해야 합니다.

### Step 1. Google AI Studio에서 API Key 발급

API Key는 Google Cloud 프로젝트와 연결되며, 이 과정에서 프로젝트가 자동 생성됩니다.

1. **Google 계정 준비** — 일반 Gmail 계정이면 충분합니다.
2. **Google AI Studio 접속** — [aistudio.google.com](https://aistudio.google.com) 에 로그인합니다.
3. **API Key 생성** — 좌측 메뉴 "Get API key" > "Create API key" 클릭합니다.
   - 이때 "Google Cloud 프로젝트"를 선택하거나 새로 생성하게 됩니다.
   - 이 프로젝트가 Step 2에서 사용할 GCP 프로젝트입니다.
4. **API Key 복사** — 생성된 키를 기록해 둡니다 (형식: `AIza...`).

> **참고**: 이 API Key 자체만으로는 PaperBanana를 실행할 수 없습니다. 아래 Step 2의 Vertex AI 설정까지 완료해야 합니다.

### Step 2. Google Cloud / Vertex AI 설정

Step 1에서 생성된(또는 선택한) GCP 프로젝트에 결제 계정을 연결하고 gcloud 인증을 설정합니다.
(`google-genai` SDK가 Vertex AI 엔드포인트를 직접 호출하므로, 별도의 "Vertex AI API" 활성화는 필요하지 않습니다.)

1. **Google Cloud Console 접속** — [console.cloud.google.com](https://console.cloud.google.com) 에서 Step 1에서 사용한 프로젝트를 선택합니다.
2. **결제 계정 연결** — 콘솔 > "결제" 메뉴에서 결제 계정을 연결합니다. (신규 가입 시 $300 무료 크레딧 제공)
3. **gcloud CLI 설치 및 인증**:
   ```bash
   # gcloud CLI 설치 (이미 설치된 경우 생략)
   # https://cloud.google.com/sdk/docs/install 참고

   # 로그인 및 기본 인증 설정
   gcloud auth login
   gcloud auth application-default login

   # 프로젝트 설정 (Step 1에서 사용한 프로젝트 ID)
   gcloud config set project YOUR_PROJECT_ID
   export GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
   ```

### Step 3. 설정 파일 구성 (configs/model_config.yaml)

API Key와 프로젝트 ID를 코드에 넣는 것이 아니라, **설정 파일**에 모아서 관리합니다.

#### config 파일 구조

```
configs/
├── model_config.template.yaml   ← git에 포함됨 (값이 비어 있는 템플릿)
└── model_config.yaml            ← git에서 제외됨 (.gitignore) — 실제 값 입력
```

- `model_config.template.yaml`은 형식 참고용 템플릿입니다. **직접 수정하지 마세요.**
- `model_config.yaml`은 `.gitignore`에 등록되어 있어 커밋되지 않으므로, 여기에 실제 키와 프로젝트 ID를 안전하게 입력합니다.

#### 설정 방법

```bash
# 템플릿 복사
cp configs/model_config.template.yaml configs/model_config.yaml
```

`configs/model_config.yaml`을 열어 아래와 같이 입력합니다:

```yaml
# Default Models
defaults:
  model_name: "gemini-2.5-flash-preview-05-20"        # 텍스트 생성용 모델
  image_model_name: "gemini-2.0-flash-exp-image-generation"  # 이미지 생성용 모델

# API Keys
api_keys:
  google_api_key: "AIzaSy..."   # ← Step 1에서 발급한 API Key 붙여넣기
  openai_api_key: ""            # 선택 (OpenAI 모델 사용 시)
  anthropic_api_key: ""         # 선택 (Claude 모델 사용 시)

# Google Cloud / Vertex AI
google_cloud:
  project_id: "my-project-12345"  # ← Step 1에서 사용한 GCP 프로젝트 ID 붙여넣기
  location: "global"              # 보통 "global" 그대로 사용
```

#### 값을 읽는 우선순위

코드(`utils/generation_utils.py`)는 각 설정값을 다음 순서로 찾습니다:

```
1. 환경변수  (export GOOGLE_CLOUD_PROJECT=...)   ← 최우선
2. config 파일  (configs/model_config.yaml)       ← 환경변수가 없을 때 사용
3. 기본값  (코드에 하드코딩된 fallback)            ← 둘 다 없을 때
```

따라서 환경변수와 config 파일 **중 하나만** 설정해도 됩니다.
둘 다 설정한 경우 환경변수가 우선합니다.

| 설정값 | 환경변수 | config 파일 위치 |
|--------|----------|-----------------|
| GCP 프로젝트 ID | `GOOGLE_CLOUD_PROJECT` | `google_cloud.project_id` |
| Vertex AI 리전 | `GOOGLE_CLOUD_LOCATION` | `google_cloud.location` |
| Google API Key | `GOOGLE_API_KEY` | `api_keys.google_api_key` |
| 텍스트 모델명 | (CLI `--model_name`) | `defaults.model_name` |
| 이미지 모델명 | (CLI `--model_name`) | `defaults.image_model_name` |

### 실행 시 코드 동작 흐름

PaperBanana를 실행하면 `utils/generation_utils.py`에서 다음 순서로 Gemini 클라이언트가 초기화됩니다:

```
실행 시작
    │
    ▼
configs/model_config.yaml 로드 (있으면)
    │
    ▼
환경변수 / config 에서 인증 정보 읽기
    │
    ├─ GOOGLE_CLOUD_PROJECT 있음?
    │      │
    │      ▼  YES
    │   genai.Client(vertexai=True, project=..., location=...)
    │   → google-auth 가 ADC 토큰을 자동으로 읽어 Vertex AI 인증
    │   → "Initialized Gemini Client with Vertex AI" 출력
    │
    ├─ GOOGLE_API_KEY만 있음?
    │      │
    │      ▼  YES
    │   genai.Client(api_key=...)
    │   → API Key로 직접 인증 (일부 기능 제한으로 에러 발생 가능)
    │   → "Initialized Gemini Client with API Key" 출력
    │
    └─ 둘 다 없음?
           │
           ▼
        gemini_client = None → 이후 API 호출 시 RuntimeError 발생
```

이후 모든 에이전트(`agents/*.py`)가 `call_gemini_with_retry_async()`를 통해
`gemini_client.aio.models.generate_content()`를 호출하며, 텍스트 생성과 이미지 생성 모두 동일한 클라이언트를 사용합니다.

### 라이브러리 의존관계

```
┌──────────────────────────────────────────────────────┐
│  PaperBanana 코드                                     │
│  utils/generation_utils.py, agents/*.py, demo.py      │
│                                                       │
│  genai.Client(vertexai=True, project=...) ← 필수 경로 │
└───────────────┬───────────────────────────────────────┘
                │ import
                ▼
┌──────────────────────────────────────┐
│  google-genai (pip 패키지)            │  ← requirements.txt
│  from google import genai             │
│  from google.genai import types       │
│                                       │
│  Gemini 모델 호출 통합 SDK            │
│  genai.Client() 하나로               │
│  텍스트/이미지 생성 모두 처리         │
└───────────┬───────────────────────────┘
            │ 내부 의존
            ▼
┌──────────────────────────────────────┐
│  google-auth (pip 패키지)             │  ← requirements.txt
│                                       │
│  ADC (Application Default             │
│  Credentials) 처리                    │
│                                       │
│  gcloud auth application-default      │
│  login 으로 생성된 인증 토큰을        │
│  자동으로 읽어 Vertex AI 요청에 사용  │
└───────────┬───────────────────────────┘
            │ 인증 파일 읽기
            ▼
┌──────────────────────────────────────┐
│  gcloud CLI (별도 설치)               │
│                                       │
│  gcloud auth application-default      │
│  login 실행 시 로컬에 인증 파일 생성  │
│  ~/.config/gcloud/application_        │
│  default_credentials.json             │
└───────────────────────────────────────┘
```

| 패키지 | 역할 | 필수 여부 |
|--------|------|----------|
| `google-genai` | Gemini API 통합 SDK. `genai.Client()`로 모델 호출 | **필수** |
| `google-auth` | GCP 인증 토큰(ADC)을 읽어 Vertex AI 요청에 자동 첨부 | **필수** |
| `gcloud` CLI | `application-default login`으로 로컬 인증 파일 생성 | **필수** (pip 패키지 아님, 별도 설치) |

---

### Quick Setup 요약

```bash
# 1. 환경변수 설정
export GOOGLE_CLOUD_PROJECT="your-project-id"

# 2. gcloud 인증 (최초 1회)
gcloud auth application-default login

# 3. 설정 파일 생성
cp configs/model_config.template.yaml configs/model_config.yaml
# configs/model_config.yaml 편집:
#   defaults.model_name, defaults.image_model_name 입력
#   google_cloud.project_id 입력

# 4. 의존성 설치
uv venv && source .venv/bin/activate
uv python install 3.12
uv pip install -r requirements.txt

# 5. 데이터셋 다운로드 (선택)
# PaperBananaBench → data/PaperBananaBench/ 에 배치
```

### Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| `GOOGLE_CLOUD_PROJECT` | Google Cloud project ID (Vertex AI 사용) | **필수** |
| `GOOGLE_CLOUD_LOCATION` | Vertex AI location (default: `global`) | 선택 |
| `ANTHROPIC_API_KEY` | Anthropic API key (Claude 모델 사용 시) | 선택 |
| `OPENAI_API_KEY` | OpenAI API key (GPT/DALL-E 모델 사용 시) | 선택 |

---

> Hi everyone! The original version of PaperBanana is already open-sourced under Google-Research as [PaperVizAgent](https://github.com/google-research/papervizagent).
This repository forked the content of that repo and aims to keep evolving toward better support for academic paper illustration—though we have made solid progress, there is still a long way to go for more reliable generation and for more diverse, complex scenarios. PaperBanana is intended to be a fully open-source project dedicated to facilitating academic illustration for all researchers. Our goal is simply to benefit the community, so we currently have no plans to use it for commercial purposes.




**PaperBanana** is a reference-driven multi-agent framework for automated academic illustration generation. Acting like a creative team of specialized agents, it transforms raw scientific content into publication-quality diagrams and plots through an orchestrated pipeline of **Retriever, Planner, Stylist, Visualizer, and Critic** agents. The framework leverages in-context learning from reference examples and iterative refinement to produce aesthetically pleasing and semantically accurate scientific illustrations.

Here are some example diagrams and plots generated by PaperBanana:
![Examples](assets/teaser_figure.jpg)

## Overview of PaperBanana

![PaperBanana Framework](assets/method_diagram.png)

PaperBanana achieves high-quality academic illustration generation by orchestrating five specialized agents in a structured pipeline:

1. **Retriever Agent**: Identifies the most relevant reference diagrams from a curated collection to guide downstream agents
2. **Planner Agent**: Translates method content and communicative intent into comprehensive textual descriptions using in-context learning
3. **Stylist Agent**: Refines descriptions to adhere to academic aesthetic standards using automatically synthesized style guidelines
4. **Visualizer Agent**: Transforms textual descriptions into visual outputs using state-of-the-art image generation models
5. **Critic Agent**: Forms a closed-loop refinement mechanism with the Visualizer through multi-round iterative improvements

## Quick Start

### Step1: Clone the Repo
```bash
git clone https://github.com/dwzhu-pku/PaperBanana.git
cd PaperBanana
```

### Step2: Configuration
PaperBanana supports configuring API keys from a YAML configuration file or via environment variables.

We recommend duplicate the `configs/model_config.template.yaml` file into `configs/model_config.yaml` to externalize all user configurations. This file is ignored by git to keep your api keys and configurations secret. In `model_config.yaml`, remember to fill in the two model names (`defaults.model_name` and `defaults.image_model_name`) and set at least one API key under `api_keys` (e.g. `google_api_key` for Gemini models).

Note that if you need to generate many candidates simultaneously, you will require an API key that supports high concurrency.

### Step3: Downloading the Dataset
First download [PaperBananaBench](https://huggingface.co/datasets/dwzhu/PaperBananaBench), then place it under the `data` directory (e.g., `data/PaperBananaBench/`). The framework is designed to function gracefully without the dataset by bypassing the Retriever Agent's few-shot learning capability. If interested in the original PDFs, please download them from [PaperBananaDiagramPDFs](https://huggingface.co/datasets/dwzhu/PaperBananaDiagramPDFs).

### Step4: Installing the Environment
1. We use `uv` to manage Python packages. Please install `uv` following the instructions [here](https://docs.astral.sh/uv/getting-started/installation/).

2. Create and activate a virtual environment
    ```bash
    uv venv # This will create a virtual environment in the current directory, under .venv/
    source .venv/bin/activate  # or .venv\Scripts\activate on Windows
    ```

3. Install python 3.12
    ```bash
    uv python install 3.12
    ```

4. Install required packages
    ```bash
    uv pip install -r requirements.txt
    ```

### Launch PaperBanana

#### Interactive Demo (Streamlit)
The easiest way to launch PaperBanana is via the interactive Streamlit demo:
```bash
streamlit run demo.py
```

The web interface provides two main workflows:

**1. Generate Candidates Tab**:
- Paste your method section content (Markdown recommended) and provide the figure caption.
- Configure settings (pipeline mode, retrieval setting, number of candidates, aspect ratio, critic rounds).
- Click "Generate Candidates" and wait for parallel processing.
- View results in a grid with evolution timelines and download individual images or batch ZIP.

**2. Refine Image Tab**:
- Upload a generated candidate or any diagram.
- Describe desired changes or request upscaling.
- Select resolution (2K/4K) and aspect ratio.
- Download the refined high-resolution output.

#### Command-Line Interface
You can also run PaperBanana from the command line:
```bash
# Basic usage with default settings
python main.py

# Advanced usage with custom settings
python main.py \
  --dataset_name "PaperBananaBench" \
  --task_name "diagram" \
  --split_name "test" \
  --exp_mode "dev_full" \
  --retrieval_setting "auto"
```

**Available Options:**
- `--dataset_name`: Dataset to use (default: `PaperBananaBench`)
- `--task_name`: Task type - `diagram` or `plot` (default: `diagram`)
- `--split_name`: Dataset split (default: `test`)
- `--exp_mode`: Experiment mode (see section below)
- `--retrieval_setting`: Retrieval strategy - `auto`, `manual`, `random`, or `none` (default: `auto`)

**Experiment Modes:**
- `vanilla`: Direct generation without planning or refinement
- `dev_planner`: Planner → Visualizer only
- `dev_planner_stylist`: Planner → Stylist → Visualizer
- `dev_planner_critic`: Planner → Visualizer → Critic (multi-round)
- `dev_full`: Full pipeline with all agents
- `demo_planner_critic`: Demo mode (Planner → Visualizer → Critic) without evaluation
- `demo_full`: Demo mode (full pipeline) without evaluation

### Visualization Tools

View pipeline evolution and intermediate results:
```bash
streamlit run visualize/show_pipeline_evolution.py
```
View evaluation results:
```bash
streamlit run visualize/show_referenced_eval.py
```

## Project Structure
```
├── .venv/
│   └── ...
├── data/
│   └── PaperBananaBench/
│       ├── diagram/
│       │   ├── images/
│       │   ├── pdfs/
│       │   ├── test.json
│       │   └── ref.json
│       └── plot/
├── agents/
│   ├── __init__.py
│   ├── base_agent.py
│   ├── retriever_agent.py
│   ├── planner_agent.py
│   ├── stylist_agent.py
│   ├── visualizer_agent.py
│   ├── critic_agent.py
│   ├── vanilla_agent.py
│   └── polish_agent.py
├── prompts/
│   ├── __init__.py
│   ├── diagram_eval_prompts.py
│   └── plot_eval_prompts.py
├── style_guides/
│   ├── generate_category_style_guide.py
│   └── ...
├── utils/
│   ├── __init__.py
│   ├── config.py
│   ├── paperviz_processor.py
│   ├── eval_toolkits.py
│   ├── generation_utils.py
│   └── image_utils.py
├── visualize/
│   ├── show_pipeline_evolution.py
│   └── show_referenced_eval.py
├── scripts/
│   ├── run_main.sh
│   ├── run_demo.sh
├── configs/
│   └── model_config.template.yaml
├── results/
│   ├── PaperBananaBench_diagram/
│   └── parallel_demo/
├── main.py
├── demo.py
└── README.md
```

## Key Features

### Multi-Agent Pipeline
- **Reference-Driven**: Learns from curated examples through generative retrieval
- **Iterative Refinement**: Critic-Visualizer loop for progressive quality improvement
- **Style-Aware**: Automatically synthesized aesthetic guidelines ensure academic quality
- **Flexible Modes**: Multiple experiment modes for different use cases

### Interactive Demo
- **Parallel Generation**: Generate up to 20 candidate diagrams simultaneously
- **Pipeline Visualization**: Track the evolution through Planner → Stylist → Critic stages
- **High-Resolution Refinement**: Upscale to 2K/4K using Image Generation APIs
- **Batch Export**: Download all candidates as PNG or ZIP

### Extensible Design
- **Modular Agents**: Each agent is independently configurable
- **Task Support**: Handles both conceptual diagrams and data plots
- **Evaluation Framework**: Built-in evaluation against ground truth with multiple metrics
- **Async Processing**: Efficient batch processing with configurable concurrency


## TODO List
- [ ] Add support for using manually selected examples. Provide **a** user-friendly interface.
- [ ] Upload code for generating statistical plots.
- [ ] Upload code for improving existing diagrams based on style guideline.
- [ ] Expand the reference set to support more areas beyond computer science.


## Community Supports
Around the release of this repo, we noticed several community efforts to reproduce this work. These efforts introduce unique perspectives that we find incredibly valuable. We highly recommend checking out these excellent contributions: (welcome to add if we missed something):
- https://github.com/llmsresearch/paperbanana
- https://github.com/efradeca/freepaperbanana

Additionally, alongside the development of this method, many other works have been exploring the same topic of automated academic illustration generation—some even enabling editable generated figures. Their contributions are essential to the ecosystem and are well worth your attention (likewise, welcome to add):
- https://github.com/ResearAI/AutoFigure-Edit
- https://github.com/OpenDCAI/Paper2Any
- https://github.com/BIT-DataLab/Edit-Banana

Overall, we are encouraged that the fundamental capabilities of current models have brought us much closer to solving the problem of automated academic illustration generation. With the community's continued efforts, we believe that in the near future we will have high-quality automated drawing tools to accelerate academic research iteration and visual communication.

We warmly welcome community contributions to make PaperBanana even better!

## License
Apache-2.0

## Citation
If you find this repo helpful, please cite our paper as follows:
```bibtex
@article{zhu2026paperbanana,
  title={PaperBanana: Automating Academic Illustration for AI Scientists},
  author={Zhu, Dawei and Meng, Rui and Song, Yale and Wei, Xiyu and Li, Sujian and Pfister, Tomas and Yoon, Jinsung},
  journal={arXiv preprint arXiv:2601.23265},
  year={2026}
}
```

## Disclaimer
This is not an officially supported Google product. This project is not eligible for the [Google Open Source Software Vulnerability Rewards Program](https://bughunters.google.com/open-source-security).

Our goal is simply to benefit the community, so currently we have no plans to use it for commercial purposes. The core methodology was developed during my internship at Google, and patents have been filed for these specific workflows by Google. While this doesn't impact open-source research efforts, it restricts third-party commercial applications using similar logic.

