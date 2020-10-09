from pulse_pal.pulse_pal import PulsePalObject  # Import PulsePalObject
import time

def photometry_pulses(acquisition_freq, stim_duration=1*30):
    myPulsePal = PulsePalObject()  # Create a new instance of a PulsePal object
    myPulsePal.connect(serialPortName='COM10')  # Connect to PulsePal on port COM# (
    assert acquisition_freq in [20, 40], NotImplemented('asdf')
    if acquisition_freq == 40:
        photo_up_time = 0.017
        photo_down_time = 0.008
    elif acquisition_freq == 20:
        photo_up_time = 0.035
        photo_down_time = 0.015

    myPulsePal.setDisplay("Stimming", "")
    myPulsePal.programOutputChannelParam('isBiphasic', 1, 0)
    myPulsePal.programOutputChannelParam('phase1Voltage', 1, 5)
    myPulsePal.programOutputChannelParam('interPulseInterval', 1, photo_down_time)
    myPulsePal.programOutputChannelParam('restingVoltage', 1, 0)
    myPulsePal.programOutputChannelParam('phase1Duration', 1, photo_up_time)
    myPulsePal.programOutputChannelParam('pulseTrainDuration', 1, stim_duration)
    myPulsePal.programOutputChannelParam('pulseTrainDelay', 1, 0)
    myPulsePal.triggerOutputChannels(1, 0, 0, 0)
    msg = input('Type x and hit enter to stop pulses \n')
    if msg == 'x':
        myPulsePal.abortPulseTrains()

    else:
        time.sleep(stim_duration)

    myPulsePal.setDisplay("Done", " Click for menu")

    myPulsePal.disconnect()
