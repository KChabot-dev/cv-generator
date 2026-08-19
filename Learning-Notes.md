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