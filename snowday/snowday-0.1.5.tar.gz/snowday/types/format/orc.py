from dataclasses import dataclass
from typing import Union
from snowday.types.format.base import BaseFormatOptions
from snowday.types.base import Sql


@dataclass
class OrcFormatOptions(BaseFormatOptions):
    trim_space: bool = False
    null_if: str = ""

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=(f"trim_space = {self.trim_space} " f"null_if = ({self.null_if})")
        )
