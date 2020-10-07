from pandas import DataFrame

from ds_methods.common.validators import check_keys, check_datetime
from ds_methods.common.df import DataFrameUtils
from ds_methods.common.types import MethodOutput

from ds_methods.methods.base import BaseMethod

from .schemas import BoxPlotType, options_schema


class BoxPlot(BaseMethod):
    options_schema = options_schema

    def make_(self, input_data: DataFrame) -> MethodOutput:
        numeric_part, _ = DataFrameUtils.decompose(input_data)
        box_plot_type = self.options['type']
        if box_plot_type == BoxPlotType.FEATURES:
            numeric_part = self.features(input_data)
        elif box_plot_type == BoxPlotType.DAYS:
            numeric_part = self.days(input_data)

        return MethodOutput(
            data=numeric_part,
            error=None,
        )

    @staticmethod
    def features(input_data: DataFrame) -> DataFrame:
        return input_data.quantile([0.01, 0.25, 0.5, 0.75, 0.99])

    @staticmethod
    def days(input_data: DataFrame) -> DataFrame:
        return BoxPlot.features(input_data.groupby(input_data['date'].dt.date))

    def validate_input_(self, input_data: DataFrame):
        if self.options['type'] == BoxPlotType.DAYS:
            return check_keys(input_data, 'date') and check_datetime(input_data['date'])

        return True
