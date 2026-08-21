from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)

def save_json(model: BaseModel, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        model.model_dump_json(indent=2),
        encoding="utf-8",
    )

def load_json(
    model_type: type[ModelT],
    path: Path,
) -> ModelT:
    json_data = path.read_text(encoding="utf-8")
    return model_type.model_validate_json(json_data)