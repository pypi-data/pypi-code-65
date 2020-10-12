from simpleoptics.helpers.preambule import *

import warnings

class Simulation_rectangular():
    ''' two methods are implemented : Marcatili, Menon. The latter
        can calculate a trapezoidal wg as well, using Menon+Barybin CMT
        [Cheplagin, Zaretskaia 2018]
    
    Waveguide mode classes are as follows:
            /  I      Ex21, Ex23, Ey12, Ey32, ...
            |  II     Ex22, Ex44, Ey11, Ey33, ...
    Class: <
            |  III    Ex11, Ex33, Ey22, Ey44, ...
            \  IV     Ex12, Ex32, Ey21, Ey23, ...
    
    There is no possibility to arbitrary choose a mode. Though by changing the
    modenumber variable it is possible to calculate the dispersion of a higher mode,
    to attribute a particular mode to a particular class it is to the engineer itself.
    But, I do not see the method in its current state be applied to thoroughly
    calculate something other that Ex11 and Ey11 lowest-order modes.
    '''

    def __init__(self,  waveguide,
                        modeclass, polarisation, method, units, 
                        start=None, stop=None, points=None, 
                        centre=None, span=None, step=None):

            # main variables
        ''' via start, stop, step and start, stop, points '''
        if start is not None and stop is not None:
            if points is not None:
                self.start = start
                self.stop = stop
                self.points = points
            if points is None:      # then it's step
                self.step = step
                self.points = int((stop - start)/step)
                
        ''' via start, stop, step and start, stop, points '''        
        if centre is not None and span is not None:
            if points is not None:
                self.start = centre - span/2
                self.stop  = centre + span/2
                self.points = points
            if points is None:      # then it's step
                self.step = step
                self.points = int(span/step)

        self.units = units
        self.polarisation = polarisation # TODO make it work with normal mode designations
        self.modeclass = modeclass
        self.method = method

        ''' pushing the necessary variables to an underlying waveguide instance '''
        self.waveguide = waveguide
        self.waveguide.units = self.units
        self.waveguide._start = self.start
        self.waveguide._stop = self.stop
        self.waveguide._points = self.points
        
        ''' Inheriting back the waveguide properties
            This is ugly but seem necessary as long as the consequent field
            computations use a lot of this. It would be uglier to indicate
            waveguide everytime a field amplitude is instanced. 
        '''
        self._a    = waveguide.width /2             # [μm]
        self._b    = waveguide.height /2            # [μm]
        
        self._V    = waveguide.V                    # [1]
        self._Vn   = waveguide.Vn                   # [1]
        self._w0   = waveguide.pulsation            # [rad/s]      
        self._lam  = waveguide.wavelength           # [μm]
        self._freq = waveguide.frequency            # [THz]

        self._epsr1 = waveguide.core_epsr
        self._epsr2 = waveguide.cladding_epsr
        self._epsr  = waveguide.core_epsr/waveguide.cladding_epsr
        
    
    ''' '''

        ## DISPERSION

        
    ''' '''

    ''' 
        The Marcatilli equations tare also utilised for Menon initval estimation,
        a problem here is to choose the good modenumber as long as
        the initial value test grid is badly set and can fail. Maybe 
    '''
        ## Equations Marcatili
    def disEXkx(self, kx, i):

        Vn = self.waveguide.Vn
        epsr = self.waveguide.core_epsr/self.waveguide.cladding_epsr
        a = self.waveguide.width /2

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
            epsr = np.flipud(epsr)
        else:
            pass

        return tan(2*kx*a) - 2*kx*sqrt(Vn[i]**2-kx**2)/ \
               (kx**2* (epsr[i]**-1+epsr[i]) - Vn[i]**2*epsr[i])
    ''' '''
    def disEXky(self, ky, i):

        Vn = self.waveguide.Vn
        b = self.waveguide.height /2

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
        else:
            pass

        return tan(2*ky*b) - 2*ky*sqrt(Vn[i]**2-ky**2) / (2*ky**2-Vn[i]**2)
    ''' '''
    def disEYkx(self, kx, i):

        Vn = self.waveguide.Vn
        a = self.waveguide.width /2

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
        else:
            pass

        return tan(2*kx*a) - 2*kx*sqrt(Vn[i]**2-kx**2) / (2*kx**2-Vn[i]**2)
    ''' '''
    def disEYky(self, ky, i):

        Vn = self.waveguide.Vn
        epsr = self.waveguide.core_epsr/self.waveguide.cladding_epsr
        b = self.waveguide.height /2

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
            epsr = np.flipud(epsr)
        else:
            pass

        return tan(2*ky*b) - 2*ky*sqrt(Vn[i]**2-ky**2)/ \
               (ky**2*(epsr[i]**-1+epsr[i]) - Vn[i]**2*epsr[i])
    ''' '''
        ## Equations Menon by modeclass
    def disvec1(self, k, i):         #Ex21, Ex23, Ey12, Ey32,...

        Vn = self.waveguide.Vn
        epsr = self.waveguide.core_epsr/self.waveguide.cladding_epsr
        a = self.waveguide.width /2
        b = self.waveguide.height/2

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
            epsr = np.flipud(epsr)
        else:
            pass

            # helper designations
        k2x = sqrt(Vn[i]**2 - k[0]**2); k2y = sqrt(Vn[i]**2 - k[1]**2)
        kt1sq = Vn[i]**2 - k[0]**2 - k[1]**2

        return [k[0]*k2x*tan(k[0]*a) + k[1]*k2y*tan(k[1]*b) - kt1sq,
                k[0]*k2x*cot(k[0]*a) + k[1]*k2y*cot(k[1]*b) + kt1sq*epsr[i]]

    def disvec2(self, k, i):         #Ex22, Ex44, Ey11, Ey33,...

        Vn = self.waveguide.Vn
        epsr = self.waveguide.core_epsr/self.waveguide.cladding_epsr
        a = self.waveguide.width /2
        b = self.waveguide.height/2

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
            epsr = np.flipud(epsr)
        else:
            pass

        k2x = sqrt(Vn[i]**2 - k[0]**2); k2y = sqrt(Vn[i]**2 - k[1]**2)
        kt1sq = Vn[i]**2 - k[0]**2 - k[1]**2

        return [k[0]*k2x*tan(k[0]*a) - k[1]*k2y*cot(k[1]*b) - kt1sq,
                k[0]*k2x*cot(k[0]*a) - k[1]*k2y*tan(k[1]*b) + kt1sq*epsr[i]]

    def disvec3(self, k, i):         #Ex11, Ex33, Ey22, Ey44,...

        Vn = self.waveguide.Vn
        epsr = self.waveguide.core_epsr/self.waveguide.cladding_epsr
        a = self.waveguide.width /2
        b = self.waveguide.height/2

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
            epsr = np.flipud(epsr)
        else:
            pass

        k2x = sqrt(Vn[i]**2 - k[0]**2); k2y = sqrt(Vn[i]**2 - k[1]**2)
        kt1sq = Vn[i]**2 - k[0]**2 - k[1]**2

        return [k[0]*k2x*cot(k[0]*a) - k[1]*k2y*tan(k[1]*b) + kt1sq,
                k[0]*k2x*tan(k[0]*a) - k[1]*k2y*cot(k[1]*b) - kt1sq*epsr[i]]

    def disvec4(self, k, i):         #Ex12, Ex32, Ey21, Ey23,...

        Vn = self.waveguide.Vn
        epsr = self.waveguide.core_epsr/self.waveguide.cladding_epsr
        a = self.waveguide.width /2
        b = self.waveguide.height/2

        if self.units != 'wavelength':
            Vn = np.flipud(Vn)
            epsr = np.flipud(epsr)
        else:
            pass

        k2x = sqrt(Vn[i]**2 - k[0]**2); k2y = sqrt(Vn[i]**2 - k[1]**2)
        kt1sq = Vn[i]**2 - k[0]**2 - k[1]**2

        return [k[0]*k2x*cot(k[0]*a) + k[1]*k2y*cot(k[1]*b) + kt1sq,
                k[0]*k2x*tan(k[0]*a) + k[1]*k2y*tan(k[1]*b) - kt1sq*epsr[i]]

    ''' '''
        ## Initial value finder
#TODO for now on it works only in the case of lowest-order modes

    ''' There is a huge problem here about the choice of mode designations.
            By default this solver searches for the lowest mode, which
            is ex11 and ey11 according to the method utilised.
            It's OK with Marcatili because there is an evident separation between
            two polarisations, whereas for Menon it is much worse as long as
            in each of 4 mode classes both ex and ey polarisations are present '''

#TODO deal with mode designations
    ''' The vague idea is to collect the values of solkx_test and solky_test
            which contain implicitly mode type and then attribute each of it to
            one of menon type. But how? One cannot clearly say which set of {kx,ky}
            belongs to which mode type except for the lowest-order mode.
            The solution may be hiding behing mode symmetry imposed by the
            particular set of trigonometric functions.
        '''

    def get_initvals(self, modenumber):
        '''nous cherchons les racines sur une seule longueur d'onde :
        Vn=Vn[0]; epsr=epsr[0]'''
            # le NUMERO d'une mode. 0 ne marche pas
        mode = modenumber

                # valeurs initiales kx
        a = self.waveguide.width /2
        b = self.waveguide.height/2

        '''Границы поперечных волновых чисел устанавливаются вручную исходя из неких
        предположений. в отличие от B2 волновые числа возрастают c возрастанием
        номера моды, следовательно низшая мода [1] ВРОДЕ ДА'''
        startkx = 0.5/a; endkx = 3/a; stepkx = 1e-3
        listekx = np.arange(startkx, endkx, stepkx)
        startky = 0.5/b; endky = 3/b; stepky = 1e-3
        listeky = np.arange(startky, endky, stepky)

            # faisons une réticule entre 0 et la racine courante
        kx_test = np.linspace(startkx, endkx, 100)
            # les solutions pour kx
        solkx_test = self.disEXkx(kx_test, i=0)
        diffx = np.diff(np.sign(solkx_test))
        chx = np.where(abs(diffx)==2)[0]    # c'est [0] se sert à chosir le tuple True

            # choosing the polarisation
        if self.polarisation == 'ex':
            dqkx = lambda kx: self.disEXkx(kx, i=0)
        elif self.polarisation == 'ey':
            dqkx = lambda kx: self.disEYkx(kx, i=0)
        else:
            warnings.warn('Please make sure that a polarisation is properly set.')

            # checking whether there's at least one root
        if np.shape(chx)>(0,):
            kx_cur = brentq(dqkx,kx_test[chx[mode]],kx_test[chx[mode]+1])
        else:
            kx_cur = 0

                # valeurs initiales ky
        ky_test = np.linspace(startky, endky, 100)
        solky_test = self.disEXky(ky_test, i=0)
        diffy = np.diff(np.sign(solky_test))
        chy = np.where(abs(diffy)==2)[0]

            # choosing the polarisation
        if self.polarisation == 'ex':
            dqky = lambda ky: self.disEXky(ky, i=0)
        elif self.polarisation == 'ey':
            dqky = lambda ky: self.disEYky(ky, i=0)
        else:
            warnings.warn('Please make sure that a polarisation is properly set.')

        if np.shape(chy)>(0,):
            ky_cur = brentq(dqky,ky_test[chy[mode]],ky_test[chy[mode]+1])
        else:
            ky_cur = 0

        return np.array([kx_cur, ky_cur])

    ''' '''
        ## Menon calculation
    def __internal_wavenumbers_menon(self):
        ''' The main solver routine '''
        kx1 = np.empty((0,)); ky1 = np.empty((0,));

        # assigning the right mode class
        if self.modeclass==1:    # classe I  Ex21, Ex23, Ey12, Ey32,...
            dispf = lambda k: self.disvec1(k,i)
            kxinitial,kyinitial = self.get_initvals(modenumber=1)

        if self.modeclass==2:    # classe II Ex22, Ex44, Ey11, Ey33,...
            dispf = lambda k: self.disvec2(k,i)
            kxinitial,kyinitial = self.get_initvals(modenumber=1)

        if self.modeclass==3:    # classe III Ex11, Ex33, Ey22, Ey44,...
            dispf = lambda k: self.disvec3(k,i)
            kxinitial,kyinitial = self.get_initvals(modenumber=1)

        if self.modeclass==4:    # classe IV Ex12, Ex32, Ey21, Ey23,...
            dispf = lambda k: self.disvec4(k,i)
            kxinitial,kyinitial = self.get_initvals(modenumber=1)

        # a standard scipy solver
        for i in np.arange(0, self.points):
            kxcurrent, kycurrent = root(dispf, [kxinitial,kyinitial], method='hybr').x
            kxinitial, kyinitial = kxcurrent, kycurrent
            kx1 = np.append(kx1, kxcurrent); ky1 = np.append(ky1, kycurrent)

        if self.units != 'wavelength':
            kx1   =  np.flipud(kx1)
            ky1   =  np.flipud(ky1)
        else:
            pass

        return np.array([kx1, ky1])


    ''' A sempiternal classic is still there '''
        ## Marcatili calculation
    def __internal_wavenumbers_marcatili(self):

        kx1 = np.empty((0,)); ky1 = np.empty((0,))

        # assigning the right mode class
        if self.polarisation=='ex':    # all Ex modes
            dispf_kx = lambda kx: self.disEXkx(kx,i)
            dispf_ky = lambda ky: self.disEXky(ky,i)
            kxinit, kyinit = self.get_initvals(modenumber=1)

        if self.polarisation=='ey':      # all Ey modes
            dispf_kx = lambda kx: self.disEYkx(kx,i)
            dispf_ky = lambda ky: self.disEYky(ky,i)
            kxinit, kyinit = self.get_initvals(modenumber=1)

        # a standard scipy solver
        for i in np.arange(0, self.points):
            kxcurrent = root(dispf_kx, kxinitial, method='hybr').x[0]
            kycurrent = root(dispf_ky, kyinitial, method='hybr').x[0]
            kxinitial, kyinitial = kxcurrent, kycurrent
            kx1 = np.append(kx1, kxcurrent); ky1 = np.append(ky1, kycurrent)

        if self.units != 'wavelength':
            kx1   =  np.flipud(kx1)
            ky1   =  np.flipud(ky1)
        else:
            pass

        return np.array([kx1, ky1])
        
    def _calculate_wavenumbers(self, waveguide):
        ''' translating calculated internal wavenumbers to propagation constants '''
        Vn = self.waveguide.Vn
        epsr1 = self.waveguide.core_epsr
        epsr2 = self.waveguide.cladding_epsr

        if self.method=='Marcatili':
            kx1, ky1 = self.__internal_wavenumbers_marcatili()

        if self.method=='Menon':
            kx1, ky1 = self.__internal_wavenumbers_menon()

        beta = sqrt(Vn**2 * epsr1/(epsr1-epsr2) - (kx1**2 + ky1**2))
        betanorm = 1 - 1/Vn**2*(kx1**2 + ky1**2)

        kx2 = sqrt(Vn**2 - kx1**2)
        ky2 = sqrt(Vn**2 - ky1**2)
        kt1sq = kx1**2 + ky1**2
        kt2sq = Vn**2 - kx1**2 - ky1**2

        return np.array([beta, betanorm, kx1, ky1, kx2, ky2, kt1sq, kt2sq])
    
    ''' '''


        ## FIELDS

        
    ''' '''
    
    ''' 
    Fields can exist in various forms. 
    1st, in guise of methods, from where we will be able to pick frequecny slices,
        as well as use them afterwards in numerical integration routines (hopefully)
        
    2nd, as calculated properties, if we need to just pass them to subsequential
        analytical solvers, e.g. CMT ones. 
    '''
    
            ## Menon style fields
    ''' 
        Interiour fields are represented as follows
        E1z(x,y) = ez1*sin(x*kx1)*cos(y*ky1)
        H1z(x,y) = hz1*cos(x*kx1)*sin(y*ky1)
        
        Other components are
        Ex = i*ex1*cos(kx1*x)*cos(ky1*y)
        Ey = i*ey1*sin(kx1*x)*sin(ky1*y)
        Hx = i*hx1*sin(kx1*x)*sin(ky1*y)
        Hy = i*hy1*cos(kx1*x)*cos(ky1*y)
        
        the same goes for the I and II regions (cf. Menon's paper).
        As long as in analytical methods the trigonometric functions are generally
        integrated, the main calculations pass over amplitudes ex_i. So they are
        explisited as methods.
        
        Here, due to efforts put in the non-symmetric case (in vain)
        I renumbered regions so they were like that: 
           ___0___ 
        4 |   1   | 3
           ⎺⎺⎺2⎺⎺⎺  
        The justification behind that is that to maintain consistency between
        planar designations and rectangular ones. Hence, Y axis corresponds to
        height and along Y there are media No.No. 0-1-2
    '''
        
        # Modeclass 3, guided I have for the others as well, cf. thesis drafts
    
        # Fields components as methods so to evoke them afterwards
        # Longitudinal, internal
    def Ez1(self, x, y):
        Ez1 = self._ez1*sin(x*self._kx1)*cos(y*self._ky1)
        return Ez1
    def Hz1(self, x, y):
        Ez1 = self._hz1*cos(x*self._kx1)*sin(y*self._ky1)
        return Ez1
        
        # Transversal, internal 
    def Ex1(self, x, y):
        Ex1 = 1j*self._ex1 * cos(self._kx1*x) * cos(self._ky1*y)
        return Ex
    def Ey1(self, x, y):
        Ey1 = 1j*self._ey1 * sin(self._kx1*x) * sin(self._ky1*y)
        return Ey1
    def Hx1(self, x, y):
        Hx1 = 1j*self._hx1 * sin(self._kx1*x) * sin(self._ky1*y)
        return Hx1
    def Hy1(self, x, y):
        Hy1 = 1j*self._hy1 * cos(self._kx1*x) * cos(self._ky1*y)
        return Hy1
        
        # Transversal, external region I, 0
    def Ex0(self, x, y):
        Ex0 = -1j*self._ex0 * cos(self._ky1*y) * exp(self._kx3*(self._a-x))
        return Ex0
    def Ey0(self, x, y):
        Ex0 = -1j*self._ey0 * sin(self._ky1*y) * exp(self._kx3*(self._a-x))
        return Ey0
    def Hx0(self, x, y):
        Hx0 = -1j*self._hx0 * sin(self._ky1*y) * exp(self._kx3*(self._a-x))
        return 
    def Hy0(self, x, y):
        Hy0 = -1j*self._hy0 * cos(self._ky1*y) * exp(self._kx3*(self._a-x))
        return Hy0
        
        # Transversal, external region II, 3
    def Ex3(self, x, y):
        Ex3 = -1j*self._ex3 * cos(self._kx1*x) * exp(self._ky0*(self._b-y))
        return Ex3
    def Ey3(self, x, y):
        Ey3 = -1j*self._ey3 * sin(self._kx1*x) * exp(self._ky0*(self._b-y))
        return Ey3
    def Hx3(self, x, y):
        Hx3 = -1j*self._hx3 * sin(self._kx1*x) * exp(self._ky0*(self._b-y))
        return Hx3
    def Hy3(self, x, y):
        Hy3 = -1j*self._hy3 * cos(self._kx1*x) * exp(self._ky0*(self._b-y))
        return Hy3

        # Field amplitudes
        # Longitudinal, internal
    @property
    def _ez1(self):
        return 1
    @property
    def _hz1(self):
        ez1   = self._ez1   ; w0    = self._w0    ; epsr2 = self._epsr2 
        kt1sq = self._kt1sq ; b     = self._b     ; ky1   = self._ky1
        ky2   = self._ky2   ; epsr1 = self._epsr1 ; kt2sq = self._kt2sq
        beta  = self._beta  ; Vn    = self._Vn    ; kx1   = self._kx1
        
        hz1=ez1*w0*eps0*(epsr2*kt1sq*cos(b*ky1)*ky2 + epsr1*kt2sq*ky1*sin(b*ky1))/ \
                        (beta*Vn**2*kx1*sin(b*ky1))
        return hz1
        
        # Transversal, internal 
    @property
    def _ex1(self):
        hz1 = self._hz1 ; ky1  = self._ky1  ; w0  = self._w0    
        ez1 = self._ez1 ; beta = self._beta ; kx1 = self._kx1       
        
        ex1=1/self._kt1sq * (hz1*ky1*mu0_umps*w0 + ez1*beta*kx1)
        
        return ex1
    @property
    def _ey1(self):
        kt1sq = self._kt1sq ; hz1 = self._hz1  ; kx1  = self._kx1 
        w0    = self._w0    ; ez1 = self._ez1  ; beta = self._beta     
        ky1   = self._ky1       
        
        ey1=1/self._kt1sq * (hz1*kx1*mu0_umps*w0 - ez1*beta*ky1)
        
        return ey1
    @property
    def _hx1(self):
        kt1sq = self._kt1sq ; ez1 = self._ez1 ; epsr1 = self._epsr1 
        ky1   = self._ky1   ; w0  = self._w0  ; hz1   = self._hz1  
        beta  = self._beta  ; kx1 = self._kx1 
           
        hx1=1/self._kt1sq * (ez1*eps0*epsr1*ky1*w0 - hz1*beta*kx1)
        
        return hx1
    @property
    def _hy1(self):
        ez1 = self._ez1 ; epsr1 = self._epsr1 ; kx1  = self._kx1 
        w0  = self._w0  ; hz1   = self._hz1  ;  beta = self._beta 
        ky1 = self._ky1 
        
        hy1=1/self._kt1sq * (ez1*eps0*epsr1*kx1*w0 + hz1*beta*ky1)
        
        return hy1
        
        # Longitudinal, external (region I Menon, '3' my, wn symm='2')
    @property
    def _ez3(self):
        ez3 = self._ez1 * sin(self._a*self._kx1)   
        return ez3 
    @property
    def _hz3(self):
        hz3 = self._hz1 * cos(self._a*self._kx1)
        return hz3
        
        # Transversal, external, I, 3
    @property
    def _ex3(self):
        hz1  = self._hz1  ; a   = self._a ;  kx1 = self._kx1
        ky1  = self._ky1  ; w0  = self._w0 ; ez1 = self._ez1 
        beta = self._beta ; kx2 = self._kx2 
        
        ex3 = 1/self._kt2sq * \
                (hz1*cos(a*kx1)*ky1*mu0_umps*w0 - ez1*beta*sin(a*kx1)*kx2)
        return ex3
    @property
    def _ey3(self):        
        hz1  = self._hz1  ; a   = self._a  ; kx1 = self._kx1
        kx2  = self._kx2  ; w0  = self._w0 ; ez1 = self._ez1 
        beta = self._beta ; ky1 = self._ky1
        
        ey3 = 1/self._kt2sq * \
                (hz1*cos(a*kx1)*kx2*mu0_umps*w0 - ez1*beta*sin(a*kx1)*ky1)

        return ey3    
    @property
    def _hx3(self):
        ez1 = self._ez1 ; epsr2 = self._epsr2 ; a   = self._a
        kx1 = self._kx1 ; ky1   = self._ky1   ; w0  = self._w0
        hz1 = self._hz1 ; beta  = self._beta  ; kx2 = self._kx2 
        
        hx3 = 1/self._kt2sq * \
                (ez1*eps0*epsr2*sin(a*kx1)*ky1*w0 - hz1*beta*cos(a*kx1)*kx2)
        return hx3
    @property
    def _hy3(self):
        hz1   = self._hz1   ; beta = self._beta ; a   = self._a 
        kx1   = self._kx1   ; ky1  = self._ky1  ; ez1 = self._ez1 
        epsr2 = self._epsr2 ; kx2  = self._kx2  ; w0  = self._w0 
        
        hy3 = 1/self._kt2sq * \
                (hz1*beta*cos(a*kx1)*ky1 - ez1*eps0*epsr2*sin(a*kx1)*kx2*w0) 
        return hy3
    
        # Longitudinal external, II, '0'
    @property
    def _ez0(self):
        ez0 = self._ez1 * cos(self._b*self._ky1)
        return ez0
    @property
    def _hz0(self):
        hz0 = self._hz1 * sin(self._b*self._ky1)
        return hz0
        
        # # Transversal, external, II, '0'
    @property
    def _ex0(self):
        ez1 = self._ez1 ; beta = self._beta ; kx1 = self._kx1 
        b   = self._b   ; ky1  = self._ky1  ; hz1 = self._hz1 
        ky2 = self._ky2 ; w0   = self._w0
        
        ex0 = 1/self._kt2sq * \
                (ez1*beta*kx1*cos(b*ky1) - hz1*sin(b*ky1)*ky2*mu0_umps*w0)
        return ex0
    @property
    def _ey0(self):
        hz1  = self._hz1  ; kx1 = self._kx1 ; b   = self._b 
        ky1  = self._ky1  ; w0  = self._w0  ; ez1 = self._ez1 
        beta = self._beta ; ky1 = self._ky1 ; ky2 = self._ky2 
                
        ey0 = 1/self._kt2sq * \
                (hz1*kx1*sin(b*ky1)*mu0_umps*w0 - ez1*beta*cos(b*ky1)*ky2)        
        return ey0
    @property
    def _hx0(self):
        ez1 = self._ez1 ; epsr2 = self._epsr2 ; b   = self._b
        ky1 = self._ky1 ; ky2   = self._ky2   ; w0  = self._w0 
        hz1 = self._hz1 ; beta  = self._beta  ; kx1 = self._kx1
        
        hx0=1/self._kt2sq * \
                (ez1*eps0*epsr2*cos(b*ky1)*ky2*w0 - hz1*beta*kx1*sin(b*ky1))
        return hx0
    @property
    def _hy0(self):
        ez1 = self._ez1 ; epsr2 = self._epsr2 ; kx1 = self._kx1 
        b   = self._b   ; ky1   = self._ky1   ; w0  = self._w0
        hz1 = self._hz1 ; beta  = self._beta  ; ky2 = self._ky2 

        hy0=1/self._kt2sq * \
                (ez1*eps0*epsr2*kx1*cos(b*ky1)*w0 - hz1*beta*ky2*sin(b*ky1))          
        return hy0
    
    ''' '''
            # Norms guided, class 3
    @property
    def _Ng(self):
        a   = self._a ;   b   = self._b   ;
        ex1 = self._ex1 ; ey1 = self._ey1 ; hx1 = self._hx1 ; hy1 = self._hy1 ;
        ex0 = self._ex0 ; ey0 = self._ey0 ; hx0 = self._hx0 ; hy0 = self._hy0 ;
        ex3 = self._ex1 ; ey3 = self._ey3 ; hx3 = self._hx3 ; hy3 = self._hy3 ;
        kx1 = self._kx1 ; ky1 = self._ky1 ; kx2 = self._kx2 ; ky2 = self._ky2 ;

        Ng1=2*a*b*(ex1*hy1 * (1+sinc(2*kx1*a/pi)) * ((1+sinc(2*ky1*b/pi))) - \
                   ey1*hx1 * (1-sinc(2*kx1*a/pi)) * ((1-sinc(2*ky1*b/pi))))       
            
        Ng0=a/ky2*(ex0*hy0 * (1+sinc(2*kx1*a/pi)) - \
                   ey0*hx0 * (1-sinc(2*kx1*a/pi)))
    
        Ng1=b/kx2*(ex3*hy3 * (1+sinc(2*ky1*b/pi)) - \
                   ey3*hx3 * (1-sinc(2*ky1*b/pi)))
        
        Ng=Ng1+2*(Ng0+Ng1)
        
        return Ng
        
        ## Simulations
    
    ''' '''
    '''
    running the simulation and setting the waveguide instance properties 
    '''
    def simulate(self, waveguide):
            # setting waveguide instance properties
        waveguide.beta, waveguide.beta_normalised, \
        waveguide._kx1, waveguide._ky1, waveguide._kx2, waveguide._ky2, \
        waveguide._kt1sq, waveguide._kt2sq = self._calculate_wavenumbers(waveguide)

        self._beta, self._beta_normalised, \
        self._kx1, self._ky1, self._kx2, self._ky2, self._kt1sq, self._kt2sq = \
        waveguide.beta, waveguide.beta_normalised, \
        waveguide._kx1, waveguide._ky1, waveguide._kx2, waveguide._ky2, \
        waveguide._kt1sq, waveguide._kt2sq
        
