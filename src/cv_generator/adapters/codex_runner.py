import json
import subprocess
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from pydantic import BaseModel


class CodexStructuredRunner:
    def __init__(self, executable: str = "codex.cmd") -> None:
        self.executable = executable

    def run[ModelT: BaseModel](
        self,
        prompt: str,
        model_type: type[ModelT],
    ) -> ModelT:
        with TemporaryDirectory() as temp_directory:
            temp_path = Path(temp_directory)
            schema_path = temp_path / "output_schema.json"
            result_path = temp_path / "output_result.json"

            schema = _make_codex_compatible_schema(
                model_type.model_json_schema()
            )

            schema_path.write_text(
                json.dumps(
                    schema,
                    indent=2,
                ),
                encoding="utf-8",
            )

            completed_process = subprocess.run(
                [
                    self.executable,
                    "exec",
                    "--sandbox",
                    "read-only",
                    "--ephemeral",
                    "--output-schema",
                    str(schema_path),
                    "--output-last-message",
                    str(result_path),
                    "--color",
                    "never",
                    "-",
                ],
                input=prompt,
                text=True,
                encoding="utf-8",
                capture_output=True,
                check=False,
            )

            if completed_process.returncode != 0:
                raise RuntimeError(
                    "Codex structured execution failed\n"
                    f"Return code: {completed_process.returncode}\n"
                    f"STDOUT:\n{completed_process.stdout}\n"
                    f"STDERR:\n{completed_process.stderr}"
                )

            if not result_path.is_file():
                raise RuntimeError(
                    "Codex structured execution did not produce a result file"
                )

            result_json = result_path.read_text(
                encoding="utf-8"
            )

            return model_type.model_validate_json(
                result_json
            )


def _make_codex_compatible_schema(
    schema: dict[str, object],
) -> dict[str, object]:
    codex_schema = deepcopy(schema)
    _make_all_properties_required(codex_schema)
    return codex_schema


def _make_all_properties_required(node: object) -> None:
    if isinstance(node, dict):
        node.pop("default", None)

        properties = node.get("properties")

        if isinstance(properties, dict):
            node["required"] = list(properties.keys())
            node["additionalProperties"] = False

        for value in node.values():
            _make_all_properties_required(value)

    elif isinstance(node, list):
        for item in node:
            _make_all_properties_required(item)