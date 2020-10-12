from simpleoptics.helpers.preambule import *

from simpleoptics.epsilon_data.formulas import *

import warnings

class Waveguide:

    ''' There are properties that the Waveguide class possesses even before the
        simulation set up and run. They are as follows.

        * when a waveguide is instanced:
            substrate, core, cladding as names, i.e. strings
            width, height as values

        * when a simulation is instanced the waveguide _instance_ obtains:
            start, stop, points as values to latter calculate
            substrate_epsr, core_epsr, cladding_epsr as values
            units as strings

        * After the simulation has been run the waveguide instance obtains:
            polarisation, modeclass, method as strings
            beta, betanorm as values
            ng, vg, D, GDD as values
            ex, ey, ez, hx, hy, hz as arrays as well as normes and powers
    '''

    def __init__(self,  core   = None, cladding = None, substrate = None,
                        height = None, width = None,
                        _start=None, _stop=None, _points=None):

        ''' the empty properties will be set after the simulation has been run,
            so I do not see a possibility to set them '''
        self.substrate = substrate
        self.core = core
        self.cladding = cladding

        ''' width can't be False even in planar because we have to
            calculate norms afterwards '''
        self.height = height
        if width==None:
            self._geometry='planar'
        else:pass
        self.width = width

    ''' this is what we got after the simulation has been set up '''
    @property
    def units(self):
        return self.__units

    @units.setter
    def units(self, value):
        self.__units = value

    @property
    def _geometry(self):
        return self.__geometry

    @_geometry.setter
    def _geometry(self, value):
        self.__geometry = value

    ''' setting absissae '''
    def __lam(self):                                                # [μm]
        if self.__units != 'wavelength':
            warnings.warn('Please don\'t access it like that')
        else:
            lam = np.linspace(self._start,self._stop, self._points)
        return lam

    def __V(self):                                                  # [1]
        if self.__units != 'V-number':
            warnings.warn('Please don\'t access it like that')
        else:

            V = np.linspace(self._start,self._stop,self._points)
        return V

    def __freq(self):                                               # [THz]
        if self.__units != 'frequency':
            warnings.warn('Please don\'t access it like that')
        else:
            freq = np.linspace(self._start,self._stop,self._points)
        return freq

    ''' '''
        ## Public abscissae
    @property
    def wavelength(self):
        if self.__units=='wavelength':
            return self.__lam()

        if self.__units=='frequency':
            lam = 1/(self.__freq()*sqrt(eps0_umps*mu0_umps))
            ''' in this case lam array is reversed '''
            return lam

        if self.__units=='V-number':
            return 2*self.height/self.__V*sqrt(self.__epsr1 - self.__epsr2)

    @property
    def frequency(self):
        if self.__units=='wavelength':
            freq = 1/(sqrt(eps0_umps*mu0_umps)*self.__lam())
            ''' in this case freq array is reversed '''
            return freq

        if self.__units=='frequency':
            return self.__freq()

        if self.__units=='V-number':
            Vn = self.__V()*pi/self.height
            w0 = Vn/sqrt(eps0_umps*mu0_umps*(self.__epsr1 - self.__epsr2))
            return w0/(2*pi)

    @property
    def pulsation(self):
        ''' pulsation array is reversed if freq is so '''
        return 2*pi*self.frequency


    ''' Material database '''
    def epsr(self, material):

        if self.__units=='V-number':
            raise Exception("Variable indices can't be used with V as the main units.")
        if self.__units=='wavelength':
            lam = self.__lam()
        if self.__units=='frequency':
            lam = self.wavelength

        epsr = get_epsr_value(lam, material)

        return epsr

    ''' '''

        ## Material parameters

    ''' Substrate properties '''

    '''
        Material numbercal properties can be set in the following manner:
        1. core = 'sio2' then the program searches in the library
        if the string contains keywords n or epsr, it takes the corresponding values
        so, for example:
        2. core = 'epsr = 12'
        it cuts the string until there's epsr, then cut from the other side and sets
        the corresponding value.
        this is the easiest way possible for now.

    '''

    @property
    def substrate_epsr(self):
        ''' I have to set it anyway because elsewise A2TE and A2TM will return error'''

            # if there's no substrate set equate it to the cladding
        if self.substrate == None:
            return self.cladding_epsr

            # if there's string we have to decide whether there's epsr or n
        if isinstance(self.substrate, str) == True:

            # search if there is the equality sign
            if self.substrate.find('=') != -1:

                # search until there is but a word
                parameter = self.substrate.split('=')[0]
                parameter = parameter.split(' ')[0]

                if parameter == 'epsr':

                    value = self.substrate.split('=')[-1]
                    value = value.split(' ')[-1]
                    epsr = float(value) * np.ones(self._points)

                if parameter == 'n':
                    epsr = self.substrate_n**2

            # if there's no equality sign then the substrate is a word from the database
            else:
                epsr = self.epsr(material = self.substrate)

            # if there's a material string provided use it from the library
        else:warning.warn("Substrate is not defined")

        return epsr

    @property
    def substrate_n(self):
        if self.substrate == None:
            return self.cladding_n

        if isinstance(self.substrate, str) != True:
            warning.warn("Substrate is not defined")
        elif self.substrate.find('=') != -1:

            # search until there is but a word
            parameter = self.substrate.split('=')[0]
            parameter = parameter.split(' ')[0]

            if parameter == 'n':

                value = self.substrate.split('=')[-1]
                value = value.split(' ')[-1]
                n = float(value) * np.ones(self._points)

            if parameter == 'epsr':
                n = sqrt(self.substrate_epsr)

        else:n = sqrt(self.epsr(material = self.substrate))

        return n

    ''' Core properties '''

    @property
    def core_epsr(self):
        if isinstance(self.core, str) != True:
            warning.warn("Core is not defined")

        elif self.core.find('=') != -1:

            # search until there is but a word
            parameter = self.core.split('=')[0]
            parameter = parameter.split(' ')[0]

            if parameter == 'epsr':
                value = self.core.split('=')[-1]
                value = value.split(' ')[-1]
                epsr = float(value) * np.ones(self._points)

            if parameter == 'n':
                epsr = self.core_n ** 2

        else:epsr = self.epsr(material = self.core)

        return epsr

    @property
    def core_n(self):
        if isinstance(self.core, str) != True:
            warning.warn("Core is not defined")

        elif self.core.find('=') != -1:

            # search until there is but a word
            parameter = self.core.split('=')[0]
            parameter = parameter.split(' ')[0]

            if parameter == 'n':
                value = self.core.split('=')[-1]
                value = value.split(' ')[-1]
                n = float(value) * np.ones(self._points)

            if parameter == 'epsr':
                n = sqrt(self.core_epsr)

        else:n = sqrt(self.epsr(material = self.core))

        return n

    ''' Cladding properties '''

    @property
    def cladding_epsr(self):
        if isinstance(self.cladding, str) != True:
            warning.warn("Cladding is not defined")

        elif self.cladding.find('=') != -1:

            # search until there is but a word
            parameter = self.cladding.split('=')[0]
            parameter = parameter.split(' ')[0]

            if parameter == 'epsr':
                value = self.cladding.split('=')[-1]
                value = value.split(' ')[-1]
                epsr = float(value) * np.ones(self._points)

            if parameter == 'n':
                epsr = self.cladding_n ** 2

        else:epsr = self.epsr(material = self.cladding)

        return epsr

    @property
    def cladding_n(self):
        if isinstance(self.cladding, str) != True:
            warning.warn("Cladding is not defined")

        elif self.cladding.find('=') != -1:

            # search until there is but a word
            parameter = self.cladding.split('=')[0]
            parameter = parameter.split(' ')[0]

            if parameter == 'n':
                value = self.cladding.split('=')[-1]
                value = value.split(' ')[-1]
                n = float(value) * np.ones(self._points)

            if parameter == 'epsr':
                n = sqrt(self.cladding_epsr)

        else:n = sqrt(self.epsr(material = self.cladding))

        return n

    ''' to simplify formulas for internal usage I rename these to epsr0,1,2 '''

    @property
    def __epsr0(self):
        return self.substrate_epsr

    @property
    def __epsr1(self):
        return self.core_epsr

    @property
    def __epsr2(self):
        return self.cladding_epsr

    @property # looks unnecessary
    def eps_relative(self):
        if self.substrate != False:
            warning.warn("The relative dielectric constant can not be defined when the substrate is")
            pass
        else:
            return self.core_epsr/self.cladding_epsr

        # assymetry parameters
    @property
    def A2TE(self):
        return (self.__epsr2 - self.__epsr0)/(self.__epsr1 - self.__epsr2)

    @property
    def A2TM(self):
        return (self.__epsr2 - self.__epsr0)*(self.__epsr1/self.__epsr0)/ \
               (self.__epsr1 - self.__epsr2)

    ''' '''

        ## V-number
        # this is a mian computation abscissae used together withe normalisation
    @property
    def V(self):
        if self.__units=='wavelength':
            V = 2*self.height/self.__lam()*sqrt(self.__epsr1 - self.__epsr2)
            ''' it has to be inverted because this is a normalised freq,
                so it is inversely proportional to the wavelength '''
            return V

        if self.__units=='frequency':
            V = 2*self.height*self.__freq() * sqrt(eps0_umps*mu0_umps) * \
                                              sqrt(self.__epsr1 - self.__epsr2)
            return V

        if self.__units=='V-number':
            return __V()

        # The normalised V: useful to simplify formulae
    @property
    def Vn(self):
        return self.V*pi/self.height

    ''' '''

        ## Wavenumbers

    ''' there are k_i = k_freespace*sqrt(epsr_i) '''
    def k_internal(self):
        return self.Vn*sqrt(self.__epsr1)/sqrt(self.__epsr1 - self.__epsr2)

    def k_external(self):
        return self.Vn*sqrt(self.__epsr2)/sqrt(self.__epsr1 - self.__epsr2)

    def Z0(self):
        return sqrt(mu0_umps/(eps0_umps*self.__epsr0))

    ''' '''

        #todo all function downwards are enormously precarious because
        #todo they treat but the normal dispersion, interpolator chews
        #todo only increasing values, so you understood.


        ## Effective indices

    def neff(self, wavelength=None, frequency=None, internal=None, points=2**10):

            # interpolation
        ''' for the frequency as units, the wavelengths array is descending,
            that kills the interpolator. From where two cases. '''
        if self.__units=='wavelength':
            lam, beta = interp_xypts(self.wavelength,            # [μm]
                                     self.beta, points,          # [rad/μm]
                                     return_x=True)
        else:
            lam, beta = interp_xypts(np.flipud(self.wavelength),
                                     np.flipud(self.beta), points,
                                     return_x=True)
        freq = c_umps/lam

        neff_calc = beta*lam/(2*pi)                       # [rad/um * um/2π = 1]

            # output wavelength
        if self.__units=='wavelength':
            ''' one can output an array of neffs accoring to computation grid
                or a single value on a particular wavelength/frequency'''
                # the interpolated neff for subsequent usage
            # # if internal !=None and wavelength == None and frequency == None:
            # #     neff = neff_calc
            # # else:
            # #     pass

            if wavelength != None:
                    # just one value
                neff = neff_calc[fna(lam, wavelength)]
            elif frequency != None:
                neff = neff_calc[fna(freq, frequency)]

            if wavelength==None and frequency==None:
                    # interpolating back
                neff = interp_tonew_x(lam, self.wavelength, neff_calc, self._points)

            # output frequency
        if self.__units=='frequency':
            # # if internal !=None and wavelength == None and frequency == None:
            # #     neff = np.flipud(neff_calc)
            # # else:
            # #     pass

            if frequency != None:
                ''' outputting just one value, no need to reverse anything '''
                neff = neff_calc[fna(freq, frequency)]
            elif wavelength != None:
            	neff = neff_calc[fna(lam, wavelength)]

            if frequency==None and wavelength==None:
                    # reversing back
                neff_calc = np.flipud(neff_calc)
                freq = np.flipud(freq)
                    # interpolating back
                neff = interp_tonew_x(freq, self.frequency, neff_calc, self._points)

        #todo it for V-number, eventually

        return neff

    ''' '''
        ## group index
    def ng(self, wavelength=None, frequency=None, V=None, points=2**10):
            # interpolating wavelengths and beta
            # interpolation
        ''' for the frequency as units, the wavelengths array is descending,
            that kills the interpolator. From where two cases. '''
        if self.__units=='wavelength':
            lam, beta = interp_xypts(self.wavelength,            # [μm]
                                     self.beta, points,          # [rad/μm]
                                     return_x=True)
        else:
            lam, beta = interp_xypts(np.flipud(self.wavelength),
                                     np.flipud(self.beta), points,
                                     return_x=True)
        freq = c_umps/lam # # # # decreases

        neff = beta*lam/(2*pi)                       # [rad/um * um/2π = 1]

        ''' approximation parabolique de la dispersion selon λ
        β(λ) = β₂λ² + β_slope*λ + β_intersection
            les coefficients
        beta = coeffs[0]*λ**2 + coeffs[1]*λ + coeffs[2]
            dont les unités sont
               [ps2/um rad]      [ps/um]      [rad/um]  '''
        beta2_lam, beta_slope_lam, beta_intersection_lam = np.polyfit(lam, beta, 2)

        ''' ng = neff - λ⋅∂neff/∂λ
            ∂n_eff/∂λ = ∂(βλ/2π) / ∂λ = 1/2π (λ⋅∂β/∂λ + β), where
            ∂β/∂λ = 2β₂λ + β_slope '''
            # group index
        dbdlam = 2*beta2_lam * lam + beta_slope_lam       # ∂β/∂λ
        dneff_dlam = 1/(2*pi)*(dbdlam*lam + beta)         # ∂n_eff/∂λ

        ng_calc = neff - lam*dneff_dlam

            # output
        if self.__units=='wavelength':
            ''' one can output an array of neffs accoring to computation grid
                or a single value on a particular wavelength/frequency'''
            if wavelength != None:
                    # just one value
                ng = ng_calc[fna(lam, wavelength)]
            elif frequency != None:
                ng = ng_calc[fna(freq, frequency)]

            if wavelength==None and frequency==None:
                    # interpolating back
                ng = interp_tonew_x(lam, self.wavelength, ng_calc, self._points)


        if self.__units=='frequency':
            if frequency != None:
                ''' outputting just one value, no need to reverse anything '''
                ng = ng_calc[fna(freq, frequency)]
            elif wavelength != None:
            	ng = ng_calc[fna(lam, wavelength)]

            if frequency==None and wavelength==None:
                    # reversing back
                ng_calc = np.flipud(ng_calc)
                freq = np.flipud(freq)

                    # interpolating back
                ng = interp_tonew_x(freq, self.frequency, ng_calc, self._points)

        #todo it for V-number, eventually

        return ng
    ''' '''

        ## group velocity
    def vg(self, wavelength=None, frequency=None, V=None, points=2**10):
            # interpolating wavelengths and beta
            # interpolation
        ''' for the frequency as units, the wavelengths array is descending,
            that kills the interpolator. From where two cases. '''
        if self.__units=='wavelength':
            w0, beta = interp_xypts(np.flipud(self.pulsation),
                                    np.flipud(self.beta), points,
                                    return_x=True)
        else:
            w0, beta = interp_xypts(self.pulsation,            # [μm]
                                    self.beta, points,          # [rad/μm]
                                    return_x=True)
        freq = w0/(2*pi)
        lam = c_umps/freq


        ''' approximation parabolique de la dispersion, la même chose que plus haut
            [ps/um], [rad/um] '''
        beta2, beta_slope_w, beta_intersection_w = np.polyfit(w0, beta, 2)

        vg_calc = (2*beta2*w0 + beta_slope_w)**-1                   # [μm/ps]


            # output
        ''' one can output an array of neffs accoring to computation grid
            or a single value on a particular wavelength/frequency'''
        if self.__units=='wavelength':
            if wavelength != None:
                    # just one value
                vg = vg_calc[fna(lam, wavelength)]
            elif frequency != None:
                vg = vg_calc[fna(freq, frequency)]

            if wavelength==None and frequency==None:
                    # reversing back
                vg_calc = np.flipud(vg_calc)
                    # interpolating back
                vg = interp_tonew_x(lam, self.wavelength, vg_calc, self._points)

        if self.__units=='frequency':
            if frequency != None:
                ''' outputting just one value, no need to reverse anything '''
                vg = vg_calc[fna(lam, wavelength)]
            elif wavelength != None:
                vg = vg_calc[fna(freq, frequency)]

            if frequency==None and wavelength==None:
                    # interpolating back
                vg = interp_tonew_x(freq, self.frequency, vg_calc, self._points)

        #todo it for V-number, eventually

        return vg

    ''' From now on and down nothing works'''
        ## Dispersion paratmeter
    def D(self, wavelength=None):
        ''' rp-photonics always gives 1e-6 x (my value)
            units conversion is as follows to obtain [ps/(nm km)]
            wl -> [nm], beta2 -> [ps^2/rad km] '''
        points = 2**10
        lam = np.linspace(self.wavelength[0],
                          self.wavelength[-1], points)            # [μm]
        w0 = 2*pi/(sqrt(eps0_umps*mu0_umps)*lam)                    # [rad/ps]
        interpolator = interpolate_xy(self.pulsation, self.beta)
        beta = interpolator(w0)                                     # [rad/μm]

        beta2, beta_slope_w, beta_intersection_w = np.polyfit(w0, beta, 2)

        D_calc = -2*pi*c_nmps/(self.wavelength*1e3)**2 * (beta2*1e9)
        #todo fix unités
        if wavelength==None:
            interpolator = interpolate_xy(w0, D_calc)
            D = interpolator(self.wavelength)
        else:
            D = D_calc[fna(w0, wavelength)]
        return D

        ## Group delay dispersion
    def GDD_s2(self, lentgh, wavelength=None):
        ''' group delay dispersion  : L->[m] '''
        points = 2**10
        lam = np.linspace(self.wavelength[0],
                          self.wavelength[-1], points)            # [μm]
        w0 = 2*pi/(sqrt(eps0_umps*mu0_umps)*lam)                    # [rad/ps]
        interpolator = interpolate_xy(self.pulsation, self.beta)
        beta = interpolator(w0)                                     # [rad/μm]

        beta2, beta_slope_w, beta_intersection_w = np.polyfit(w0, beta, 2)

        D2_calc = beta2*length # this is [ps2]
        #todo fix unités
        if wavelength==None:
            interpolator = interpolate_xy(w0, D2_calc)
            D2 = interpolator(self.wavelength)
        else:
            D2 = D2_calc[fna(w0, wavelength)]
        return D2*1e-24
