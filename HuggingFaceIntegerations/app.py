from functools import lru_cache

import gradio as gr
from transformers import pipeline
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

HI_EN_MODEL = "Helsinki-NLP/opus-mt-hi-en"
EN_HI_MODEL = "Helsinki-NLP/opus-mt-en-hi"


@lru_cache(maxsize=1)
def get_hi_en_pipe():
    return pipeline("translation_hi_to_en", model=HI_EN_MODEL)


@lru_cache(maxsize=1)
def get_en_hi_pipe():
    return pipeline("translation_en_to_hi", model=EN_HI_MODEL)


def translate(text: str, task_name: str, max_length: int = 512) -> str:
    text = (text or "").strip()
    if not text:
        return ""

    if task_name == "Hindi → English":
        result = get_hi_en_pipe()(text, max_length=max_length)
        return result[0]["translation_text"]

    if task_name == "English → Hindi":
        result = get_en_hi_pipe()(text, max_length=max_length)
        return result[0]["translation_text"]

    if task_name == "Hindi → Hinglish (transliteration)":
        return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)

    return "Unknown task"


def build_demo():
    with gr.Blocks() as demo:
        gr.Markdown("## Simple MT: Hindi ↔ English + Hindi → Hinglish")

        task = gr.Dropdown(
            choices=[
                "Hindi → English",
                "English → Hindi",
                "Hindi → Hinglish (transliteration)",
            ],
            value="Hindi → English",
            label="Task",
        )

        inp = gr.Textbox(label="Input text", lines=5)
        max_len = gr.Slider(16, 512, value=256, step=8, label="Max length")
        btn = gr.Button("Translate")
        out = gr.Textbox(label="Output", lines=5)

        btn.click(
            fn=translate, inputs=[inp, task, max_len], outputs=[out]
        )  # pylint: disable=no-member
    return demo


if __name__ == "__main__":
    build_demo().launch()
