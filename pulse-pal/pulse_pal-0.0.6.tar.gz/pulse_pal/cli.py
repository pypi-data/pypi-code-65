"""Console script for pulse_pal."""
import sys
import click
from pulse_pal import pulse_pal


def test_pulse_pal(serialPortName='COM10'):
    import serial, struct

    OpMenuByte = 213
    serialObject = serial.Serial(serialPortName, 115200, timeout=1)
    handshakeByteString = struct.pack('BB', OpMenuByte, 72)
    serialObject.write(handshakeByteString)
    Response = serialObject.read(5)
    print(len(Response))


@click.command()
@click.option('--do', default='test', help='test or set or trigger')
@click.option('--port', default='COM1')
@click.option('--param_name')
@click.option('--channel', default=1)
@click.option('--param_value')
def main(do='test', port='COM1', param_name=None, channel=1, param_value=None):
    """Console script for pulse_pal."""
    if do == 'test':
        test_pulse_pal(serialPortName=port)
    elif do == 'set':
        obj = pulse_pal.PulsePalObject.connect(serialPortName=port)
        pulse_pal.PulsePalObject.programOutputChannelParam(obj,
                                                           paramName=param_name,
                                                           channel=channel,
                                                           value=param_value)
    elif do == 'trigger':
        obj = pulse_pal.PulsePalObject.connect(serialPortName=port)
        chans = [0,0,0,0]
        chans[channel] = 1
        obj.triggerOutputChannels(*chans)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
