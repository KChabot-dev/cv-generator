import json
import subprocess
from pathlib import Path

import pytest
from pydantic import BaseModel, Field

from cv_generator.adapters.codex_runner import CodexStructuredRunner


class ExampleOutput(BaseModel):
    message: str
    tags: list[str] = Field(default_factory=list)


def test_codex_runner_returns_structured_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    received_command: list[str] = []
    received_prompt = ""

    def fake_run(
        command: list[str],
        *,
        input: str,
        text: bool,
        encoding: str,
        capture_output: bool,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        nonlocal received_command, received_prompt

        received_command = command
        received_prompt = input

        schema_path = Path(
            command[
                command.index("--output-schema") + 1
            ]
        )
        result_path = Path(
            command[
                command.index("--output-last-message") + 1
            ]
        )

        schema = json.loads(
            schema_path.read_text(encoding="utf-8")
        )

        assert schema["required"] == [
            "message",
            "tags",
        ]
        assert schema["additionalProperties"] is False
        assert "default" not in schema["properties"]["tags"]

        result_path.write_text(
            ExampleOutput(
                message="Structured result",
                tags=[],
            ).model_dump_json(),
            encoding="utf-8",
        )

        assert encoding == "utf-8"

        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout="",
            stderr="",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    runner = CodexStructuredRunner(
        executable="codex-test"
    )

    result = runner.run(
        "Test structured prompt",
        ExampleOutput,
    )

    assert result == ExampleOutput(
        message="Structured result",
        tags=[],
    )

    assert received_prompt == "Test structured prompt"
    assert received_command[0] == "codex-test"
    assert "--output-schema" in received_command
    assert "--output-last-message" in received_command
    assert "--sandbox" in received_command
    assert "read-only" in received_command
    assert "--ephemeral" in received_command
    assert received_command[-1] == "-"


def test_codex_runner_reports_cli_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_run(
        command: list[str],
        *,
        input: str,
        text: bool,
        encoding: str,
        capture_output: bool,
        check: bool,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            args=command,
            returncode=1,
            stdout="",
            stderr="Codex failed",
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    runner = CodexStructuredRunner(
        executable="codex-test"
    )

    with pytest.raises(RuntimeError) as exc_info:
        runner.run(
            "Test prompt",
            ExampleOutput,
        )

    error_message = str(exc_info.value)

    assert "Codex structured execution failed" in error_message
    assert "Codex failed" in error_message