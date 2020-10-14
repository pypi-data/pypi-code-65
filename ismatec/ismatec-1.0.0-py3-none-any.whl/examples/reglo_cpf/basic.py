import time
import logging
from ismatec.piston_pump import RegloCPF
from ismatec.errors import PumpError, PumpOverloadError, CommandError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

if __name__ == '__main__':
    # connect to pump
    port = 'COM7'
    cpf = RegloCPF(port)
    cpf.set_control_panel_manual()
    cpf.set_default_values()
    cpf.stop()

    # commands - controlling the drive
    # todo commented out in case pump isn't set up with tubing. but this does work
    # cpf.start()
    # time.sleep(0.5)
    # cpf.stop()
    cpf.set_revolution_counter_clockwise()
    cpf.set_revolution_clockwise()
    cpf.set_control_panel_manual()
    cpf.inactivate_control_panel()
    cpf.write_to_control_panel('HI')
    cpf.write_to_control_panel(-2.456)
    cpf.set_control_panel_manual()

    # commands - selecting the operating modes
    for mode in RegloCPF._MODES:
        cpf.set_mode(mode)
    cpf.read_current_mode()
    cpf.set_mode_pump_rpm()

    # commands - inquiring and setting parameters
    logger.debug(cpf.pump_type_software_version)
    logger.debug(cpf.pump_version)
    logger.debug(cpf.n_digits_after_decimal)

    pump_head_id = cpf.pump_head_id_number
    logger.debug(pump_head_id)
    # todo setting didnt work in testing except for setting it to the current pump head id
    # cpf.pump_head_id_number = 30
    # if cpf.pump_head_id_number != 30:
    #     logger.warning('failed to set pump id')
    # cpf.pump_head_id_number = pump_head_id

    default_speed = cpf.speed
    cpf.speed = 1234
    if cpf.speed != 1234:
        logger.warning('failed to set pump speed')
    try:
        cpf.speed = 2000
    except CommandError:
        logger.debug('successfully caught speed command error')
    cpf.speed = default_speed

    logger.debug(cpf.default_flow_rate)
    cpf.flow_rate = '1234E-2'
    if 1235E-2 < cpf.flow_rate < 1235E-2:
        logger.warning('failed to set flow rate')

    # todo not working in Windows 10
    # logger.debug(cpf.calibrated_flow_rate)
    # cpf.calibrated_flow_rate = 12.34
    # if cpf.calibrated_flow_rate != 12.34:
    #     logger.warning('failed to set calibrated flow rate')

    default_dispensing_time = cpf.dispensing_time
    cpf.set_dispensing_time_s(5)
    if cpf.dispensing_time != 5:
        logger.warning('failed to set dispensing time in seconds')
    cpf.set_dispensing_time_m(5)
    if cpf.dispensing_time != 5*60:
        logger.warning('failed to set dispensing time in minutes')
    cpf.set_dispensing_time_h(5)
    if cpf.dispensing_time != 5*60*60:
        logger.warning('failed to set dispensing time in hours')
    cpf.set_dispensing_time_s(int(default_dispensing_time))

    default_piston_strokes_dispense_mode = cpf.dispense_mode_piston_strokes
    cpf.dispense_mode_piston_strokes = 62000
    if cpf.dispense_mode_piston_strokes != 62000:
        logger.warning('failed to set dispense mode piston strokes - small number')
    cpf.dispense_mode_piston_strokes = 100000
    if 99999 < cpf.dispense_mode_piston_strokes < 100001:
        logger.warning('failed to set dispense mode piston strokes - large number')

    current_piston_stroke_volume = cpf.piston_stroke_volume
    logger.debug(current_piston_stroke_volume)
    # todo set default currently not working and set piston stroke volume, might need to test with actual tubing
    # default_piston_stroke_volume = cpf.set_roller_default_volume()
    # cpf.piston_stroke_volume = '2345E-1'
    # if cpf.piston_stroke_volume != 2345E-1:
    #     logger.warning('failed to set piston stroke volume')

    default_dispensing_volume = cpf.dispensing_volume
    logger.debug(default_dispensing_volume)
    cpf.dispensing_volume = '6320E+2'
    if cpf.dispensing_volume != 6320E+2:
        logger.warning('failed to set dispensing volume')

    cpf.set_dispense_mode_dispense_volume(50)
    cpf.set_dispense_mode_dispense_volume(400.00)  # can have up to 2 decimal places

    default_piston_back_steps = cpf.piston_stroke_back_steps
    cpf.piston_stroke_back_steps = 50
    if cpf.piston_stroke_back_steps != 50:
        logger.warning('failed to set dispense mode piston strokes - small number')
    cpf.piston_stroke_back_steps = default_piston_back_steps
    try:
        cpf.piston_stroke_back_steps = 200
    except CommandError:
        logger.debug('Caught piston stroke back steps error successfully')

    default_pause_time = cpf.pause_time
    cpf.set_pause_time_s(5)
    if cpf.pause_time != 5:
        logger.warning('failed to set pause time in seconds')
    cpf.set_pause_time_m(5)
    if cpf.pause_time != 5*60:
        logger.warning('failed to set pause time in minutes')
    cpf.set_pause_time_h(5)
    if cpf.pause_time != 5*60*60:
        logger.warning('failed to set pause time in hours')
    cpf.set_pause_time_s(int(default_pause_time))

    default_dispensing_cycles = cpf.dispense_cycles
    cpf.dispense_cycles = 50
    if cpf.dispense_cycles != 50:
        logger.warning('failed to set dispensing cycles')
    cpf.dispense_cycles = default_dispensing_cycles
    try:
        cpf.dispense_cycles = 10000
    except CommandError:
        logger.debug('Caught dispensing cycles error successfully')

    logger.debug(cpf.total_volume)
    cpf.reset_total_volume()
    if cpf.total_volume != 0:
        logger.warning('failed to reset total volume')

    # commands - inputs and outputs
    logger.debug(cpf.footswitch)
    cpf.set_footswitch_mode_toggle()
    cpf.set_footswitch_mode_direct()

    cpf.set_default_values()
    cpf.store_application_parameters()



