from cv_generator.rendering.latex_renderer import (
    compact_education_date,
    escape_latex,
    humanize_label,
)


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

def test_compact_education_date_keeps_only_years() -> None:
    assert compact_education_date("2021–Present") == "2021–Present"
    assert (
        compact_education_date("2014–December 2018")
        == "2014–2018"
    )
    assert (
        compact_education_date("January 2011–December 2014")
        == "2011–2014"
    )

def test_humanize_label_formats_enum_style_values() -> None:
    assert humanize_label("native_or_bilingual") == "Native or bilingual"
    assert humanize_label("full_professional") == "Full professional"