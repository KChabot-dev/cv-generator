# CV Generator

A Python application that generates evidence-grounded, job-specific CV drafts from a structured candidate profile and a curated professional portfolio.

## How it works

```text
Job posting
    ↓
Job analysis
    ↓
Evidence matching
    ↓
CV planning
    ↓
CV writing
    ↓
Validation
    ↓
Human review
    ↓
LaTeX rendering
```

The pipeline uses typed Pydantic models and persists intermediate JSON artifacts so each stage can be inspected and validated independently.

## Highlights

- Evidence-grounded CV generation with source provenance
- Typed domain models and schema-constrained AI outputs
- Ports-and-adapters architecture with Protocol-based interfaces
- Deterministic cross-model validation and fail-fast behavior
- Markdown portfolio loading with stable source identifiers
- Jinja2 / LaTeX rendering
- Regression tests for observed pipeline failures

## Tech stack

Python · Pydantic · Jinja2 · LaTeX · pytest · mypy · Ruff · Codex CLI

## Development

Install dependencies:

`uv sync`

Run quality checks:

`uv run ruff check .`

`uv run mypy src tests`

`uv run pytest`

Run the CV-generation pipeline:

`uv run python run_cv_generator.py`

Render the latest validated draft:

`uv run python render_cv.py`

## Current status

V1 is functional end-to-end and has been exercised with real job postings and a real professional portfolio.

The professional portfolio, candidate data, job postings, and generated runtime artifacts are intentionally excluded from this repository.

## Documentation

See `Architecture.md`, `Data-Models.md`, and `Decisions.md` for the main design documentation.

## Fonts

Raleway font assets are distributed under the SIL Open Font License 1.1. See `src/cv_generator/rendering/assets/fonts/OFL.txt`.
