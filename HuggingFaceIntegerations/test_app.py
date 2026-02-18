import app
import gradio as gr


class DummyPipe:
    def __init__(self, out_text: str):
        self.out_text = out_text

    def __call__(self, text, **kwargs):  # accept all kwargs → matches real pipeline
        return [{"translation_text": self.out_text}]


def test_translate_empty_returns_empty():
    assert app.translate("", "Hindi → English") == ""
    assert app.translate("   ", "English → Hindi") == ""
    assert app.translate(None, "Hindi → Hinglish (transliteration)") == ""


def test_hi_to_en_uses_hi_en_pipe(monkeypatch):
    app.get_hi_en_pipe.cache_clear()
    monkeypatch.setattr(app, "get_hi_en_pipe", lambda: DummyPipe("hello"))
    assert app.translate("नमस्ते", "Hindi → English") == "hello"


def test_en_to_hi_uses_en_hi_pipe(monkeypatch):
    app.get_en_hi_pipe.cache_clear()
    monkeypatch.setattr(app, "get_en_hi_pipe", lambda: DummyPipe("नमस्ते"))
    assert app.translate("hello", "English → Hindi") == "नमस्ते"


def test_hi_to_hinglish_transliteration_nonempty():
    out = app.translate("नमस्ते भाई कैसे हो?", "Hindi → Hinglish (transliteration)")
    assert isinstance(out, str)
    assert len(out) > 0

def test_build_demo_returns_blocks():
    demo = app.build_demo()
    assert isinstance(demo, gr.Blocks)
    assert demo.title == "Hindi ↔ English + Hinglish Translator"  # or whatever your title is

def get_all_component_types(block):
    types = set()
    def recurse(b):
        if hasattr(b, 'children'):
            for child in b.children or []:
                types.add(type(child).__name__)
                recurse(child)
    recurse(block)
    return types


def test_build_demo_has_expected_components():
    demo = app.build_demo()
    component_types = get_all_component_types(demo)
    
    assert "Dropdown" in component_types
    assert "Slider" in component_types
    assert "Textbox" in component_types
    assert "Button" in component_types
    
def test_translate_catches_translation_error(monkeypatch):
    def broken_pipe(*args, **kwargs):
        raise RuntimeError("mock model crash")

    monkeypatch.setattr(app, "get_hi_en_pipe", lambda: broken_pipe)
    
    result = app.translate("नमस्ते", "Hindi → English")
    assert "error" in result.lower()
    assert "mock model crash" in result   # or just check prefix