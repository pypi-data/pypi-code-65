from decimal import Decimal
from typing import List

from iflag import data
from iflag.parse import DatabaseRecordParameter

HOURLY_DB_52: List[DatabaseRecordParameter] = [
    DatabaseRecordParameter(name="record_duration", data_class=data.Byte),
    DatabaseRecordParameter(name="status", data_class=data.Byte),
    DatabaseRecordParameter(name="end_date", data_class=data.Date),
    DatabaseRecordParameter(
        name="consumption_unconverted_hourly",
        data_class=data.Word,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_converted_hourly",
        data_class=data.ULong,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="counter_unconverted_hourly",
        data_class=data.Word,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="counter_converted_hourly",
        data_class=data.ULong,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="temperature_hourly_minimum", data_class=data.Float1),
    DatabaseRecordParameter(name="temperature_hourly_maximum", data_class=data.Float1),
    DatabaseRecordParameter(name="temperature_hourly_average", data_class=data.Float1),
    DatabaseRecordParameter(name="pressure_hourly_minimum", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_hourly_maximum", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_hourly_average", data_class=data.Float2),
    DatabaseRecordParameter(
        name="flowrate_unconverted_hourly_minimum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_unconverted_hourly_maximum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_hourly_minimum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_hourly_maximum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="none_data_1", data_class=data.Null4),
    DatabaseRecordParameter(
        name="flowrate_unconverted_hourly_average",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_hourly_average",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="start_date", data_class=data.Date),
    DatabaseRecordParameter(name="none_data_2", data_class=data.Null2),
]

HOURLY_DB_90: List[DatabaseRecordParameter] = [
    DatabaseRecordParameter(name="record_duration", data_class=data.Byte),
    DatabaseRecordParameter(name="status", data_class=data.Byte),
    DatabaseRecordParameter(name="end_date", data_class=data.Date),
    DatabaseRecordParameter(
        name="consumption_unconverted_hourly",
        data_class=data.Word,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_converted_hourly",
        data_class=data.ULong,
        affected_by_pulse_input=True,
        multiplied=Decimal("1000"),
    ),
    DatabaseRecordParameter(
        name="consumption_unconverted_hourly_under_alarm",
        data_class=data.Word,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="consumption_converted_hourly_under_alarm",
        data_class=data.ULong,
        affected_by_pulse_input=True,
        multiplied=Decimal("1000"),
    ),
    DatabaseRecordParameter(name="temperature_hourly_minimum", data_class=data.Float1),
    DatabaseRecordParameter(name="temperature_hourly_maximum", data_class=data.Float1),
    DatabaseRecordParameter(name="temperature_hourly_average", data_class=data.Float1),
    DatabaseRecordParameter(name="pressure_hourly_minimum", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_hourly_maximum", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_hourly_average", data_class=data.Float2),
    DatabaseRecordParameter(
        name="flowrate_unconverted_hourly_minimum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_unconverted_hourly_maximum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_hourly_minimum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_hourly_maximum",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="calorific_value", data_class=data.Float),
    DatabaseRecordParameter(name="index_unconverted", data_class=data.Index),
    DatabaseRecordParameter(name="index_converted", data_class=data.Index),
    DatabaseRecordParameter(
        name="counter_unconverted_under_alarm", data_class=data.Index
    ),
    DatabaseRecordParameter(
        name="counter_converted_under_alarm", data_class=data.Index
    ),
    DatabaseRecordParameter(
        name="flowrate_unconverted_hourly_average",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(
        name="flowrate_converted_hourly_average",
        data_class=data.Float3,
        affected_by_pulse_input=True,
    ),
    DatabaseRecordParameter(name="start_date", data_class=data.Date),
    DatabaseRecordParameter(name="not_used", data_class=data.Null2),
    DatabaseRecordParameter(name="pressure_hourly_minimum_2", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_hourly_maximum_2", data_class=data.Float2),
    DatabaseRecordParameter(name="pressure_hourly_average_2", data_class=data.Float2),
]

HOURLY_DB_92: List[DatabaseRecordParameter] = HOURLY_DB_90 + [
    DatabaseRecordParameter(name="unknown", data_class=data.Null2)
]
