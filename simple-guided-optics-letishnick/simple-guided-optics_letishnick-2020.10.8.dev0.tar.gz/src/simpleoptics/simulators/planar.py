from simpleoptics.helpers.preambule import *

import warnings

class Simulation_planar:

    ''' polarisation means TE or TM mode, the lowest mode has 0 as a number '''

    def __init__(self,  waveguide,
                        polarisation, modenumber,
                        units, start=None, stop=None, points=None,
                        centre=None, span=None, step=None):

            # main variables
        ''' via start, stop, step and start, stop, points '''
        if start is not None and stop is not None:
            if points is not None:
                self.start = start
                self.stop = stop
                self.points = points
            if points is None:      # then its step !
                self.step = step
                self.points = int((stop - start)/step)

        ''' via start, stop, step and start, stop, points '''
        if centre is not None and span is not None:
            if points is not None:
                self.start = centre - span/2
                self.stop  = centre + span/2
                self.points = points
            if points is None:      # then its step !
                self.step = step
                self.points = int(span/step)

        self.units        = units
        self.polarisation = polarisation
        self.modenumber    = modenumber

        ''' pushing the necessary variables to the overlying waveguide instance '''
        self.waveguide          = waveguide
        self.waveguide.units    = self.units
        self.waveguide._start   = self.start
        self.waveguide._stop    = self.stop
        self.waveguide._points  = self.points

        ''' Inheriting back the waveguide properties
            This is ugly but seem necessary as long as the consequent field
            computations use a lot of this. It would be uglier to indicate
            waveguide everytime a field amplitude is instanced.
            Yes, there is width as a necessary condition to norm calculation
        '''
        self._w    = waveguide.width                # [μm]
        self._b    = waveguide.height /2            # [μm]

        self._V    = waveguide.V                    # [1]
        self._Vn   = waveguide.Vn                   # [1]
        self._w0   = waveguide.pulsation            # [rad/ps]
        self._lam  = waveguide.wavelength           # [μm]
        self._freq = waveguide.frequency            # [THz]

        self._epsr0 = waveguide.cladding_epsr
        self._epsr1 = waveguide.core_epsr
        self._epsr2 = waveguide.substrate_epsr
        self._epsr  = waveguide.core_epsr/waveguide.cladding_epsr

    ''' '''

        ## DISPERSION

    ''' '''

    def __dispnormTE(self, waveguide, B2, i):

        V = waveguide.V
        A2TE = waveguide.A2TE
        ''' the calculations start from the largest V number because the curve it
            is easier to attribute an initial value to it. So when the main units
            are lambdas V has to be reversed
        '''
        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
            A2TE = np.flipud(A2TE)
        else:
            pass

        m = self.modenumber

        return -m*pi + V[i]*pi*sqrt(1-B2) - arctan(sqrt(B2/(1-B2))) - \
                                            arctan(sqrt((B2+A2TE[i])/(1-B2)))

    def __dispnormTM(self, waveguide, B2, i):

        V = waveguide.V
        A2TM = waveguide.A2TM
        m = self.modenumber

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
            A2TM = np.flipud(A2TM)
        else:
            pass

        return -m*pi + V[i]*pi*sqrt(1-B2) - arctan(sqrt(B2/(1-B2))) - \
                                            arctan(sqrt((B2+A2TM[i])/(1-B2)))

    ''' The initial value finder has been taken from plandrem github.
        It has been modified and hardcoded here and there, namely inside B2_test.
        The biggest issue though is that sometimes ch fails; it finds more than
        two roots. This case is left for posterior investigations '''

        ## initnal value finder
    def __initval(self, waveguide):
        ''' the grid of beta points '''
        B2_test = np.linspace(0.005,0.99,100)
        m = self.modenumber

        ''' beta test solutions in the point upper frequency,
            given that inside the corresponding functions V arrays are reversed,
            the i of the largest value of V is 0
        '''
        if self.polarisation=='TE':
            solB2_test = self.__dispnormTE(waveguide, B2_test, i=0)
        elif self.polarisation=='TM':
            solB2_test = self.__dispnormTM(waveguide, B2_test, i=0)
        else:
            warnings.warn('Please set the polarisation.')

            # cherchons les points de changement de la signe :
        diff = np.diff(np.sign(solB2_test))
            # obtenons les indices de ces points
        ch = np.where(abs(diff)==2)[0]

        if self.polarisation=='TE':
            dispf = lambda B2: self.__dispnormTE(waveguide,B2,i=0)
        elif self.polarisation=='TM':
            dispf = lambda B2: self.__dispnormTM(waveguide,B2,i=0)
        else:
            warnings.warn('Please set the polarisation.')

            # la racine cherchée est en haut
        B2init = brentq(dispf, B2_test[ch[-1]], B2_test[ch[-1]+1])

        return B2init

    ''' '''

        # Solver that gives a normalised beta
    def __calculate_betanorm_planar(self, waveguide):
        '''
        a simple scipy root finder
        '''
        B2initial = self.__initval(waveguide)                # la valeur initiale
        if self.polarisation=='TE':
            dispf = lambda B2: self.__dispnormTE(waveguide,B2,i)
        elif self.polarisation=='TM':
            dispf = lambda B2: self.__dispnormTM(waveguide,B2,i)
        else:
            warnings.warn('Please please set the pol')

        betanorm = np.empty((0,))
        for i in np.arange(waveguide._points):
            B2current = root(dispf, B2initial, method='hybr').x[0]
            B2initial = B2current
            betanorm = np.append(betanorm, B2current)

        if self.units != 'wavelength':
            betanorm = np.flipud(betanorm)

        return betanorm

    ''' '''
        # normal beta from the normalised one
    def _calculate_wavenumbers(self, waveguide):

        Vn = waveguide.Vn
        epsr0 = waveguide.substrate_epsr
        epsr1 = waveguide.core_epsr
        epsr2 = waveguide.cladding_epsr
        w0 = waveguide.pulsation
        betanorm = self.__calculate_betanorm_planar(waveguide)

        beta = Vn*sqrt(betanorm + epsr2/(epsr1 - epsr2))            # [rad/μm]

            # nombres d'ondes transverses
        ky1 = sqrt(w0**2*epsr1/c_umps**2 - beta**2)
        ky0 = sqrt(beta**2 - w0**2*epsr0 * eps0_umps*mu0_umps)
        ky2 = sqrt(beta**2 - w0**2*epsr2 * eps0_umps*mu0_umps)

        return np.array([betanorm, beta, ky0, ky1, ky2])

    ''' These can be calculated in two forms
    Pour pouvoir dessiner les champs il me faut les réticules des
            coordonnées. D’ailleurs, dans le cas du guide d’onde planair je
            peux m’arranger seulument avec la ligne des Y.
            Je peux donc créer une méthode qui prendra
            np.linspace comme l’argument
    Le guide d’onde, je n’en veux que les valeurs des champs. Par conséquent, je
        leur fourninai avec les propriétés waveguide.Ex(y)
        self.waveguide.Ex =
        Puisque cette appel consommera la ligne des Y fournie tout en produisant un
        massif, il me semble qu’il faut séparer le calcul de la dispersion et des
        champs. '''


    ''' '''


        ## FIELDS


    '''
    Fields can be represented in different forms
        ___0___
           1
        ⎺⎺⎺2⎺⎺⎺

    '''
            ## Champs électriques
            # trigonométrique
    def Ex0(self, y):
        return self._A0 * exp(-self._ky0*(y-self._b))

    def Ex1(self, y):
        return self._A1*sin(self._ky1*y) + self._B1*cos(self._ky1*y)

    def Ex2(self, y):
        return self._B2 * exp(self._ky2*(y+self._b))

        # Amplitudes classic trigonometric style TE
    @property
    def _A1(self):
        return 1
    @property
    def _B1(self):
        ky1=self._ky1 ; ky2=self._ky2 ; b=self._b
        B1 = self._A1 * (ky1/ky2*cos(ky1*b) + sin(ky1*b)) / (cos(ky1*b) - ky1/ky2*sin(ky1*b))
        return B1
    @property
    def _A0(self):
        ky1=self._ky1 ; ky0=self._ky0 ; b=self._b
        A0 = -self._A1 * (ky1/ky0) / (ky1/ky0*sin(ky1*b) - cos(ky1*b))
        return A0
    @property
    def _B2(self):
        ky1=self._ky1 ; ky2=self._ky2 ; b=self._b
        B2 = -self._A1 * (ky1/ky2) / (ky1/ky2*sin(ky1*b) - cos(ky1*b))
        return B2

            # Norme trigonometrique
    # @property
    # def _Ng(self):
    #     A0   = self._A0    ; B1  = self._B1  ; A1  = self._A1  ; B2 = self._B2
    #     beta = self._beta  ; w   = self._w   ; b   = self._b
    #     ky0  = self._ky0   ; ky1 = self._ky1 ; ky2 = self._ky2 ; w0 = self._w0
    #
    #     N0 = (A0**2*beta*w)/(mu0_umps*ky0*w0)
    #     N1 = beta*w*2*b*(
    #             (B1**2 - A1**2)*sinc(2*b*ky1/pi) + B1**2 + A1**2) / (mu0_umps*w0)
    #     N2 = (B2**2*beta*w)/(mu0_umps*ky2*w0)
    #
    #     N = N0 + N1 + N2
    #
    #     return N

        # Forme symm/assym
    def Ex0m(self, y):
        return self._e0m*exp(-self._ky0*(y-self._b))
    def Ex1m(self, y):
        return self._e1m*cos(self._ky1*y-self._f1m)
    def Ex2m(self, y):
        return self._e2m*exp(self._ky2*(y+self._b))

        # d'amplitudes maximums
    @property
    def _e1m(self):
        return 1
    @property
    def _e0m(self):
        ky0=self._ky0 ; ky1=self._ky1
        e0m = self._e1m/sqrt(1+ky0**2/ky1**2)
        return e0m
    @property
    def _e2m(self):
        ky2=self._ky2 ; ky1=self._ky1
        e2m = self._e1m/sqrt(1+ky2**2/ky1**2)
        return e2m
    @property
    def _f1m(self):
        ky0=self._ky0; ky1=self._ky1 ; ky2=self._ky2
        f1m = -1/2*(arctan(ky0/ky1)-arctan(ky2/ky1))
        return f1m

            # Norme symm/asymm
        # Norme trigonometrique
    @property
    def _Ng(self):
        e0m  = self._e0m   ; e1m = self._e1m ; e2m = self._e2m ; f1m = self._f1m
        beta = self._beta  ; w   = self._w   ; b   = self._b
        ky0  = self._ky0   ; ky1 = self._ky1 ; ky2 = self._ky2 ; w0  = self._w0

        N0 = beta*e0m**2*w/(ky0*mu0_umps*w0)
        N1 = beta*e1m**2*w*2*b*(sinc((2*b*ky1/pi))*cos(2*f1m)+1)/(mu0_umps*w0)
        N2 = beta*e2m**2*w/(ky2*mu0_umps*w0)

        N = N0 + N1 + N2

        return N

            ## Normes modes de propagation
        # Forme Barybin
    @property
    def _Nb(self):
        dm = 2*self._b + 1/self._ky0 + 1/self._ky2
        N = self._w*self._beta*dm/(self._w0*mu0_umps) * self._e1m**2
        return N

            # modes de rayonnement STRUC
    @property
    def _f1r(self):
        f1r = 0.5*arctan(
            tan(2*ky1_*b) * ((ky1_**2+ky0_*ky2_)/(ky1_**2-ky0_*ky2_)) * ((ky2_-ky0)/(ky2_+ky0)) )
        return f1r
    @property
    def _f0rs(self):
        f0rs=arctan(-ky1_/ky0_*tan(ky1_*b-f1r))
        return f0rs
    @property
    def _f2rs(self):
        f2rs=arctan( ky1_/ky2_*tan(ky1_*b+f1r))
        return f2rs
    @property
    def _e0rs(self):
        e0rs=1
        return e0rs
    @property
    def _e1rs(self):
        e1rs=e0rs*sqrt(cos(f0rs)**2+ky0_**2/ky1_**2*sin(f0rs)**2)
        return e1rs
    @property
    def _e2rs(self):
        e2rs=e1rs/sqrt(cos(f2rs)**2+ky2_**2/ky1_**2*sin(f2rs)**2)
        return e2rs

    ''' '''

    ''' '''

    # #         # exponentielle
    # # def Ex0c(y):
    # #     return A0c*exp(-ky0*(y-b)) # signe?
    # # def Ex1c(y):
    # #     return A1c*exp(-1j*ky1*y)+B1c*exp(1j*ky1*y)
    # # def Ex2c(y):
    # #     return B2c*exp(ky2*(y+b)) # signe?
    # #         # d'amplitude maximum
    # # def Ex0m(y):
    # #     return E0m*exp(-sky0*(y-b))
    # # def Ex1m(y):
    # #     return E1m*cos(ky1*y-f1m)
    # # def Ex2m(y):
    # #     return E2m*exp(sky2*(y+b))
    # #         # des modes de rayonnement SUB
    # # def Ex0r(y):
    # #     return E0r*exp(-ky0_*(y-b))
    # # def Ex1r(y):
    # #     return E1r*cos(ky1_*y-f1rsub)
    # # def Ex2r(y):
    # #     return E2r*cos(ky2_*(y+b)-f2r)
    # #         # des modes de rayonnement STRUC SYMM
    # # def Ex0rs(y):
    # #     return E0rs*cos(ky0_*(y-b)-f0rs)
    # # def Ex1rs(y):
    # #     return E1rs*cos(ky1_*y-f1r)
    # # def Ex2rs(y):
    # #     return E2rs*cos(ky2_*(y+b)-f2rs)
    # # ''' '''


    ''' '''

        ## SIMULATION


    ''' running the simulation and setting the waveguide instance properties,
        also translating it as the protected properties to the current simulation
        instance '''
    def simulate(self, waveguide):
        '''
        as long as ky_i don't need to be called from waveguide instance,
        their values aren'k attributed and rest in the simulation class
        '''
            # calculating wavenumbers including beta
        waveguide.beta_normalised, waveguide.beta, \
        waveguide._ky0, waveguide._ky1, waveguide._ky2 = self._calculate_wavenumbers(waveguide)

            # setting simulation properties that enable to calc fields
        self._beta_normalised, self._beta, \
        self._ky0, self._ky1, self._ky2 = \
        waveguide.beta_normalised, waveguide.beta, \
        waveguide._ky0, waveguide._ky1, waveguide._ky2



