from src.ui.styles import STYLESHEET


def test_stylesheet_is_non_empty_string():
    assert isinstance(STYLESHEET, str)
    assert len(STYLESHEET) > 0


def test_stylesheet_contains_accent_color():
    assert "#4b6bdf" in STYLESHEET


def test_stylesheet_contains_background_color():
    assert "#f4f5f9" in STYLESHEET
