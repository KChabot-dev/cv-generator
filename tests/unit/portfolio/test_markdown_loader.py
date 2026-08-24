from pathlib import Path

import pytest

from cv_generator.portfolio.markdown_loader import MarkdownPortfolioLoader


def write_file(root: Path, relative_path: str, content: str) -> None:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_loader_loads_only_curated_non_empty_markdown(
    tmp_path: Path,
) -> None:
    write_file(
        tmp_path,
        "04-skills/Scientific-Software-Development.md",
        "# Scientific Software Development",
    )
    write_file(
        tmp_path,
        "02-experiences/Graduate-Researcher.md",
        "# Graduate Researcher",
    )

    write_file(
        tmp_path,
        "04-skills/README.md",
        "# Skills Index",
    )
    write_file(
        tmp_path,
        "04-skills/Empty.md",
        "   ",
    )
    write_file(
        tmp_path,
        "AI Instructions.md",
        "# Instructions",
    )
    write_file(
        tmp_path,
        "04-skills/notes.txt",
        "not markdown",
    )

    context = MarkdownPortfolioLoader(tmp_path).load()

    assert [document.source_id for document in context.documents] == [
        "02-experiences/Graduate-Researcher.md",
        "04-skills/Scientific-Software-Development.md",
    ]


def test_loader_rejects_missing_portfolio_root(
    tmp_path: Path,
) -> None:
    missing_root = tmp_path / "does-not-exist"

    loader = MarkdownPortfolioLoader(missing_root)

    with pytest.raises(FileNotFoundError):
        loader.load()