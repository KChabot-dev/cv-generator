from pathlib import Path

from cv_generator.domain.draft import CVDraft
from cv_generator.rendering.latex_renderer import LaTeXCVRenderer

RUNS_DIRECTORY = Path("artifacts") / "runs"


def find_latest_draft() -> Path:
    draft_paths = list(
        RUNS_DIRECTORY.glob("RUN-*/cv_draft.json")
    )

    if not draft_paths:
        raise RuntimeError(
            "No cv_draft.json found in artifacts/runs."
        )

    return max(
        draft_paths,
        key=lambda path: path.stat().st_mtime,
    )


def main() -> None:
    draft_path = find_latest_draft()
    run_directory = draft_path.parent
    tex_path = run_directory / "cv.tex"

    print(f"Using CV draft: {draft_path}")

    cv_draft = CVDraft.model_validate_json(
        draft_path.read_text(
            encoding="utf-8",
        )
    )

    renderer = LaTeXCVRenderer()

    latex_source = renderer.render(cv_draft)

    tex_path.write_text(
        latex_source,
        encoding="utf-8",
    )

    print(f"Rendered LaTeX to: {tex_path}")


if __name__ == "__main__":
    main()