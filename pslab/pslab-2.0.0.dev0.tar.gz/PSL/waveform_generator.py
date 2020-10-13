import time

import numpy as np

import PSL.commands_proto as CP


class AnalogWaveformGenerator:

    def set_w1(self, freq, waveType=None):
        """
		Set the frequency of wavegen 1

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency to set on wave generator 1.
		waveType		'sine','tria' . Default : Do not reload table. and use last set table
		==============  ============================================================================================


		:return: frequency
		"""
        if freq < 0.1:
            self.__print__('freq too low')
            return 0
        elif freq < 1100:
            HIGHRES = 1
            table_size = 512
        else:
            HIGHRES = 0
            table_size = 32

        if waveType:  # User wants to set a particular waveform type. sine or tria
            if waveType in ['sine', 'tria']:
                if (self.WType['W1'] != waveType):
                    self.load_equation('W1', waveType)
            else:
                print('Not a valid waveform. try sine or tria')

        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = int(round(64e6 / freq / p[prescaler] / table_size))
            freq = (64e6 / wavelength / p[prescaler] / table_size)
            if wavelength < 65525: break
            prescaler += 1
        if prescaler == 4:
            self.__print__('out of range')
            return 0

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SINE1)
        self.H.__sendByte__(HIGHRES | (prescaler << 1))  # use larger table for low frequencies
        self.H.__sendInt__(wavelength - 1)
        self.H.__get_ack__()
        self.sine1freq = freq
        return freq

    def set_w2(self, freq, waveType=None):
        """
		Set the frequency of wavegen 2

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency to set on wave generator 1.
		==============  ============================================================================================

		:return: frequency
		"""
        if freq < 0.1:
            self.__print__('freq too low')
            return 0
        elif freq < 1100:
            HIGHRES = 1
            table_size = 512
        else:
            HIGHRES = 0
            table_size = 32

        if waveType:  # User wants to set a particular waveform type. sine or tria
            if waveType in ['sine', 'tria']:
                if (self.WType['W2'] != waveType):
                    self.load_equation('W2', waveType)
            else:
                print('Not a valid waveform. try sine or tria')

        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = int(round(64e6 / freq / p[prescaler] / table_size))
            freq = (64e6 / wavelength / p[prescaler] / table_size)
            if wavelength < 65525: break
            prescaler += 1
        if prescaler == 4:
            self.__print__('out of range')
            return 0

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SINE2)
        self.H.__sendByte__(HIGHRES | (prescaler << 1))  # use larger table for low frequencies
        self.H.__sendInt__(wavelength - 1)
        self.H.__get_ack__()
        self.sine2freq = freq

        return freq

    def set_waves(self, freq, phase, f2=None):
        """
		Set the frequency of wavegen

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency to set on both wave generators
		phase           Phase difference between the two. 0-360 degrees
		f2              Only specify if you require two separate frequencies to be set
		==============  ============================================================================================

		:return: frequency
		"""
        if f2:
            freq2 = f2
        else:
            freq2 = freq

        if freq < 0.1:
            self.__print__('freq1 too low')
            return 0
        elif freq < 1100:
            HIGHRES = 1
            table_size = 512
        else:
            HIGHRES = 0
            table_size = 32

        if freq2 < 0.1:
            self.__print__('freq2 too low')
            return 0
        elif freq2 < 1100:
            HIGHRES2 = 1
            table_size2 = 512
        else:
            HIGHRES2 = 0
            table_size2 = 32
        if freq < 1. or freq2 < 1.:
            self.__print__('extremely low frequencies will have reduced amplitudes due to AC coupling restrictions')

        p = [1, 8, 64, 256]
        prescaler1 = 0
        while prescaler1 <= 3:
            wavelength = int(round(64e6 / freq / p[prescaler1] / table_size))
            retfreq = (64e6 / wavelength / p[prescaler1] / table_size)
            if wavelength < 65525: break
            prescaler1 += 1
        if prescaler1 == 4:
            self.__print__('#1 out of range')
            return 0

        p = [1, 8, 64, 256]
        prescaler2 = 0
        while prescaler2 <= 3:
            wavelength2 = int(round(64e6 / freq2 / p[prescaler2] / table_size2))
            retfreq2 = (64e6 / wavelength2 / p[prescaler2] / table_size2)
            if wavelength2 < 65525: break
            prescaler2 += 1
        if prescaler2 == 4:
            self.__print__('#2 out of range')
            return 0

        phase_coarse = int(table_size2 * (phase) / 360.)
        phase_fine = int(wavelength2 * (phase - (phase_coarse) * 360. / table_size2) / (360. / table_size2))

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_BOTH_WG)

        self.H.__sendInt__(wavelength - 1)  # not really wavelength. time between each datapoint
        self.H.__sendInt__(wavelength2 - 1)  # not really wavelength. time between each datapoint
        self.H.__sendInt__(phase_coarse)  # table position for phase adjust
        self.H.__sendInt__(phase_fine)  # timer delay / fine phase adjust

        self.H.__sendByte__((prescaler2 << 4) | (prescaler1 << 2) | (HIGHRES2 << 1) | (
            HIGHRES))  # use larger table for low frequencies
        self.H.__get_ack__()
        self.sine1freq = retfreq
        self.sine2freq = retfreq2

        return retfreq

    def load_table(self, chan, points, mode='arbit', **kwargs):
        '''
		Load an arbitrary waveform table to the waveform generators

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		chan             The waveform generator to alter. 'W1' or 'W2'
		points          A list of 512 datapoints exactly
		mode			Optional argument. Type of waveform. default value 'arbit'. accepts 'sine', 'tria'
		==============  ============================================================================================

		example::

		  >>> self.I.load_waveform_table(1,range(512))
		  #Load sawtooth wave to wavegen 1
		'''
        self.__print__('reloaded wave table for %s : %s' % (chan, mode))
        self.WType[chan] = mode
        chans = ['W1', 'W2']
        if chan in chans:
            num = chans.index(chan) + 1
        else:
            print('Channel does not exist. Try W2 or W2')
            return

        # Normalize and scale .
        # y1 = array with 512 points between 0 and 512
        # y2 = array with 32 points between 0 and 64

        amp = kwargs.get('amp', 0.95)
        LARGE_MAX = 511 * amp  # A form of amplitude control. This decides the max PWM duty cycle out of 512 clocks
        SMALL_MAX = 63 * amp  # Max duty cycle out of 64 clocks
        y1 = np.array(points)
        y1 -= min(y1)
        y1 = y1 / float(max(y1))
        y1 = 1. - y1
        y1 = list(np.int16(np.round(LARGE_MAX - LARGE_MAX * y1)))

        y2 = np.array(points[::16])
        y2 -= min(y2)
        y2 = y2 / float(max(y2))
        y2 = 1. - y2
        y2 = list(np.int16(np.round(SMALL_MAX - SMALL_MAX * y2)))

        self.H.__sendByte__(CP.WAVEGEN)
        if (num == 1):
            self.H.__sendByte__(CP.LOAD_WAVEFORM1)
        elif (num == 2):
            self.H.__sendByte__(CP.LOAD_WAVEFORM2)

        for a in y1:
            self.H.__sendInt__(a)
        for a in y2:
            self.H.__sendByte__(CP.Byte.pack(a))
        time.sleep(0.01)
        self.H.__get_ack__()


class DigitalWaveformGenerator:

    def sqr1(self, freq, duty_cycle=50, onlyPrepare=False):
        """
		Set the frequency of sqr1

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency
		duty_cycle      Percentage of high time
		==============  ============================================================================================
		"""
        if freq == 0 or duty_cycle == 0: return None
        if freq > 10e6:
            print('Frequency is greater than 10MHz. Please use map_reference_clock for 16 & 32MHz outputs')
            return 0

        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = int(64e6 / freq / p[prescaler])
            if wavelength < 65525: break
            prescaler += 1
        if prescaler == 4 or wavelength == 0:
            self.__print__('out of range')
            return 0
        high_time = wavelength * duty_cycle / 100.
        self.__print__(wavelength, ':', high_time, ':', prescaler)
        if onlyPrepare: self.set_state(SQR1=False)

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SQR1)
        self.H.__sendInt__(int(round(wavelength)))
        self.H.__sendInt__(int(round(high_time)))
        if onlyPrepare: prescaler |= 0x4  # Instruct hardware to prepare the square wave, but do not connect it to the output.
        self.H.__sendByte__(prescaler)
        self.H.__get_ack__()

        self.sqrfreq['SQR1'] = 64e6 / wavelength / p[prescaler & 0x3]
        return self.sqrfreq['SQR1']

    def sqr1_pattern(self, timing_array):
        """
		output a preset sqr1 frequency in fixed intervals. Can be used for sending IR signals that are packets
		of 38KHz pulses.
		refer to the example

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		timing_array    A list of on & off times in uS units
		==============  ============================================================================================

		.. code-block:: python
			I.sqr1(38e3 , 50, True )   # Prepare a 38KHz, 50% square wave. Do not output it yet
			I.sqr1_pattern([1000,1000,1000,1000,1000])  #On:1mS (38KHz packet), Off:1mS, On:1mS (38KHz packet), Off:1mS, On:1mS (38KHz packet), Off: indefinitely..
		"""
        self.fill_buffer(self.MAX_SAMPLES / 2, timing_array)  # Load the array to the ADCBuffer(second half)

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SQR1_PATTERN)
        self.H.__sendInt__(len(timing_array))
        time.sleep(sum(timing_array) * 1e-6)  # Sleep for the whole duration
        self.H.__get_ack__()

        return True

    def sqr2(self, freq, duty_cycle):
        """
		Set the frequency of sqr2

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		frequency       Frequency
		duty_cycle      Percentage of high time
		==============  ============================================================================================
		"""
        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = 64e6 / freq / p[prescaler]
            if wavelength < 65525: break
            prescaler += 1

        if prescaler == 4 or wavelength == 0:
            self.__print__('out of range')
            return 0

        high_time = wavelength * duty_cycle / 100.
        self.__print__(wavelength, high_time, prescaler)
        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SQR2)
        self.H.__sendInt__(int(round(wavelength)))
        self.H.__sendInt__(int(round(high_time)))
        self.H.__sendByte__(prescaler)
        self.H.__get_ack__()

        self.sqrfreq['SQR2'] = 64e6 / wavelength / p[prescaler & 0x3]
        return self.sqrfreq['SQR2']

    def set_sqrs(self, wavelength, phase, high_time1, high_time2, prescaler=1):
        """
		Set the frequency of sqr1,sqr2, with phase shift

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		wavelength      Number of 64Mhz/prescaler clock cycles per wave
		phase           Clock cycles between rising edges of SQR1 and SQR2
		high time1      Clock cycles for which SQR1 must be HIGH
		high time2      Clock cycles for which SQR2 must be HIGH
		prescaler       0,1,2. Divides the 64Mhz clock by 8,64, or 256
		==============  ============================================================================================

		"""

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SET_SQRS)
        self.H.__sendInt__(wavelength)
        self.H.__sendInt__(phase)
        self.H.__sendInt__(high_time1)
        self.H.__sendInt__(high_time2)
        self.H.__sendByte__(prescaler)
        self.H.__get_ack__()

    def sqrPWM(self, freq, h0, p1, h1, p2, h2, p3, h3, **kwargs):
        """
		Initialize phase correlated square waves on SQR1,SQR2,SQR3,SQR4

		.. tabularcolumns:: |p{3cm}|p{11cm}|

		==============  ============================================================================================
		**Arguments**
		==============  ============================================================================================
		freq            Frequency in Hertz
		h0              Duty Cycle for SQR1 (0-1)
		p1              Phase shift for SQR2 (0-1)
		h1              Duty Cycle for SQR2 (0-1)
		p2              Phase shift for OD1  (0-1)
		h2              Duty Cycle for OD1  (0-1)
		p3              Phase shift for OD2  (0-1)
		h3              Duty Cycle for OD2  (0-1)
		==============  ============================================================================================

		"""
        if freq == 0 or h0 == 0 or h1 == 0 or h2 == 0 or h3 == 0: return 0
        if freq > 10e6:
            print('Frequency is greater than 10MHz. Please use map_reference_clock for 16 & 32MHz outputs')
            return 0

        p = [1, 8, 64, 256]
        prescaler = 0
        while prescaler <= 3:
            wavelength = int(64e6 / freq / p[prescaler])
            if wavelength < 65525: break
            prescaler += 1
        if prescaler == 4 or wavelength == 0:
            self.__print__('out of range')
            return 0

        if not kwargs.get('pulse', False): prescaler |= (1 << 5)

        A1 = int(p1 % 1 * wavelength)
        B1 = int((h1 + p1) % 1 * wavelength)
        A2 = int(p2 % 1 * wavelength)
        B2 = int((h2 + p2) % 1 * wavelength)
        A3 = int(p3 % 1 * wavelength)
        B3 = int((h3 + p3) % 1 * wavelength)

        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.SQR4)
        self.H.__sendInt__(wavelength - 1)
        self.H.__sendInt__(int(wavelength * h0) - 1)

        self.H.__sendInt__(max(0, A1 - 1))
        self.H.__sendInt__(max(1, B1 - 1))
        self.H.__sendInt__(max(0, A2 - 1))
        self.H.__sendInt__(max(1, B2 - 1))
        self.H.__sendInt__(max(0, A3 - 1))
        self.H.__sendInt__(max(1, B3 - 1))
        self.H.__sendByte__(prescaler)
        self.H.__get_ack__()

        for a in ['SQR1', 'SQR2', 'SQR3', 'SQR4']: self.sqrfreq[a] = 64e6 / wavelength / p[prescaler & 0x3]
        return 64e6 / wavelength / p[prescaler & 0x3]

    def map_reference_clock(self, scaler, *args):
        """
		Map the internal oscillator output  to SQR1,SQR2,SQR3,SQR4 or WAVEGEN
		The output frequency is 128/(1<<scaler) MHz

		scaler [0-15]

			* 0 -> 128MHz
			* 1 -> 64MHz
			* 2 -> 32MHz
			* 3 -> 16MHz
			* .
			* .
			* 15 ->128./32768 MHz

		example::

		>>> I.map_reference_clock(2,'SQR1','SQR2')

		outputs 32 MHz on SQR1, SQR2 pins

		.. note::
			if you change the reference clock for 'wavegen' , the external waveform generator(AD9833) resolution and range will also change.
			default frequency for 'wavegen' is 16MHz. Setting to 1MHz will give you 16 times better resolution, but a usable range of
			0Hz to about 100KHz instead of the original 2MHz.

		"""
        self.H.__sendByte__(CP.WAVEGEN)
        self.H.__sendByte__(CP.MAP_REFERENCE)
        chan = 0
        if 'SQR1' in args: chan |= 1
        if 'SQR2' in args: chan |= 2
        if 'SQR3' in args: chan |= 4
        if 'SQR4' in args: chan |= 8
        if 'WAVEGEN' in args: chan |= 16
        self.H.__sendByte__(chan)
        self.H.__sendByte__(scaler)
        if 'WAVEGEN' in args: self.DDS_CLOCK = 128e6 / (1 << scaler)
        self.H.__get_ack__()