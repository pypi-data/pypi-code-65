from simpleoptics.helpers.preambule import *

class Simulation_Goell:
    ''' The classic [Goell 1969] solver of the rectandular waveguide. 
        The python realisation is borrowed from plandrem's github and been 
        enhanced to be more versatile. Furthermore, this method can calculate 
        a trapezoidal wg as well using a sidewall angle variable.

    The correspondence between [Menon 2002] classes and Goell's are as follows
        class 1 x- sym, y- sym modes Ex21, Ex23, Ey12, Ey32,... <- row remove
        class 2 x- sym, y-asym modes Ex22, Ex44, Ey11, Ey33,...
        class 3 x-asym, y- sym modes Ex11, Ex33, Ey22, Ey44,...
        class 4 x-asym, y-asym modes Ex12, Ex32, Ey21, Ey23,... <- row remove
    
     Modeclass is the nonsense variable again, which is to be fixed!
    '''
    def __init__(self,  waveguide, modeclass, number_of_harmonics,
                        units, start=None, stop=None, points=None,
                        centre=None, span=None, step=None):

            # main variables
            # start, stop, step and start, stop, points
        if start is not None and stop is not None:
            if points is not None:
                self._start = start
                self._stop = stop
                self._points = points
            if points is None: # then its step
                self._step = step
                self._points = int((stop - start)/step)

            # start, stop, step and start, stop, points
        if centre is not None and span is not None:
            if points is not None:
                self._start = centre - span/2
                self._stop  = centre + span/2
                self._points = points
            if points is None: # then its step
                self._step = step
                self._points = int(span/step)

        self.units = units
        self.modeclass = modeclass
        self.number_of_harmonics = number_of_harmonics

        ''' pushing the necessary variables to an underlying waveguide instance '''
        self.waveguide = waveguide
        self.set_waveguideunits()
        self.set_waveguide_start()
        self.set_waveguide_stop()
        self.set_waveguide_points()

       # methods to set waveguide properties
    def set_waveguideunits(self):
        self.waveguide.units = self.units

    def set_waveguide_start(self):
        self.waveguide._start = self._start

    def set_waveguide_stop(self):
        self.waveguide._stop = self._stop

    def set_waveguide_points(self):
        self.waveguide._points = self._points

    ''' '''

    def matriceQ(self, i, B2, scale=True):
            # import from the already modified waveguide instance
        Vn = self.waveguide.Vn if self.units == 'wavelength' \
                               else np.flipud(self.waveguide.Vn)
        # if self.units != 'wavelength':
        #     Vn = np.flipud(Vn)

        a = self.waveguide.width /2
        b = self.waveguide.height/2
        ''' this is different from the Menon where 2 was the cladding, but it is
            so here for that the designations of the paper be maintained '''

        epsr1 = self.waveguide.core_epsr if self.units == 'wavelength' \
                               else np.flipud(self.waveguide.core_epsr)
        epsr0 = self.waveguide.cladding_epsr if self.units == 'wavelength' \
                               else np.flipud(self.waveguide.cladding_epsr)
        epsr = epsr1/epsr0

            # Abbrevations
        d = (a+b)/2
        Z0 = sqrt(mu0_umps/(eps0_umps*epsr0))
            # k_i = k_freespace*sqrt(epsr0)
        k0 = Vn*sqrt(epsr0)/(sqrt(epsr1-epsr0))
        k1 = Vn*sqrt(epsr1)/(sqrt(epsr1-epsr0))

                # Les points de correspondance
            # la quantité de points de la série
        N = self.number_of_harmonics
        # nous choisissons entre les types des modes
        ''' в этом месте я искусственно поменял класс 2 и 3 для совпадения с меноном '''
        if self.modeclass==1:                               # sym=0,harm=0 en plandrem
            n=np.arange(0,2*N,  2, dtype=np.int); phi=pi/2
        if self.modeclass==2:                               # sym=0,harm=1
            n=np.arange(1,2*N+1,2, dtype=np.int); phi=0
        if self.modeclass==3:                               # sym=1,harm=1
            n=np.arange(1,2*N+1,2, dtype=np.int); phi=pi/2
        if self.modeclass==4:                               # sym=1,harm=0
            n=np.arange(0,2*N,  2, dtype=np.int); phi=0
            # la liste des points de correspondance
        m = np.linspace(1,N,N,dtype=np.int)
            # la liste de thêtas
        thetam=(m-0.5)*pi/(2*N)
        thetac = arctan(b/a)

        # There's an inconsistency between my efforts to derive the following formulas
        # and the final ones in [Goell 1969]. In fact, there are different versions
        # whhich correspond more or less to my formulas, but I leave the original
        # ones. Here are the mine:
        # R=   sin(thetam)*(thetam<thetac) + cos(thetam+pi/4)*(thetam==thetac) -\
        #     cos(thetam)*(thetam>thetac)
        # T =  cos(thetam)*(thetam<thetac) + cos(thetam-pi/4)*(thetam==thetac) +\
        #      sin(thetam)*(thetam>thetac)
        # rm=a/cos(thetam)*(thetam<thetac) + sqrt(a**2+b**2)*(thetam==thetac) +\
        #     b/sin(thetam)*(thetam>thetac)
        
        # négatif test
        R=   sin(thetam)*(thetam<thetac) + cos(thetam+pi/4)*(thetam==thetac) +\
             cos(thetam)*(thetam>thetac)
        T=   cos(thetam)*(thetam<thetac) + cos(thetam-pi/4)*(thetam==thetac) -\
             sin(thetam)*(thetam>thetac)
        rm=a/cos(thetam)*(thetam<thetac) + sqrt(a**2 + b**2)*(thetam==thetac) +\
           b/sin(thetam)*(thetam>thetac)

            # Les fonctions constituantes
        eLA = np.zeros((N,N),dtype=float); eLC = np.zeros((N,N),dtype=float)
        hLB = np.zeros((N,N),dtype=float); hLD = np.zeros((N,N),dtype=float)
        eTA = np.zeros((N,N),dtype=float); eTB = np.zeros((N,N),dtype=float)
        eTC = np.zeros((N,N),dtype=float); eTD = np.zeros((N,N),dtype=float)
        hTA = np.zeros((N,N),dtype=float); hTB = np.zeros((N,N),dtype=float)
        hTC = np.zeros((N,N),dtype=float); hTD = np.zeros((N,N),dtype=float)

        ''' filling in the matrix '''
        for k in np.arange(0,len(n)):              # on fait les colonnes ...

                # function abbrevations
            S=sin(n[k]*thetam+phi)
            C=cos(n[k]*thetam+phi)
            J=jv(n[k],rm*Vn[i]*sqrt(1-B2))
            K=kv(n[k],rm*Vn[i]*sqrt(B2))
            Jaug= n[k]/(rm*Vn[i]**2*(1-B2))* jv(n[k],rm*Vn[i]*sqrt(1-B2))
            Jpaug= 1  /(Vn[i]*sqrt((1-B2)))*jvp(n[k],rm*Vn[i]*sqrt(1-B2))
            Kaug= n[k]/(rm*Vn[i]**2*B2)*     kv(n[k],rm*Vn[i]*sqrt(B2))
            Kpaug= 1  /(Vn[i]*sqrt(B2))*    kvp(n[k],rm*Vn[i]*sqrt(B2))
            kz=Vn[i]*sqrt((B2+epsr0[i]/(epsr1[i]-epsr0[i])))    # kz=beta
        #   les multiplicateurs des colonnes (sic!)
        #   cela changera le déterminant mais ne changera pas de position de leurs ZEROS
            if scale==True:
        #   les normalisations de Goell
                jnorm=d*Vn[i]**2*(1-B2)/np.absolute(jv(n[k],b*Vn[i]*sqrt(1-B2)))
                knorm=d*Vn[i]**2*  B2 / np.absolute(kv(n[k],b*Vn[i]*sqrt(B2)))
            if scale==False:
                jnorm=1; knorm=1
        #   les blocs de la matrice
        # ... on les met en ligne
            eLA[:,k]=J*S                                        *jnorm
            eLC[:,k]=K*S                                        *knorm
            hLB[:,k]=J*C                                        *jnorm
            hLD[:,k]=K*C                                        *knorm
            eTA[:,k]=-kz*(Jpaug*S*R + Jaug*C*T)                 *jnorm
            eTB[:,k]= k0[i]*Z0[i]*(Jaug*S*R + Jpaug*C*T)        *jnorm
            eTC[:,k]= kz*(Kpaug*S*R + Kaug*C*T)                 *knorm
            eTD[:,k]=-k0[i]*Z0[i]*(Kaug*S*R + Kpaug*C*T)        *knorm
            hTA[:,k]= epsr[i]*k0[i]/Z0[i]*(Jaug*C*R - Jpaug*S*T)*jnorm
            hTB[:,k]=-kz*(Jpaug*C*R - Jaug*S*T)                 *jnorm
            hTC[:,k]=-k0[i]/Z0[i]*(Kaug*C*R - Kpaug*S*T)        *knorm
            hTD[:,k]= kz*(Kpaug*C*R - Kaug*S*T)                 *knorm
        #   la matrice se remplit
        zero = np.zeros(np.shape(eLA))
        Q1 = np.hstack((eLA,zero,-1*eLC,zero))
        Q2 = np.hstack((zero,hLB,zero,-1*hLD))
        Q3 = np.hstack((eTA,eTB,-1*eTC,-1*eTD))
        Q4 = np.hstack((hTA,hTB,-1*hTC,-1*hTD))
        #   la matrice-même se construit
        Q = np.vstack((Q1,Q2,Q3,Q4))
        #   on élimine les lignes et colognes entre les classes I et IV dans les modes z impaires
        if self.modeclass==1:
            Q = np.delete(Q,[N,3*N],1)      # on élimine Hz, axis 1 = column
            Q = np.delete(Q,[N,2*N-1],0)    # Hz, axis 0 = row
        elif self.modeclass==4:
            Q = np.delete(Q,[0,2*N],1)      # Ez, n=0 deux fois
            Q = np.delete(Q,[0,N-1],0)      # Ez, m=1 et N une fois
        else:
            pass                            # mais il n'y a aucune autre possibilité
        #   et finalement
        return Q
    ''' '''
        ## Détérminant
    def detQ(self,i,B2):
        dq = np.linalg.det(self.matriceQ(i,B2))
        return dq
        
        # In the original paper there was a necessity to cut the
        # exorbitating det values. I haven't ever encountered such a behaviour
        # during my studies, so I ignore it.
        
    # # def detQ(B2,seuil=1e70):
    # #     dq = np.linalg.det(matriceQ(B2))
    # #     if abs(dq) > seuil:
    # #         return dq
    # #     else: return 0
    
    ''' '''
        ## Solution
    ''' multimode Goell is abandonned in favour of using modenumber and setting
        modenumber variable. Nevertheless, the full code can be found in
        harmcirc_dispersion_standard.py'''

    def betanorm(self, waveguide, onemode=True):
        betanorm1 = np.empty((0,)); # one mode nombre d'onde

            # je crée la réticule et puis je mets les frontières des solutions
            # à chaque pas mes solutions se basent sur les racines de la determinant
        # B2_test_une = np.linspace(0.005,0.99,100)
        for i in np.arange(self._points):
            det_test = np.empty((0,))  # chaque fois ce massif doit être annulé
                # une mode ou toutes les modes?
                # une mode ici
                # vérifions s'il y a quelque chose dans le massif de betanorm,
                # i.e. au moins une racine a été trouvée
                # c'est vraiment pour éviter des erreurs
            if np.shape(betanorm1)>(0,):
                # nous faisons une réticule entre 0 et la racine courante
                B2_test = np.linspace(np.max([B2_cur-0.1, 0 + 1e-10]), \
                                      np.min([B2_cur+0.1, 1 - 1e-10]), 50)
            else:
                B2_test=np.linspace(0.005, 0.99, 100)

                # la reticule se remplit avec les valeurs de déterminant
            for B2 in B2_test:
                det_test = np.append(det_test,self.detQ(i,B2))
                # les points de changement de la signe...
            diff = np.diff(np.sign(det_test))
                # ...nous en obtenons les indices
            ch = np.where(abs(diff)==2)[0]

                # on éstime le nombre des racines dans notre intérvalle (racnom)
            if i==0:
                racnom=len(ch)
            else:
                pass

                # notre fonction sera
            dqf = lambda B2: self.detQ(i,B2)

                # une mode ou toutes les modes?
                # une mode ici
                # encore nous révisouns si la massif n'est pas vide
                # c'est vraiment pour éviter des erreurs
            if np.shape(ch)>(0,):  # la mode fondamentale est toujours ch[-1]
                B2_cur = sp.optimize.brentq(dqf, B2_test[ch[-1]],
                                                 B2_test[ch[-1]+1])
            else:
                B2_cur = 0
            betanorm1=np.append(betanorm1, B2_cur)

        ''' betanorm1 have to be reversed to the output because it is calculated
            following the decreasing values of V but beta itself no,
            because it is OK !
        '''
        if self.units != 'wavelength':
            betanorm1 = np.flipud(betanorm1)
        else:
            pass

        return betanorm1


    def beta(self, waveguide):

        Vn = self.waveguide.Vn
        epsr1 = self.waveguide.core_epsr
        epsr0 = self.waveguide.cladding_epsr

            # the just beta [rad/μm]
        beta = Vn*sqrt(self.betanorm(waveguide) + epsr0/(epsr1-epsr0))

        return beta

        # Les coéfficients des séries
    def ABCD(self):
        an = np.empty((0,len(n))); bn = np.empty((0,len(n)))
        cn = np.empty((0,len(n))); dn = np.empty((0,len(n)))
        for i in np.arange(0, self._points):
            qmatrice = self.matriceQ(i,betanorm1[i],scale=False)
            A = qmatrice[1:,1:]
            B = -1*qmatrice[1:,0]
            x = sp.linalg.solve(A,B)
            coe = np.insert(x,0,1)
            aT,bT,cT,dT = np.split(coe,4)
            an = np.vstack((an,aT)); bn = np.vstack((bn,bT));
            cn = np.vstack((cn,cT)); dn = np.vstack((dn,dT))

        return None

    # Running the simulation and setting the waveguide instance properties
    def simulate(self, waveguide):
        waveguide.beta_normalised = self.betanorm(waveguide)
        waveguide.beta            = self.beta(waveguide)


 
