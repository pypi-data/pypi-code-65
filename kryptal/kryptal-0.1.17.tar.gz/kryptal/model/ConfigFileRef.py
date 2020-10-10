from typing import Dict, Any
from typing_extensions import Final, final
import yaml


@final
class ConfigFileRef:
    def __init__(self, path: str):
        self._path: Final = path

    def load(self) -> Dict[str, Any]:
        with open(self._path, 'r') as stream:
            res: Dict[str, Any] = yaml.safe_load(stream)
            return res

    def save(self, data: Dict[str, Any]) -> None:
        with open(self._path, 'w') as stream:
            yaml.safe_dump(data, stream, default_flow_style=False)
