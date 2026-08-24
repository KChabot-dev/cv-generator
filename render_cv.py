from pathlib import Path

from cv_generator.domain.draft import CVDraft
from cv_generator.rendering.latex_renderer import LaTeXCVRenderer

RUN_ID = "RUN-20260824-171319"

RUN_DIRECTORY = (
    Path("artifacts")
    / "runs"
    / RUN_ID
)

DRAFT_PATH = RUN_DIRECTORY / "cv_draft.json"
TEX_PATH = RUN_DIRECTORY / "cv.tex"


def main() -> None:
    cv_draft = CVDraft.model_validate_json(
        DRAFT_PATH.read_text(
            encoding="utf-8",
        )
    )

    renderer = LaTeXCVRenderer()

    latex_source = renderer.render(cv_draft)

    TEX_PATH.write_text(
        latex_source,
        encoding="utf-8",
    )

    print(f"Rendered LaTeX to: {TEX_PATH}")


if __name__ == "__main__":
    main()