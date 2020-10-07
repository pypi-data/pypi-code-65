from decimal import Decimal
from typing import List

from iflag import data
from iflag.parse import DatabaseRecordParameter

MONTHLY_DB_103: List[DatabaseRecordParameter] = [
    DatabaseRecordParameter(name="record_duration", data_class=data.Word),
    DatabaseRecordParameter(name="status", data_class=data.Byte),
    DatabaseRecordParameter(name="end_date", data_class=data.Date),
    DatabaseRecordParameter(
        name="consumption_unconverted_monthly",
        data_class=data.EWord,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_converted_monthly",
        data_class=data.EULong,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="counter_unconverted_monthly",
        data_class=data.EWord,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="counter_converted_monthly",
        data_class=data.EULong,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="temperature_monthly_minimum", data_class=data.Float1),
    DatabaseRecordParameter(name="temperature_monthly_maximum", data_class=data.Float1),
    DatabaseRecordParameter(name="temperature_monthly_average", data_class=data.Float1),
    DatabaseRecordParameter(name="pressure_monthly_minimum", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_monthly_maximum", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_monthly_average", data_class=data.Float2),
    DatabaseRecordParameter(
        name="flowrate_unconverted_monthly_minimum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_unconverted_monthly_maximum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_monthly_minimum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_monthly_maximum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="none_data_1", data_class=data.Null4),
    DatabaseRecordParameter(name="index_unconverted", data_class=data.Index),
    DatabaseRecordParameter(name="index_converted", data_class=data.Index),
    DatabaseRecordParameter(
        name="counter_unconverted_under_alarm", data_class=data.Index
    ),
    DatabaseRecordParameter(
        name="counter_converted_under_alarm", data_class=data.Index
    ),
    DatabaseRecordParameter(
        name="consumption_unconverted_monthly_maximum",
        data_class=data.Word,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_unconverted_monthly_maximum_date", data_class=data.Date
    ),
    DatabaseRecordParameter(
        name="consumption_converted_monthly_maximum",
        data_class=data.ULong,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_converted_monthly_maximum_date", data_class=data.Date
    ),
    DatabaseRecordParameter(
        name="flowrate_unconverted_monthly_average",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_monthly_average",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="start_date", data_class=data.Date),
    DatabaseRecordParameter(name="none_data_2", data_class=data.Null2),
]

MONTHLY_DB_109: List[DatabaseRecordParameter] = [
    DatabaseRecordParameter(name="record_duration", data_class=data.Word),
    DatabaseRecordParameter(name="status", data_class=data.Byte),
    DatabaseRecordParameter(name="end_date", data_class=data.Date),
    DatabaseRecordParameter(
        name="consumption_unconverted_monthly",
        data_class=data.EWord,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_converted_monthly",
        data_class=data.EULong,
        affected_by_pulse_input=True,
        multiplied=Decimal("1000"),
    ),
    DatabaseRecordParameter(
        name="consumption_unconverted_monthly_under_alarm",
        data_class=data.EWord,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_converted_monthly_under_alarm",
        data_class=data.EULong,
        affected_by_pulse_input=True,
        multiplied=Decimal("1000"),
    ),
    DatabaseRecordParameter(name="temperature_monthly_minimum", data_class=data.Float1),
    DatabaseRecordParameter(name="temperature_monthly_maximum", data_class=data.Float1),
    DatabaseRecordParameter(name="temperature_monthly_average", data_class=data.Float1),
    DatabaseRecordParameter(name="pressure_monthly_minimum", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_monthly_maximum", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_monthly_average", data_class=data.Float2),
    DatabaseRecordParameter(
        name="flowrate_unconverted_monthly_minimum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_unconverted_monthly_maximum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_monthly_minimum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_monthly_maximum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="superior_calorific_value", data_class=data.Float),
    DatabaseRecordParameter(name="index_unconverted", data_class=data.Index),
    DatabaseRecordParameter(name="index_converted", data_class=data.Index),
    DatabaseRecordParameter(
        name="counter_unconverted_under_alarm", data_class=data.Index
    ),
    DatabaseRecordParameter(
        name="counter_converted_under_alarm", data_class=data.Index
    ),
    DatabaseRecordParameter(
        name="consumption_unconverted_monthly_maximum",
        data_class=data.Word,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_unconverted_monthly_maximum_date", data_class=data.Date
    ),
    DatabaseRecordParameter(
        name="consumption_converted_monthly_maximum",
        data_class=data.ULong,
        affected_by_pulse_input=True,
        multiplied=Decimal("1000")
    ),
    DatabaseRecordParameter(
        name="consumption_converted_monthly_maximum_date", data_class=data.Date
    ),
    DatabaseRecordParameter(
        name="flowrate_unconverted_monthly_average",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_monthly_average",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="start_date", data_class=data.Date),
    DatabaseRecordParameter(name="not_used", data_class=data.Null2),
    DatabaseRecordParameter(name="pressure_monthly_minimum_2", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_monthly_maximum_2", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_monthly_average_2", data_class=data.Float2),
]

MONTHLY_DB_111: List[DatabaseRecordParameter] = MONTHLY_DB_109 + [
    DatabaseRecordParameter(name="unknown", data_class=data.Null2)
]
