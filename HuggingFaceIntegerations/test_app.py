import app


class DummyPipe:
    def __init__(self, out_text: str):
        self.out_text = out_text

    def __call__(self, text, max_length=512):
        return [{"translation_text": self.out_text}]


def test_translate_empty_returns_empty():
    assert app.translate("", "Hindi → English") == ""


def test_hi_to_en_uses_hi_en_pipe(monkeypatch):
    # Ensure cached pipe isn't reused from another test run
    app.get_hi_en_pipe.cache_clear()

    monkeypatch.setattr(app, "get_hi_en_pipe", lambda: DummyPipe("hello"))
    assert app.translate("नमस्ते", "Hindi → English") == "hello"


def test_en_to_hi_uses_en_hi_pipe(monkeypatch):
    app.get_en_hi_pipe.cache_clear()

    monkeypatch.setattr(app, "get_en_hi_pipe", lambda: DummyPipe("नमस्ते"))
    assert app.translate("hello", "English → Hindi") == "नमस्ते"


def test_hi_to_hinglish_transliteration_nonempty():
    out = app.translate("नमस्ते", "Hindi → Hinglish (transliteration)")
    assert isinstance(out, str)
    assert len(out) > 0
