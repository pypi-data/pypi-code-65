from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class BlueprintMetadata:
    """
    Class representing the metadata for a blueprint
    """

    tags: List[str]
    inputs: Dict[str, Any]
