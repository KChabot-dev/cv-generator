import re
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

def compact_education_date(date_text: str) -> str:
    years = [
        str(year)
        for year in re.findall(
            r"\b(?:19|20)\d{2}\b",
            date_text,
        )
    ]

    if not years:
        return date_text

    if "Present" in date_text:
        return f"{years[0]}–Present"

    if len(years) >= 2:
        return f"{years[0]}–{years[-1]}"

    return years[0]

def humanize_label(value: str) -> str:
    return value.replace("_", " ").capitalize()

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
        self.environment.filters["education_date"] = (
            compact_education_date
        )
        self.environment.filters["humanize"] = humanize_label

    def render(self, cv_draft: CVDraft) -> str:
        template = self.environment.get_template(
            "cv.tex.j2"
        )

        return str(
            template.render(
                cv=cv_draft,
            )
        )