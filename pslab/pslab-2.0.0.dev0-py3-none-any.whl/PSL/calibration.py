# Check for calibration data if connected, and process them if found.
# Load constants for CTMU and PCS.

PAGES = {
    "cap_and_pcs": 0,
    "adc_shifts_location1": 1,
    "adc_shifts_location2": 2,
    "adc_polynomials_location": 3,
    "dac_shifts_pv1a": 4,
    "dac_shifts_pv1b": 5,
    "dac_shifts_pv2a": 6,
    "dac_shifts_pv2b": 7,
    "dac_shifts_pv3a": 8,
    "dac_shifts_pv3b": 9,
}

cap_and_pcs = H.read_bulk_flash(page=PAGES["cap_and_pcs"], numbytes=5 + 8 * 4)  # READY+calibration_string
if cap_and_pcs[:5] == 'READY':
    scalers = list(struct.unpack('8f', cap_and_pcs[5:]))
    self.SOCKET_CAPACITANCE = scalers[0]
    self.DAC.CHANS['PCS'].load_calibration_twopoint(scalers[1],
                                                    scalers[2])  # Slope and offset for current source
    self.__calibrate_ctmu__(scalers[4:])
    self.resistanceScaling = scalers[3]  # SEN
    self.aboutArray.append(['Capacitance[sock,550uA,55uA,5.5uA,.55uA]'] + scalers[:1] + scalers[4:])
    self.aboutArray.append(['PCS slope,offset'] + scalers[1:3])
    self.aboutArray.append(['SEN'] + [scalers[3]])
else:
    self.SOCKET_CAPACITANCE = 42e-12  # approx
    self.__print__('Cap and PCS calibration invalid')  # ,cap_and_pcs[:10],'...')

# Load constants for ADC and DAC
polynomials = self.read_bulk_flash(self.ADC_POLYNOMIALS_LOCATION, 2048)
polyDict = {}
if polynomials[:9] == 'PSLab':
    self.__print__('ADC calibration found...')
    self.aboutArray.append(['Calibration Found'])
    self.aboutArray.append([])
    self.calibrated = True
    adc_shifts = self.read_bulk_flash(self.ADC_SHIFTS_LOCATION1, 2048) + self.read_bulk_flash(
        self.ADC_SHIFTS_LOCATION2, 2048)
    adc_shifts = [CP.Byte.unpack(a)[0] for a in adc_shifts]
    # print(adc_shifts)
    self.__print__('ADC INL correction table loaded.')
    self.aboutArray.append(['ADC INL Correction found', adc_shifts[0], adc_shifts[1], adc_shifts[2], '...'])
    poly_sections = polynomials.split(
        'STOP')  # The 2K array is split into sections containing data for ADC_INL fit, ADC_CHANNEL fit, DAC_CHANNEL fit, PCS, CAP ...

    adc_slopes_offsets = poly_sections[0]
    dac_slope_intercept = poly_sections[1]
    inl_slope_intercept = poly_sections[2]
    # print('COMMON#########',self.__stoa__(slopes_offsets))
    # print('DAC#########',self.__stoa__(dac_slope_intercept))
    # print('ADC INL ############',self.__stoa__(inl_slope_intercept),len(inl_slope_intercept))
    # Load calibration data for ADC channels into an array that'll be evaluated in the next code block
    for a in adc_slopes_offsets.split('>|')[1:]:
        self.__print__('\n', '>' * 20, a[:3], '<' * 20)
        self.aboutArray.append([])
        self.aboutArray.append(['ADC Channel', a[:3]])
        self.aboutArray.append(['Gain', 'X^3', 'X^2', 'X', 'C'])
        cals = a[5:]
        polyDict[a[:3]] = []
        for b in range(len(cals) // 16):
            try:
                poly = struct.unpack('4f', cals[b * 16:(b + 1) * 16])
            except:
                self.__print__(a[:3], ' not calibrated')
            self.__print__(b, poly)
            self.aboutArray.append([b] + ['%.3e' % v for v in poly])
            polyDict[a[:3]].append(poly)

    # Load calibration data (slopes and offsets) for ADC channels
    inl_slope_intercept = struct.unpack('2f', inl_slope_intercept)
    for a in self.analogInputSources:
        self.analogInputSources[a].loadCalibrationTable(adc_shifts, inl_slope_intercept[0],
                                                        inl_slope_intercept[1])
        if a in polyDict:
            self.__print__('loading polynomials for ', a, polyDict[a])
            self.analogInputSources[a].loadPolynomials(polyDict[a])
            self.analogInputSources[a].calibrationReady = True
        self.analogInputSources[a].regenerateCalibration()

    # Load calibration data for DAC channels
    for a in dac_slope_intercept.split('>|')[1:]:
        NAME = a[:3]  # Name of the DAC channel . PV1, PV2 ...
        self.aboutArray.append([])
        self.aboutArray.append(['Calibrated :', NAME])
        try:
            fits = struct.unpack('6f', a[5:])
            self.__print__(NAME, ' calibrated', a[5:])
        except:
            self.__print__(NAME, ' not calibrated', a[5:], len(a[5:]), a)
            continue
        slope = fits[0]
        intercept = fits[1]
        fitvals = fits[2:]
        if NAME in ['PV1', 'PV2', 'PV3']:
            '''
						DACs have inherent non-linear behaviour, and the following algorithm generates a correction
						array from the calibration data that contains information about the offset(in codes) of each DAC code.

						The correction array defines for each DAC code, the number of codes to skip forwards or backwards
						in order to output the most accurate voltage value.

						E.g. if Code 1024 was found to output a voltage corresponding to code 1030 , and code 1020 was found to output a voltage corresponding to code 1024,
						then correction array[1024] = -4 , correction_array[1030]=-6. Adding -4 to the code 1024 will give code 1020 which will output the
						correct voltage value expected from code 1024.

						The variables LOOKAHEAD and LOOKBEHIND define the range of codes to search around a particular DAC code in order to
						find the code with the minimum deviation from the expected value.

						'''
            DACX = np.linspace(self.DAC.CHANS[NAME].range[0], self.DAC.CHANS[NAME].range[1], 4096)
            if NAME == 'PV1':
                OFF = self.read_bulk_flash(self.DAC_SHIFTS_PV1A, 2048) + self.read_bulk_flash(
                    self.DAC_SHIFTS_PV1B, 2048)
            elif NAME == 'PV2':
                OFF = self.read_bulk_flash(self.DAC_SHIFTS_PV2A, 2048) + self.read_bulk_flash(
                    self.DAC_SHIFTS_PV2B, 2048)
            elif NAME == 'PV3':
                OFF = self.read_bulk_flash(self.DAC_SHIFTS_PV3A, 2048) + self.read_bulk_flash(
                    self.DAC_SHIFTS_PV3B, 2048)
            OFF = np.array([ord(data) for data in OFF])
            self.__print__('\n', '>' * 20, NAME, '<' * 20)
            self.__print__('Offsets :', OFF[:20], '...')
            fitfn = np.poly1d(fitvals)
            YDATA = fitfn(DACX) - (OFF * slope + intercept)
            LOOKBEHIND = 100
            LOOKAHEAD = 100
            OFF = np.array([np.argmin(
                np.fabs(YDATA[max(B - LOOKBEHIND, 0):min(4095, B + LOOKAHEAD)] - DACX[B])) - (
                                    B - max(B - LOOKBEHIND, 0)) for B in range(0, 4096)])
            self.aboutArray.append(['Err min:', min(OFF), 'Err max:', max(OFF)])
            self.DAC.CHANS[NAME].load_calibration_table(OFF)