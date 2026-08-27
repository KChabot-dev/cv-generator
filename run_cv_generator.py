from datetime import datetime
from pathlib import Path

from cv_generator.adapters.codex_cv_planner import CodexCVPlanner
from cv_generator.adapters.codex_cv_writer import CodexCVWriter
from cv_generator.adapters.codex_evidence_matcher import CodexEvidenceMatcher
from cv_generator.adapters.codex_job_analyzer import CodexJobAnalyzer
from cv_generator.application.pipeline import run_pipeline
from cv_generator.persistence.artifact_paths import ArtifactPaths
from cv_generator.persistence.artifact_store import ArtifactStore
from cv_generator.portfolio.markdown_loader import MarkdownPortfolioLoader

JOB_POSTING_PATH = Path("job_posting.txt")
PORTFOLIO_PATH = Path("../Professional-Portfolio")
ARTIFACTS_PATH = Path("artifacts")


def main() -> None:
    job_text = JOB_POSTING_PATH.read_text(
        encoding="utf-8"
    )

    store = ArtifactStore(
        paths=ArtifactPaths(
            root=ARTIFACTS_PATH,
        )
    )

    candidate_profile = store.load_candidate_profile()

    portfolio_context = MarkdownPortfolioLoader(
        PORTFOLIO_PATH
    ).load()

    run_id = datetime.now().strftime(
        "RUN-%Y%m%d-%H%M%S"
    )

    run_directory = store.paths.run_directory(run_id)
    run_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        run_directory / "job_posting.txt"
    ).write_text(
        job_text,
        encoding="utf-8",
    )

    print(f"Run: {run_id}")
    print(
        "Portfolio documents loaded: "
        f"{len(portfolio_context.documents)}"
    )

    print()
    print("Running CV pipeline...")
    print()

    cv_draft, report = run_pipeline(
        run_id=run_id,
        job_text=job_text,
        candidate_profile=candidate_profile,
        portfolio_context=portfolio_context,
        analyzer=CodexJobAnalyzer(),
        matcher=CodexEvidenceMatcher(),
        planner=CodexCVPlanner(),
        writer=CodexCVWriter(),
        store=store,
    )

    print()
    print(
        "Validation issues: "
        f"{len(report.issues)}"
    )

    for issue in report.issues:
        print(
            f"- {issue.stage}: "
            f"{issue.code}: "
            f"{issue.message}"
        )

    if cv_draft is None:
        print()
        print(
            "Pipeline stopped before producing "
            "a valid CV draft."
        )
        print(
            "Artifacts saved to: "
            f"{run_directory}"
        )
        return

    draft_path = store.paths.cv_draft(run_id)

    print()
    print("CV draft generated and validated successfully.")
    print()
    print(
        "Review this file before rendering:"
    )
    print(
        draft_path.resolve()
    )

    print()
    print("Rendering has NOT been performed.")


if __name__ == "__main__":
    main()