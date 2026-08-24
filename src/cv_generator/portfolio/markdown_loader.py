from pathlib import Path

from cv_generator.domain.portfolio import PortfolioContext, PortfolioDocument

EVIDENCE_DIRECTORIES = (
    Path("01-profile"),
    Path("02-experiences"),
    Path("03-projects"),
    Path("04-skills"),
    Path("sources/code-audit"),
)


class MarkdownPortfolioLoader:
    def __init__(self, portfolio_root: Path) -> None:
        self.portfolio_root = portfolio_root

    def load(self) -> PortfolioContext:
        if not self.portfolio_root.is_dir():
            raise FileNotFoundError(
                f"portfolio root does not exist: {self.portfolio_root}"
            )

        documents: list[PortfolioDocument] = []

        for relative_directory in EVIDENCE_DIRECTORIES:
            directory = self.portfolio_root / relative_directory

            if not directory.is_dir():
                continue

            for path in directory.rglob("*"):
                if not path.is_file():
                    continue

                if path.suffix.lower() != ".md":
                    continue

                if path.name.lower() == "readme.md":
                    continue

                content = path.read_text(encoding="utf-8")

                if not content.strip():
                    continue

                documents.append(
                    PortfolioDocument(
                        source_id=path.relative_to(
                            self.portfolio_root
                        ).as_posix(),
                        content=content,
                    )
                )

        documents.sort(key=lambda document: document.source_id)

        return PortfolioContext(documents=documents)