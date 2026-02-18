---
title: Hindi ↔ English + Hinglish Translator
emoji: 🌐
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.6.0
app_file: app.py
license: MIT
short_description: Hindi↔English translator + Hinglish transliteration
tags:
  - translation
  - machine-translation
  - hindi
  - hinglish
  - indic-languages
  - gradio
models:
  - Helsinki-NLP/opus-mt-hi-en
  - Helsinki-NLP/opus-mt-en-hi
---

# Hindi ↔ English + Hinglish Translator

A simple, fast multilingual translator demo built with Hugging Face Transformers and Gradio.

## Features
- **Hindi → English** — Neural machine translation (MarianMT)
- **English → Hindi** — Neural machine translation (MarianMT)
- **Hindi → Hinglish** — Roman transliteration using ITRANS scheme

### Powered by
- [Helsinki-NLP/opus-mt-hi-en](https://huggingface.co/Helsinki-NLP/opus-mt-hi-en)
- [Helsinki-NLP/opus-mt-en-hi](https://huggingface.co/Helsinki-NLP/opus-mt-en-hi)
- [indic-transliteration library](https://github.com/AnimeshSinha1309/indic-transliteration)

Just type or paste text, select a task, adjust max length if needed, and click **Translate**!

Made with ❤️ in India 🇮🇳  
