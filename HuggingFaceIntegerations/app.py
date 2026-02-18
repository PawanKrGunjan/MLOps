from functools import lru_cache
from typing import Literal, Any

import gradio as gr
from transformers import pipeline
from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate
import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"  # silences oneDNN

# Model identifiers (Helsinki-NLP MarianMT models)
HI_EN_MODEL = "Helsinki-NLP/opus-mt-hi-en"
EN_HI_MODEL = "Helsinki-NLP/opus-mt-en-hi"

TaskType = Literal[
    "Hindi → English",
    "English → Hindi",
    "Hindi → Hinglish (transliteration)",
]


@lru_cache(maxsize=None)
def get_hi_en_pipe() -> pipeline:
    """Lazy-load Hindi → English translation pipeline"""
    return pipeline("translation", model=HI_EN_MODEL)


@lru_cache(maxsize=None)
def get_en_hi_pipe() -> pipeline:
    """Lazy-load English → Hindi translation pipeline"""
    return pipeline("translation", model=EN_HI_MODEL)


def translate(
    text: str | None,
    task: TaskType,
    max_length: int = 256,
) -> str:
    """
    Main translation function used by the Gradio interface.
    Handles empty input gracefully and supports three tasks.
    """
    text = (text or "").strip()
    if not text:
        return ""

    try:
        if task == "Hindi → English":
            pipe = get_hi_en_pipe()
            result = pipe(
                text,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
            )
            return result[0]["translation_text"]

        if task == "English → Hindi":
            pipe = get_en_hi_pipe()
            result = pipe(
                text,
                max_length=max_length,
                num_beams=4,
                early_stopping=True,
            )
            return result[0]["translation_text"]

        if task == "Hindi → Hinglish (transliteration)":
            return transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)

        return "Unsupported task selected"

    except (ValueError, RuntimeError, OSError) as e:
        return f"Translation error: {str(e)}"
    except Exception as e:  # pylint: disable=broad-exception-caught
        return f"Unexpected error during translation: {str(e)}"


def build_demo() -> gr.Blocks:
    """Build and configure the Gradio interface"""
    with gr.Blocks(title="Hindi ↔ English + Hinglish Translator") as demo:
        gr.Markdown(
            """
            # Hindi ↔ English + Hinglish Translator
            
            - **Hindi → English** & **English → Hindi**: Neural machine translation  
            - **Hindi → Hinglish**: Roman transliteration (Devanagari → ITRANS)
            """
        )

        with gr.Row():
            task = gr.Dropdown(
                choices=[
                    "Hindi → English",
                    "English → Hindi",
                    "Hindi → Hinglish (transliteration)",
                ],
                value="Hindi → English",
                label="Task",
                interactive=True,
            )
            max_len = gr.Slider(
                32, 512, value=256, step=16,
                label="Max output length",
                info="Higher values allow longer translations (slower)",
            )

        input_text = gr.Textbox(
            label="Input text",
            lines=5,
            placeholder="नमस्ते दुनिया! या Hello world...",
        )

        translate_btn = gr.Button("Translate", variant="primary")

        output_text = gr.Textbox(
            label="Output",
            lines=5,
            interactive=False,
        )

        translate_btn.click(
            fn=translate,
            inputs=[input_text, task, max_len],
            outputs=output_text,
        )

        gr.Examples(
            examples=[
                ["नमस्ते! सब ठीक है?", "Hindi → English", 128],
                ["How are you today?", "English → Hindi", 128],
                ["नमस्ते भाई, क्या हाल है?", "Hindi → Hinglish (transliteration)", 128],
                ["खुश रहो और मुस्कुराते रहो", "Hindi → Hinglish (transliteration)", 128],
            ],
            inputs=[input_text, task, max_len],
            label="Quick examples",
        )

    return demo


demo = build_demo()


if __name__ == "__main__":
    # pragma: no cover - UI launch not tested
    demo.launch(
        # share=False,
        # inbrowser=False,
        # server_name="0.0.0.0",
        # server_port=7860,
    )