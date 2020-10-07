from pandas import DataFrame

from ds_methods.common.validators import check_keys
from ds_methods.common.df import DataFrameUtils
from ds_methods.common.types import MethodOutput

from ds_methods.methods.base import BaseMethod

from .schemas import options_schema


class FilterByFeaturesValues(BaseMethod):
    options_schema = options_schema

    def make_(self, input_data: DataFrame) -> MethodOutput:
        return MethodOutput(
            data=DataFrameUtils.eval_query(input_data, DataFrameUtils.compose_query(self.options)),
            error=None,
        )

    def validate_input_(self, input_data: DataFrame) -> bool:
        return check_keys(input_data, self.options.keys())
