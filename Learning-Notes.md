# Learning Notes

## Python Project Environment and Tooling

- An IDE such as VS Code or PyCharm is an interface over the underlying development tools; the project should remain usable independently of the IDE.
- A virtual environment provides an isolated Python runtime context for a project.
- `pyproject.toml` declares project metadata, Python requirements, dependencies, build configuration, and tool configuration.
- `uv` resolves and manages project dependencies and environments.
- `uv.lock` records the resolved dependency solution for reproducibility.
- Runtime dependencies and development dependencies serve different purposes.
- pytest tests software behavior.
- Ruff performs linting/formatting and other code-quality checks.
- mypy performs static type checking.
- CI can later automate these checks whenever code changes are pushed.

## Domain Models, Validation, and Testing

- Pydantic models define both the structure of domain data and runtime validation rules.
- `model_validator(mode="after")` is useful for invariants involving multiple fields.
- Generic reusable logic should be separated from domain-specific business rules when appropriate.
- Unit tests should protect meaningful behavior, edge cases, and regressions rather than test library behavior unnecessarily.
- Tests remain part of the codebase and help detect regressions during refactoring.
- pytest, Ruff, and mypy cover different concerns:
  - pytest: behavioral correctness
  - Ruff: code quality and consistency
  - mypy: static type consistency
- A failing test during the `EducationRecord` refactor successfully detected that an existing business rule had been removed.