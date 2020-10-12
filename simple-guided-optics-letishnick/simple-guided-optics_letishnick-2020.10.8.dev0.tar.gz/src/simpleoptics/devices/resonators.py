class Fabry_Perot(Waveguide):
    def __init__(self):
        pass


    def reflection_input(self):
        pass
    
    def reflection_output(self):
        pass


    def transmission_f(self):
        ''' [Heebner and Grover], assuming constant reflection frequency dependence
        '''
        r1=np.empty(points_preliminary_interp); r2=np.empty(points_preliminary_interp)
        r1.fill(0.9); r2.fill(0.9)
        t1=1-r1; t2=1-r2

        Tr=neff_calc*length/c_umps
        phi=Tr*(2*pi*f)

        t_w = -t1*t2*2*exp(1j*phi/2)/(1-r1*r2)

        return t_w

    def reflection_f(self):
        ''' [Heebner and Grover], assuming constant reflection frequency dependence
        '''
        r1=np.empty(points_preliminary_interp); r2=np.empty(points_preliminary_interp)
        r1.fill(0.6); r2.fill(0.6)

        Tr=neff*length/c_umps
        # Tr=ng*length/c_umps
        # Tr=length/vg
        phi=Tr*(2*pi*f)
        alpha = 0.99999999

        r_w = r1-r2*alpha*exp(1j*phi)/(1-r1*r2*alpha*exp(1j*phi))

        return r_w




class Gires_Tournois(Waveguide):
    def __init__(self):
        pass

