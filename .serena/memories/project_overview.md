# Project Overview: AI異常検知プログラム生成アプリ

## Purpose
This is a Streamlit-based web application that automatically generates and executes anomaly detection programs for images using AI. Users can specify conditions in natural language (Japanese), and the application will generate Python code using Anthropic Claude API to detect anomalies based on those conditions.

## Key Features
- Text-based condition specification (e.g., "画像に2つのリンゴがあること" - "there are 2 apples in the image")
- AI-powered automatic Python code generation using Anthropic Claude API
- Image upload functionality (custom images or default samples)
- Real-time code execution and result display
- Generated code download capability

## Tech Stack
- **Frontend**: Streamlit 1.45.0
- **AI API**: Anthropic Claude (claude-3-7-sonnet-20250219)
- **Object Detection**: Grounding DINO (Hugging Face Transformers)
- **Image Processing**: PIL, PyTorch 2.7.0
- **Deployment**: Docker + EC2 (AWS)
- **Package Management**: uv (preferred) or pip
- **Python Version**: 3.11+

## Live Demo
https://takah1r0jp-streamlit-ad-app-appmain-ghw67a.streamlit.app/