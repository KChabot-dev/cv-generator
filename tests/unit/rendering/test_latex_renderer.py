from cv_generator.domain.draft import (
    ApplicationReference,
    CandidateHeader,
    CVDraft,
    DraftProject,
    ExperienceBullet,
    ProfessionalSummary,
)
from cv_generator.rendering.latex_renderer import (
    LaTeXCVRenderer,
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


def test_renderer_includes_selected_project() -> None:
    cv_draft = CVDraft(
        application_reference=ApplicationReference(
            company="Example Company",
            job_title="Scientific Software Engineer",
            job_spec_ref="JOB-001",
            content_plan_ref="CVContentPlan",
        ),
        header=CandidateHeader(
            full_name="Kevin Chabot",
        ),
        professional_summary=ProfessionalSummary(
            text="Scientific software developer.",
        ),
        projects=[
            DraftProject(
                title="Automated CV Generator",
                date_text="2026–Present",
                bullets=[
                    ExperienceBullet(
                        text=(
                            "Designed a typed Python application "
                            "using Pydantic."
                        ),
                    ),
                    ExperienceBullet(
                        text=(
                            "Added cross-model validation and "
                            "pytest regression tests."
                        ),
                    ),
                ],
            )
        ],
    )

    rendered = LaTeXCVRenderer().render(cv_draft)

    assert "Selected Project" in rendered
    assert "Automated CV Generator" in rendered
    assert "2026–Present" in rendered
    assert "Designed a typed Python application using Pydantic." in rendered
    assert (
        "Added cross-model validation and pytest regression tests."
        in rendered
    )