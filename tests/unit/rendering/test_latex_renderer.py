from cv_generator.rendering.latex_renderer import escape_latex


def test_escape_latex_escapes_special_characters() -> None:
    text = r"R&D improved 60% using file_name #1 at $5"

    escaped = escape_latex(text)

    assert escaped == (
        r"R\&D improved 60\% using file\_name \#1 at \$5"
    )


def test_escape_latex_preserves_unicode_text() -> None:
    text = "Université de Sherbrooke — Québec"

    escaped = escape_latex(text)

    assert escaped == text


def test_escape_latex_handles_all_supported_special_characters() -> None:
    text = r"\{}$&#_%~^"

    escaped = escape_latex(text)

    assert escaped == (
        r"\textbackslash{}"
        r"\{\}"
        r"\$"
        r"\&"
        r"\#"
        r"\_"
        r"\%"
        r"\textasciitilde{}"
        r"\textasciicircum{}"
    )