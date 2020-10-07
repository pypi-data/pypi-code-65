from iflag.parse import IFlagParameter
from iflag import data

PARAMETER_MAP_M5A00 = {
    "firmware_version": IFlagParameter(75, data.CorusString),  # XPCFV
    "kernel_version": IFlagParameter(0, data.CorusString),  # XPCKV
    "input_pulse_weight": IFlagParameter(1, data.Float),  # MVW1
    "parameter_mapping_version": IFlagParameter(0x5E, data.CorusString),  # XKEP, PVER
    "compressibility_formula": IFlagParameter(6, data.Byte),  # MCF
    "pressure_base": IFlagParameter(10, data.Float),  # MCRP
    "temperature_base": IFlagParameter(15, data.Float),  # MCRT
    "pressure_low": IFlagParameter(45, data.Float),  # MPTL
    "pressure_high": IFlagParameter(46, data.Float),  # MPTH
    "temperature_low": IFlagParameter(55, data.Float),  # MTTL
    "temperature_high": IFlagParameter(56, data.Float),  # MTTH
    "datetime": IFlagParameter(91, data.Date),  # XDC
    "battery_days": IFlagParameter(92, data.Word),  # XSBR
    "index_unconverted": IFlagParameter(108, data.Index9),  # MVRI
    "index_converted": IFlagParameter(109, data.Index9),  # MVBI
    "flowrate_unconverted": IFlagParameter(280, data.Float),  # MFRG
    "flowrate_converted": IFlagParameter(281, data.Float),  # MFBG
    "temperature": IFlagParameter(116, data.Float),  # MTG
    "pressure": IFlagParameter(117, data.Float),  # MPG
    "pressure_2": IFlagParameter(392, data.Float)  # MP2G
}
