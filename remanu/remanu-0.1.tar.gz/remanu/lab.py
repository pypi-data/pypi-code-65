import numpy as np
import matplotlib.pyplot as plt
import dolfin as fem
import matplotlib as mpl
import sys

class lab:
    def __init__(self, mesh, cellfn= None, boundfn= None, periodic= None, show= False, init_const= False, **kwargs):
        # PARSE ARGUMENTS
        self.mesh = mesh

        # IF A cellfn MESHFUNCTION OBJECT IS NOT SUPPLIED, CREATE ONE
        if not cellfn:
            self.cellfn = fem.MeshFunction('size_t', mesh, mesh.topology().dim())
        else:
            self.cellfn = cellfn

        # IF A boundfn MESHFUNCTION OBJECT IS NOT SUPPLIED, CREATE ONE
        if not boundfn:
            self.boundfn = fem.MeshFunction('size_t', mesh, mesh.topology().dim()-1)
        else:
            self.boundfn = boundfn

        # DEFINE MEASURES
        self.dx = fem.Measure('dx', domain= self.mesh, subdomain_data= self.cellfn)
        self.ds = fem.Measure('ds', domain= self.mesh, subdomain_data= self.boundfn)

        # THE PERIODIC BOUNDARY OBJECT
        self.periodic = periodic

        # VISUALIZATION OF eq_mag
        self.show_eq_mag = show

        # THE INITIAL CONDITION
        self.init_const = init_const

        # SET DEFAULT PHYSICAL PARAMETERS
        self.set_physical_parameters(**kwargs)


    def set_physical_parameters(self, B0  = 1.e-2, # 10 mT
                                      D   = 3.e-9, # water
                                      rho = 2.e-5,
                                      T2  = 1.0,   # water
                                      T1  = 1.2,   # water
                                      gamma=  267.5000e+6, # gyromagnetic
                                      temp =    3.0315e+2, # room
                                      molw =   18.0150e-3, # water
                                      density = 9.9700e+2, # water
                                      molf =    2.,        # water
                                ):
        # PHYSICAL PARAMETERS
        self.B0  = B0
        self.D   = D
        self.T2  = T2
        self.T1  = T1
        self.gamma = gamma

        # CALCULATE THE SATURATION MAGNETIZATION
        AVOGADRO_NUMBER  =  6.0220e23

        proton_density   = (molf*AVOGADRO_NUMBER*density/molw)

        HPLANCK = 6.626e-34
        KBOLTZ  = 1.380e-23

        # THE SATURATION MAGNETIZATION IN ABSENCE OF BOUNDARY EFFECTS
        self.msat  = proton_density*self.B0*np.power(self.gamma*HPLANCK, 2)
        self.msat /= 4.*KBOLTZ*temp

        # HANDLES THE RELAXIVITY VALUES FOR DIFFERENT BOUNDARIES SO rho CAN
        # BE USED AS A COEFFICIENT IN THE VARIATIONAL FORM
        class SurfaceRelaxivity(fem.UserExpression):
            def __init__(self, mesh, boundfn, rho, **kwargs):
                self.cells = tuple(fem.cells(mesh))
                self.boundfn = boundfn.array()
                self.rho = rho
                self.entity = mesh.topology().dim()-1
                super().__init__(**kwargs)
            def eval_cell(self, values, x, cell):
                values[0] = self.rho[self.boundfn[self.cells[cell.index].entities(self.entity)[cell.local_facet]]]
            def value_shape(self):
                return ()

        # MAKE SURE rho IS A LIST WITH len MATCHING THE NUMBER OF BOUNDARIES WITH ID
        if isinstance(rho, float): rho = [rho]
        assert len(rho) == len(set(self.boundfn.array())), \
            'rho does not match the number of boundaries'

        # CREATE rho OBJECT
        self.rho = SurfaceRelaxivity(self.mesh, self.boundfn, rho, degree= 0)

        # CALCULATE THE MESH VOLUME, SURFACE AREA AND AVERAGE RELAXIVITY
        self.volume = self.calculate_volume()
        self.area =   self.calculate_surface_area()
        self.relaxivity = self.calculate_average_relaxivity()
        self.T2an = 1./(1./self.T2 + (self.area/self.volume)*self.relaxivity)

    # CALCULATE THE MESH VOLUME
    def calculate_volume(self):
        volume = 0.
        for cell in fem.cells(self.mesh):
            volume += cell.volume()
        return volume

    # CALCULATE THE MESH SURFACE AREA
    def calculate_surface_area(self):
        bmesh  = fem.BoundaryMesh(self.mesh, 'exterior')
        area = 0.
        for cell in fem.cells(bmesh):
            area += cell.volume()
        return area

    # CALCULATE THE AVERAGE RELAXIVITY
    def calculate_average_relaxivity(self):
        return fem.assemble(self.rho*self.ds)/self.area

    # SET THE PULSE SEQUENCE, A SEQUENCE OBJECT
    def set_sequence(self, sequence):
        self.sequence = sequence
        self.setup()

    # SETUP THE FUNCTION SPACES, VARIATIONAL FORMS, SOLVER, ETC
    def setup(self):
        # SETUP: THE _out ARRAYS
        self.mt_domains = np.zeros((len(set(self.cellfn.array())), self.sequence.nt))
        self.mx_domains = np.zeros((len(set(self.cellfn.array())), self.sequence.nt))
        self.my_domains = np.zeros((len(set(self.cellfn.array())), self.sequence.nt))
        self.mt = np.zeros(self.sequence.nt)

        # SETUP: FEM SPACES, FORMS, ETC...
        fem.parameters['form_compiler']['optimize']     = True
        fem.parameters['form_compiler']['cpp_optimize'] = True

        # FUNCTION SPACES
        self.P = fem.FiniteElement('P', self.mesh.ufl_cell(), 1)

        self.V = fem.FunctionSpace(self.mesh,
                                   fem.MixedElement(
                                       (self.P, self.P)
                                   ), constrained_domain= self.periodic,
                                  )

        # THE TEST FUNCTIONS
        u, v = fem.TestFunctions(self.V)

        # THE SOLUTIONS
        self.m  = fem.Function(self.V, name= 'm' )
        self.mn = fem.Function(self.V, name= 'mn')

        # CALCULATE THE EQUILIBRIUM MAGNETIZATION
        if not self.init_const:
            self.eq_mag, self.eq_integrals = self.equilibrium_magnetization(show= self.show_eq_mag)
            self.eq_integral = np.sum(self.eq_integrals)
        else:
            self.eq_mag = fem.Constant(self.msat)
            self.eq_integrals = np.zeros(len(set(self.cellfn.array())))
            for i, j in enumerate(sorted(list(set(self.cellfn.array())))):
                self.eq_integrals[i] = fem.assemble(self.DomainSelector(self.cellfn, j)*self.eq_mag*self.dx)
            self.eq_integral = np.sum(self.eq_integrals)

        # CREATE INITIAL CONDITIONS
        self.set_init_condition()

        # SPLIT THE 'VECTOR-VALUED' FUNCTIONS INTO 'COMPONENT-VALUED' FUNCTIONS
        self.mx, self.my = fem.split(self.m)

        mxn, myn = fem.split(self.mn)

        mxnt = self.sequence.theta*self.mx + \
                (1. - self.sequence.theta)*mxn
        mynt = self.sequence.theta*self.my + \
                (1. - self.sequence.theta)*myn

        # GET THE PHASE ENCODING FIELD
        self.fG   = self.sequence.phase_encode()
        self.fG.f = self.sequence.pulse_profile(0.)

        # THE VARIATIONAL PROBLEM
        dt    = fem.Constant(1./self.sequence.dt)
        theta = fem.Constant(self.sequence.theta)
        gamma = fem.Constant(self.gamma)
        T2 = fem.Constant(1./self.T2)
        D  = fem.Constant(self.D)

        L1 = dt*(self.mx-mxn)*u*self.dx   - \
             gamma*self.fG*mynt*u*self.dx + \
             T2*mxnt*u*self.dx            + \
             D*fem.dot(fem.grad(mxnt), fem.grad(u))*self.dx
        L2 = dt*(self.my-myn)*v*self.dx   + \
             gamma*self.fG*mxnt*v*self.dx + \
             T2*mynt*v*self.dx            + \
             D*fem.dot(fem.grad(mynt), fem.grad(v))*self.dx

        L1 += self.rho*mxnt*u*self.ds
        L2 += self.rho*mynt*v*self.ds

        # THE VARIATIONAL FORM
        self.L = L1 + L2

        # NONLINEAR PROBLEM SETUP
        dm = fem.TrialFunction(self.V)
        a  = fem.derivative(self.L, self.m, dm)
        self.problem = self.BTInterface(a, self.L)

        # SOLVER PARAMETERS
        self.solver = fem.NewtonSolver()
        self.solver.parameters['linear_solver'] = 'lu'
        self.solver.parameters['convergence_criterion'] = 'incremental'
        self.solver.parameters['relative_tolerance'] = 1.e-10

    # RUN
    def run(self, point_eval= None):
        return self.sequence.run(point_eval= point_eval)

    # CALCULATE THE EQUILIBRIUM MAGNETIZATION IN THE Z-DIRECTION
    def equilibrium_magnetization(self, show= True, save= False):
        V = fem.FunctionSpace(self.mesh, 'CG', 1, constrained_domain= self.periodic)

        u, v = fem.TrialFunction(V), fem.TestFunction(V)

        DT = fem.Constant(self.D*self.T1)
        a = (DT*fem.dot(fem.grad(u), fem.grad(v)) + u*v)*self.dx + fem.Constant(self.T1)*self.rho*u*v*self.ds

        eq_mag = fem.Function(V, name= 'm')
        fem.solve(a == fem.Constant(self.msat)*v*self.dx, eq_mag)

        # PLOT TO THE TERMINAL
        if show:
            with plt.style.context('seaborn-bright'):
                mpl.rcParams['lines.linewidth'] = 1.

                fig, ax = plt.subplots(figsize= (10, 10))

                clb = fem.plot(eq_mag/self.msat, levels= 256, cmap= 'inferno')
                con = fem.plot(eq_mag/self.msat, levels=  32, mode= 'contour', colors= 'black')
                clb = plt.colorbar(clb); clb.ax.set_title(r'$m_{\mathrm{eq}}/m_\mathrm{sat}$')

                plt.title('Eq. magnetization')
                plt.xlabel('x (m)'); plt.xticks(rotation= 90.)
                plt.ylabel('y (m)')

                if save:
                    plt.savefig('{}.pdf'.format(save))
                    plt.savefig('{}.png'.format(save))

                plt.show()

        # CALCULATE INTEGRALS
        eq_integrals = np.zeros(len(set(self.cellfn.array())))
        for i, j in enumerate(sorted(list(set(self.cellfn.array())))):
            eq_integrals[i] = fem.assemble(self.DomainSelector(self.cellfn, j)*eq_mag*self.dx)

        return eq_mag, eq_integrals

    # SET THE EQUILIBRIUM MAGNETIZATION AS INITIAL CONDITION IF NOT init_const
    def set_init_condition(self):
        vertex2dof = fem.vertex_to_dof_map(self.V)
        if not self.init_const:
            m_local   =      self.m.vector().get_local()
            meq_local = self.eq_mag.vector().get_local()

            for i in range(self.mesh.coordinates().shape[0]):
                m_local[vertex2dof[2*i+0]] = meq_local[vertex2dof[2*i]//2]
                m_local[vertex2dof[2*i+1]] = 0.
        else:
            m_local = self.m.vector().get_local()

            for i in range(self.mesh.coordinates().shape[0]):
                m_local[vertex2dof[2*i+0]] = self.msat
                m_local[vertex2dof[2*i+1]] = 0.

        self.m.vector().set_local(m_local)
        self.m.vector().apply('insert')

    # CLASS FOR INTERFACING WITH THE NEWTON SOLVER
    class BTInterface(fem.NonlinearProblem):
        def __init__(self, a, L):
            fem.NonlinearProblem.__init__(self)
            self.a = a
            self.L = L
        def F(self, b, x):
            fem.assemble(self.L, tensor= b)
        def J(self, A, x):
            fem.assemble(self.a, tensor= A)

    # FOR SPECIFIC DOMAIN INTEGRATION
    class DomainSelector(fem.UserExpression):
        def __init__(self, cellfn, i, **kwargs):
            self.cellfn = cellfn.array()
            self.i = i
            super().__init__(**kwargs)
        def eval_cell(self, values, x, cell):
            values[0] = 1. if self.cellfn[cell.index] == self.i else 0.
        def value_shape(self):
            return ()
