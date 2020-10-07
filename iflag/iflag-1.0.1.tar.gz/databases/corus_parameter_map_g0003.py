from iflag.parse import IFlagParameter
from iflag import data

PARAMETER_MAP_G0003 = {
    "firmware_version": IFlagParameter(0, data.CorusString),  # XPCFV
    "input_pulse_weight": IFlagParameter(1, data.Float),  # MVW1
    "parameter_mapping_version": IFlagParameter(0x5E, data.CorusString),  # XKEP, PVER
    "compressibility_formula": IFlagParameter(15, data.Byte),  # MCF
    "pressure_base": IFlagParameter(19, data.Float),  # MCRP
    "temperature_base": IFlagParameter(24, data.Float),  # MCRT
    "pressure_low": IFlagParameter(30, data.Float),  # MPTL
    "pressure_high": IFlagParameter(31, data.Float),  # MPTH
    "temperature_low": IFlagParameter(40, data.Float),  # MTTL
    "temperature_high": IFlagParameter(41, data.Float),  # MTTH
    "datetime": IFlagParameter(106, data.Date),  # XDC
    "battery_days": IFlagParameter(107, data.Word),  # XSBR
    "index_unconverted": IFlagParameter(148, data.Index),  # MVRI
    "index_converted": IFlagParameter(149, data.Index),  # MVBI
    "flowrate_unconverted": IFlagParameter(152, data.Float),  # MFRG
    "flowrate_converted": IFlagParameter(153, data.Float),  # MFBG
    "temperature": IFlagParameter(158, data.Float),  # MTG
    "pressure": IFlagParameter(159, data.Float),  # MPG
}
