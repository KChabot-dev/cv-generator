from pathlib import Path

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from cv_generator.domain.draft import CVDraft

LATEX_SPECIAL_CHARACTERS = {
    "\\": r"\textbackslash{}",
    "{": r"\{",
    "}": r"\}",
    "$": r"\$",
    "&": r"\&",
    "#": r"\#",
    "_": r"\_",
    "%": r"\%",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def escape_latex(text: str) -> str:
    return "".join(
        LATEX_SPECIAL_CHARACTERS.get(character, character)
        for character in text
    )


class LaTeXCVRenderer:
    def __init__(self) -> None:
        template_directory = (
            Path(__file__).parent / "templates"
        )

        self.environment = Environment(
            loader=FileSystemLoader(template_directory),
            undefined=StrictUndefined,
            autoescape=False,
            block_start_string="((*",
            block_end_string="*))",
            variable_start_string="(((",
            variable_end_string=")))",
            comment_start_string="((#",
            comment_end_string="#))",
        )

        self.environment.filters["latex"] = escape_latex

    def render(self, cv_draft: CVDraft) -> str:
        template = self.environment.get_template(
            "cv.tex.j2"
        )

        return template.render(
            cv=cv_draft,
        )