
---
title: Machine Translation — Hindi ↔ English + Hinglish Transliteration
emoji: 🌐
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.0   # Safe, widely used version in late 2025/2026; update if needed (or remove line for latest)
python_version: 3.12
app_file: app.py
pinned: false
short_description: Bidirectional Hindi-English translation + Devanagari to Roman (Hinglish-style) transliteration
---
# Machine Translation — Hindi ↔ English + Hindi → Hinglish

A lightweight Gradio web app for:

- **Hindi → English** translation  
  Model: [Helsinki-NLP/opus-mt-hi-en](https://huggingface.co/Helsinki-NLP/opus-mt-hi-en)
- **English → Hindi** translation  
  Model: [Helsinki-NLP/opus-mt-en-hi](https://huggingface.co/Helsinki-NLP/opus-mt-en-hi)
- **Hindi → Hinglish** (transliteration / Romanization)  
  Using `indic-transliteration` library (ITRANS scheme) — **not semantic translation**

> **Note**: "Hinglish" here means converting Devanagari script to readable Latin characters (e.g. "नमस्ते दुनिया" → "namaste duniyaa"). It is **transliteration**, not translation or phonetic Hinglish mixing.

[![Open in Hugging Face](https://img.shields.io/badge/🤗%20Open%20in%20Spaces-blueviolet?logo=huggingface&logoColor=white)](https://huggingface.co/spaces/PawanKrGunjan/Machine-Translation)

Live demo: https://huggingface.co/spaces/PawanKrGunjan/Machine-Translation

## Features

- Lazy model loading (only downloads/loads models when first used)
- GPU acceleration if available (auto-detected)
- Max output length control for translations
- Clean, responsive Gradio interface with examples

## Screenshots / Preview

(Once running, the Space shows the Gradio UI. You can later add a static screenshot here like:)

<!-- ![App Interface](assets/screenshot.png)  → add this file later if desired -->

## Project Structure (in Hugging Face Space root)

After sync, the Space repository contains:

```
.
├── app.py              # Gradio application (main entrypoint)
├── requirements.txt    # Dependencies (transformers, gradio, torch, indic-transliteration, ...)
└── README.md           # This file (with YAML metadata)
```

## How Deployment Works

This Space is **automatically synced** from the GitHub monorepo:

- Source folder: https://github.com/PawanKrGunjan/MLOps/tree/dev/HuggingFaceIntegerations
- GitHub Actions workflow: `.github/workflows/HF-MT.yaml`
- On every push to `dev` branch (or manual dispatch), it force-pushes only the contents of `HuggingFaceIntegerations/` to the Space repo root.
- This keeps the main repo organized while the Space stays clean.

## Local Setup (for development / testing)

```bash
# 1. Clone the monorepo
git clone https://github.com/PawanKrGunjan/MLOps.git
cd MLOps/HuggingFaceIntegerations

# 2. Virtual environment
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Run the app
python app.py
```

→ Open http://127.0.0.1:7860 in your browser

## Requirements (requirements.txt excerpt)

```text
gradio
transformers>=4.45.0
torch>=2.0.0
indic-transliteration
```

(Full list in the actual file)

## Development Notes

- Models are MarianMT-based (~300–600 MB each) → first run downloads them
- Transliteration uses ITRANS scheme (good readability); alternatives like HK or IndicXlit could be explored later for more "natural" Hinglish look
- Add error handling / logging if scaling up

## License

MIT License

Feel free to fork, modify, or use in your projects!
ifferent emoji, add donation link, change license, etc.)! 🚀
