---
title: Machine Translation — Hindi ↔ English + Hinglish
emoji: 
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: "4.44.0"
python_version: "3.12"
app_file: app.py
pinned: false
short_description: Hindi ↔ English translation and Hindi to Roman (Hinglish) transliteration
---

# Machine Translation — Hindi ↔ English + Hindi → Hinglish

A simple Gradio app using:

- **Hindi → English**: [Helsinki-NLP/opus-mt-hi-en](https://huggingface.co/Helsinki-NLP/opus-mt-hi-en)
- **English → Hindi**: [Helsinki-NLP/opus-mt-en-hi](https://huggingface.co/Helsinki-NLP/opus-mt-en-hi)
- **Hindi → Hinglish** (transliteration): `indic-transliteration` (ITRANS scheme)

> **Hinglish output** is Romanized Hindi (e.g. "नमस्ते" → "namaste"), not full translation.

Live demo should appear below once configuration is fixed.

## Quick Local Test

```bash
cd HuggingFaceIntegerations
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
