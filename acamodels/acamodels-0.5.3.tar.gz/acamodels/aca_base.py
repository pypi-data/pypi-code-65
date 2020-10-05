# -----------------------------------------------------------------------------
# Imports
# -----------------------------------------------------------------------------

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel

# -----------------------------------------------------------------------------
# ACA Base model
# -----------------------------------------------------------------------------


class ACABase(BaseModel):
    """Base model with reusable methods & settings"""

    def dump(self, to_file: Path) -> None:
        data = super().json(indent=2, ensure_ascii=False)
        to_file.write_text(data, encoding="utf-8")

    def encode(self) -> Any:
        encoded_data = json.loads(super().json(ensure_ascii=False))
        return encoded_data
