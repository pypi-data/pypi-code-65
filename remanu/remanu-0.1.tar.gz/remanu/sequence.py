import numpy as np
from tqdm import tqdm
import dolfin as fem
import sys

class fid:
    def __init__(self, model,
            dt= 1.e-3,
            tf= 1.e-1,
            G=  0., g= (1., 0.),
            vtk= None,
            theta= 0.5,
                 ):
        # PARSE ARGUMENTS
        self.model = model

        self.dt = dt
        self.tf = tf

        self.G = G
        self.g = g

        self.theta = theta

        self.vtk_output = vtk

        # THE NUMBER OF ITERATIONS TO PERFORM
        self.nt     = np.int(np.round(self.tf/self.dt)) + 1
        self.t_arr  = np.linspace(0., self.tf, self.nt)

        # SET self AS THE MODEL SEQUENCE
        self.model.set_sequence(self)


    # PULSED-GRADIENT TIME-PROFILE
    def pulse_profile(self, t):
        return 1.


    # EXTERNAL FIELD
    def phase_encode(self):
        if self.model.mesh.topology().dim() == 2:
            return  fem.Expression("f*(G*(gx*x[0] + gy*x[1]))",
                             f      = self.pulse_profile(0.),
                             G      = self.G,
                             gx     = self.g[0],
                             gy     = self.g[1],
                             domain = self.model.mesh,
                             degree = 3,
                                   )
        elif self.model.mesh.topology().dim() == 3:
            return  fem.Expression("f*(G*(gx*x[0] + gy*x[1] + gz*x[2]))",
                             f      = self.pulse_profile(0.),
                             G      = self.G,
                             gx     = self.g[0],
                             gy     = self.g[1],
                             gz     = self.g[2],
                             domain = self.model.mesh,
                             degree = 3,
                                   )


    # RUN THE SEQUENCE
    def run(self, point_eval= None):
        # SOLUTION ARRAYS
        self.model.mt_domains[::, 0] = self.model.eq_integrals[::]
        self.model.mx_domains[::, 0] = self.model.eq_integrals[::]
        self.model.my_domains[::, 0] = 0.

        self.model.mt[0] = self.model.eq_integral

        # POINT EVALUATION
        if point_eval:
            self.point_e = np.zeros((len(point_eval), self.nt))
            self.phase_e = np.zeros((len(point_eval), self.nt))
            for i, point in enumerate(point_eval):
                self.point_e[i, 0] = self.model.eq_mag(point)
                self.phase_e[i, 0] = np.arctan2(self.model.my(point), self.model.mx(point))

        print('initial net magnetization in x-direction is {}Am^2'.format(np.sum(self.model.mt[0])))
        sys.stdout.flush()
        print('saturation  magnetization in z-direction is {}A/m'.format(self.model.msat))
        sys.stdout.flush()

        print('START SIMULATION. {} ITERATIONS WILL BE PERFORMED'.format(self.nt-1))
        sys.stdout.flush()

        if self.vtk_output:
            vtk_file = fem.File('{}.pvd'.format(self.vtk_output))
            vtk_file << self.model.m, 0.

        # ITERATIONS
        for i, t in tqdm(enumerate(self.t_arr[1:]), desc= "Running", total= self.nt-1):
            self.model.mn.vector()[:] = self.model.m.vector()
            self.model.solver.solve(self.model.problem, self.model.m.vector())

            for j, k in enumerate(sorted(list(set(self.model.cellfn.array())))):
                self.model.mx_domains[j, i+1] = fem.assemble(self.model.DomainSelector(self.model.cellfn, k)*self.model.mx*self.model.dx)
                self.model.my_domains[j, i+1] = fem.assemble(self.model.DomainSelector(self.model.cellfn, k)*self.model.my*self.model.dx)
                self.model.mt_domains[j, i+1] = np.sqrt(
                    np.power(self.model.mx_domains[j, i+1], 2) +
                    np.power(self.model.my_domains[j, i+1], 2)
                                                        )

            self.model.mt[i+1] = np.sum(self.model.mt_domains[::,i+1])

            if point_eval:
                for j, point in enumerate(point_eval):
                    self.point_e[j, i+1] = np.sqrt(np.power(self.model.mx(point), 2) + np.power(self.model.my(point), 2))
                    self.phase_e[j, i+1] = np.arctan2(self.model.my(point), self.model.mx(point))

            if self.vtk_output: vtk_file << self.model.m, t

        return self.model.mt/self.model.eq_integral



class cpmg:
    def __init__(self, model,
            dt= 1.e-3,
            ne= 32,
            delta= 4.e-1,
            DELTA= 4.e-1,
            G= 6.e-1, g= (1., 0.),
            vtk= None,
            theta= 0.5,
                 ):
        # PARSE ARGUMENTS
        self.model = model

        self.dt = dt
        self.ne = ne

        self.delta = delta
        self.DELTA = DELTA

        self.G = G
        self.g = g

        self.theta = theta

        self.vtk_output = vtk

        self.tf = 2.*self.ne*self.DELTA

        # THE NUMBER OF ITERATIONS TO PERFORM
        self.nt     = np.int(np.round(self.tf/self.dt)) + 1
        self.t_arr  = np.linspace(0., self.tf, self.nt)
        self.i_flip = np.int(np.round(self.DELTA/self.dt))

        # SET self AS THE MODEL SEQUENCE
        self.model.set_sequence(self)


    # PERFORM A PI RF PULSE (SHORT PULSE LIMIT) THROUGH ALL THE DOMAIN
    def pi_pulse(self):
        m_local = self.model.m.vector().get_local()
        ver2dof = fem.vertex_to_dof_map(self.model.V)
        for i in range(self.model.mesh.coordinates().shape[0]):
            m_local[ver2dof[2*i+1]] *= -1.

        self.model.m.vector().set_local(m_local)
        self.model.m.vector().apply("insert")


    # PULSED-GRADIENT TIME-PROFILE
    def pulse_profile(self, t):
        for i in range(2*(self.ne)+1):
            if i*self.DELTA <= t <= i*self.DELTA+self.delta:
                return 1.
        return 0.


    # EXTERNAL FIELD
    def phase_encode(self):
        if self.model.mesh.topology().dim() == 2:
            return  fem.Expression("f*(G*(gx*x[0] + gy*x[1]))",
                             f      = self.pulse_profile(0.),
                             G      = self.G,
                             gx     = self.g[0],
                             gy     = self.g[1],
                             domain = self.model.mesh,
                             degree = 3,
                                   )
        elif self.model.mesh().topology().dim() == 3:
            return  fem.Expression("f*(G*(gx*x[0] + gy*x[1] + gz*x[2]))",
                             f      = self.pulse_profile(0.),
                             G      = self.G,
                             gx     = self.g[0],
                             gy     = self.g[1],
                             gz     = self.g[2],
                             domain = self.model.mesh,
                             degree = 3,
                                   )


    def run(self, point_eval= None):
        # SOLUTION ARRAYS
        self.model.mt_domains[::, 0] = self.model.eq_integrals[::]
        self.model.mx_domains[::, 0] = self.model.eq_integrals[::]
        self.model.my_domains[::, 0] = 0.

        self.model.mt[0] = self.model.eq_integral

        # POINT EVALUATION
        if point_eval:
            self.point_e = np.zeros((len(point_eval), self.nt))
            self.phase_e = np.zeros((len(point_eval), self.nt+self.ne))
            self.encoded = np.zeros((len(point_eval), self.nt+self.ne))
            self.t_cpmg  = np.zeros(                  self.nt+self.ne)
            for i, point in enumerate(point_eval):
                self.point_e[i, 0] = self.model.eq_mag(point)
                self.phase_e[i, 0] = np.arctan2(self.model.my(point), self.model.mx(point))
                self.t_cpmg[    0] = 0.
                self.encoded[i, 0] = 0.

        print('initial net magnetization in x-direction is {}Am^2'.format(np.sum(self.model.mt[0])))
        sys.stdout.flush()
        print('saturation  magnetization in z-direction is {}A/m'.format(self.model.msat))
        sys.stdout.flush()

        print('START SIMULATION. {} ITERATIONS WILL BE PERFORMED'.format(self.nt-1))
        sys.stdout.flush()

        if self.vtk_output:
            vtk_file = fem.File('{}.pvd'.format(self.vtk_output))
            vtk_file << self.model.m, 0.

        l = 0
        m = 0
        for i, t in tqdm(enumerate(self.t_arr[1:]), desc= "Running", total= self.nt-1):
            self.model.fG.f = self.pulse_profile(t)
            self.model.mn.vector()[:] = self.model.m.vector()
            self.model.solver.solve(self.model.problem, self.model.m.vector())

            for j, k in enumerate(sorted(list(set(self.model.cellfn.array())))):
                self.model.mx_domains[j, i+1] = fem.assemble(self.model.DomainSelector(self.model.cellfn, k)*self.model.mx*self.model.dx)
                self.model.my_domains[j, i+1] = fem.assemble(self.model.DomainSelector(self.model.cellfn, k)*self.model.my*self.model.dx)
                self.model.mt_domains[j, i+1] = np.sqrt(
                    np.power(self.model.mx_domains[j, i+1], 2) +
                    np.power(self.model.my_domains[j, i+1], 2)
                                                        )

            self.model.mt[i+1] = np.sum(self.model.mt_domains[::,i+1])

            if point_eval:
                self.t_cpmg[i+m+1] = t
                for j, point in enumerate(point_eval):
                    self.point_e[j, i  +1] = np.sqrt(np.power(self.model.mx(point), 2) + np.power(self.model.my(point), 2))
                    self.phase_e[j, i+m+1] = np.arctan2(self.model.my(point), self.model.mx(point))
                    self.encoded[j, i+m+1] = self.encoded[j, i+m] - self.model.gamma*self.model.fG(point)*self.dt

            if self.vtk_output: vtk_file << self.model.m, t

            if ((i+1) % self.i_flip) == 0:
                if l % 2 == 0:
                    # print('pi-pulse!')
                    self.pi_pulse()
                    if point_eval:
                        for j, point in enumerate(point_eval):
                            self.phase_e[j, i+m+2] = -self.phase_e[j, i+m+1]
                            self.encoded[j, i+m+2] = -self.encoded[j, i+m+1]
                            self.t_cpmg[    i+m+2] =  t
                        m += 1
                    l += 1
                else:
                    # print('echo!')
                    l += 1

        return self.model.mt/self.model.eq_integral
