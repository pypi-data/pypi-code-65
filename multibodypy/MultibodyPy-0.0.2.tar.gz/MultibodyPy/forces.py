import numpy as np
from MultibodyPy import bodies


def cross(a, b):
    c = [a[1] * b[2] - a[2] * b[1],
         a[2] * b[0] - a[0] * b[2],
         a[0] * b[1] - a[1] * b[0]]

    return np.array(c)


def norm(a):
    return np.sqrt(a[0]**2 + a[1]**2 + a[2]**2)


class Force:
    def __init__(self, p1: bodies.Marker, p2: bodies.Marker, save=False, name='Force'):
        self.p1 = p1
        self.p2 = p2
        self.body1 = p1.body
        self.body2 = p2.body

        self.save = save
        if self.save:
            self.force_saver = ForceSaver()

        self.F1 = 0
        self.F2 = 0
        self.M1 = 0
        self.M2 = 0

        self.name = name

    def get_force(self):
        pass


class Bushing(Force):
    def __init__(self, p1: bodies.Marker, p2: bodies.Marker,
                 K: np.array, D: np.array, Kr: np.array, Dr: np.array,
                 save=True, name='Bushing'):
        Force.__init__(self, p1, p2, save, name)
        self.K = K
        self.D = D
        self.Kr = Kr
        self.Dr = Dr

        self.u0 = self.u
        self.phi0 = self.kardan_diff

    def get_force(self):
        # location of connection points
        rSP10 = np.dot(self.body1.A0K, self.p1.rSPK)
        rSP20 = np.dot(self.body2.A0K, self.p2.rSPK)
        r0P10 = self.body1.r0S0 + rSP10
        r0P20 = self.body2.r0S0 + rSP20

        # velocitiy of connection points
        v01P0 = self.body1.v0S0 + np.cross(self.body1.om0KK, self.p1.rSPK)
        v02P0 = self.body2.v0S0 + np.cross(self.body2.om0KK, self.p2.rSPK)

        # linearized angles between bodys, small angle approximation: cos(phi) -> 1, sin(phi) -> phi
        # in Kardan-Angles
        kardan_12 = self.kardan_diff

        # Forces (Stiffness and Damping)
        dx = (r0P10 - r0P20) - self.u0
        dv = v01P0 - v02P0
        dom = np.dot(self.body1.A0K, self.body1.om0KK) - \
            np.dot(self.body2.A0K, self.body2.om0KK)
        self.F1 = -np.dot(self.K, dx) - np.dot(self.D, dv)
        self.F2 = -self.F1

        # Moments (Stiffness, Damping and spin angular momentum)
        self.M1 = np.cross(rSP10, self.F1) - np.dot(self.Dr,
                                                    dom) + np.dot(self.Kr, kardan_12 - self.phi0)
        self.M2 = np.cross(rSP20, self.F2) + np.dot(self.Dr,
                                                    dom) - np.dot(self.Kr, kardan_12 - self.phi0)

        return self.F1, self.M1, self.F2, self.M2

    @property
    def u(self):
        r0P10 = self.body1.r0S0 + np.dot(self.body1.A0K, self.p1.rSPK)
        r0P20 = self.body2.r0S0 + np.dot(self.body2.A0K, self.p2.rSPK)
        u = r0P10 - r0P20
        return u

    @property
    def pE0(self):
        r0P10 = self.body1.r0S0 + np.dot(self.body1.A0K, self.p1.rSPK)
        r0P20 = self.body2.r0S0 + np.dot(self.body2.A0K, self.p2.rSPK)
        u = r0P10 - r0P20
        return u

    @property
    def kardan_diff(self):
        A01 = self.body1.A0K
        A02 = self.body2.A0K
        A12 = np.dot(A01.T, A02)
        ga_12 = -A12[0, 1]
        be_12 = A12[0, 2]
        al_12 = -A12[1, 2]
        return np.array([al_12, be_12, ga_12])


class PointForce(Force):
    def __init__(self, p1: bodies.Marker, p2: bodies.Marker, F, move_with_body=False, save=False, name='PointForce'):
        Force.__init__(self, p1, p2, save, name)
        self.F = np.array(F)
        self.move_with_body = move_with_body

    def get_force(self):
        # Force Point on 1
        rSP10 = np.dot(self.body1.A0K, self.p1.rSPK)

        # Forces
        if self.move_with_body:
            self.F1 = np.dot(self.body1.A0K, self.F)
        else:
            self.F1 = self.F
        self.F2 = -self.F1

        # Moments
        self.M1 = np.cross(rSP10, self.F1)
        self.M2 = -self.M1

        return self.F1, self.M1, self.F2, self.M2


class PointMoment(Force):
    def __init__(self, p1: bodies.Marker, p2: bodies.Marker, M, save=False, name='PointMoment'):
        Force.__init__(self, p1, p2, save, name)
        self.M = np.array(M)

    def get_force(self):
        # Forces
        self.F1 = np.zeros(3)
        self.F2 = self.F1

        # Moments
        self.M1 = self.M
        self.M2 = -self.M

        return self.F1, self.M1, self.F2, self.M2


class PointForceLoc(PointForce):
    def __init__(self, p1: bodies.Marker, p2: bodies.Marker, F: np.array, left_boundary=0, right_boundary=np.inf,
                 move_with_body=False, save=False, name='PointForceLoc'):
        PointForce.__init__(self, p1, p2, F, move_with_body, save, name)
        self.bs = left_boundary
        self.be = right_boundary

    def get_force(self):
        # Force Point on 1
        rSP10 = np.dot(self.body1.A0K, self.p1.rSPK)
        rSP20 = np.dot(self.body2.A0K, self.p2.rSPK)

        # Forces
        if not any(self.p1.rSPK > self.be) and not any(self.p1.rSPK < self.bs):
            if self.move_with_body:
                self.F1 = np.dot(self.body1.A0K, self.F)
            else:
                self.F1 = self.F
        else:
            self.F1 = np.zeros(3)
        self.F2 = -self.F1

        # Moments
        self.M1 = np.cross(rSP10, self.F1)
        self.M2 = np.cross(rSP20, self.F2)

        return self.F1, self.M1, self.F2, self.M2


class DampingForce(Force):
    def __init__(self, p1: bodies.Marker, p2: bodies.Marker, damping: np.array, save=False, name='DampingForce'):
        super().__init__(p1, p2, save, name)
        self.damping = np.diag(damping)

    def get_force(self):
        v1 = self.p1.body.v0S0
        v2 = self.p2.body.v0S0
        A02 = self.p2.body.A0K

        dv = v2 - v1
        dv2 = np.dot(A02, dv)

        F = np.dot(self.damping, dv2)

        return F, np.zeros(3), -F, np.zeros(3)


class ForceSaver:
    def __init__(self):
        self.F = None

    def save(self, F: np.array):
        if self.F is None:
            self.F = F
        else:
            self.F = np.vstack((self.F, F))


class Contact(Force):
    def __init__(self, body1: bodies.RigidBody, body2: bodies.RigidBody, p1: bodies.Marker, p2: bodies.Marker, n2: np.array, k, d, fric=None, save=True, name='Contact'):
        Force.__init__(self, p1, p2, save, name)
        self.body1 = body1
        self.body2 = body2
        self.n2 = np.array(n2)
        self.k = k
        self.d = d
        self.fric = fric

    def get_force(self):
        A01 = self.body1.A0K
        A02 = self.body2.A0K

        # Point locations
        r1P0 = np.dot(A01, self.p1.rSPK)
        r2P0 = np.dot(A02, self.p2.rSPK)

        # get current gap and velocity
        dn, vn = self.get_gap_velcotiy_normal
        # compute contact normal force
        if dn < 0:
            Fn = self.get_normal_force(dn, vn)

            if self.fric is not None:
                vt, et = self.get_velocity_tangential
                Ft = -self.fric.get_friction_force(Fn, vt)
            else:
                Ft = 0
                et = 0

            F = Fn * self.n2 + Ft * et

        else:
            F = np.zeros(3)

        # forces and moments acting on bodies
        self.F1 = -np.dot(A02, F)
        self.F2 = np.dot(A02, F)
        self.M1 = np.dot(A01.T, cross(r1P0, self.F1))
        self.M2 = np.dot(A02.T, cross(r2P0, self.F2))
        # self.M1 = np.cross(r1P1, self.F1)
        # self.M2 = np.cross(r2P2, self.F2)

        return self.F1, self.M1, self.F2, self.M2

    def get_normal_force(self, dn, vn):
        return 0

    @property
    def get_gap_velcotiy_normal(self):
        # location of bodies
        r010 = self.body1.r0S0
        r020 = self.body2.r0S0

        # velocities of bodies
        v010 = self.body1.v0S0
        v020 = self.body2.v0S0

        # rotation matrices
        A01 = self.body1.A0K
        A02 = self.body2.A0K

        # derivation of rotation matrices
        A01d = self.body1.A0Kd
        A02d = self.body2.A0Kd

        # local location of Points
        r1P1 = self.p1.rSPK
        r2P2 = self.p2.rSPK

        # Location Vector between Contact Points
        d0 = r010 + np.dot(A01, r1P1) - r020 - np.dot(A02, r2P2)

        # Velocity Vector betwwen Contact Points
        d0d = v010 + np.dot(A01d, r1P1) - v020 - np.dot(A02d, r2P2)

        # Transform to plane coordinate system
        d2 = np.dot(A02.T, d0)
        d2d = np.dot(A02.T, d0d)

        # Perpendicular Vector to plane
        d = np.dot(d2.T, self.n2)
        v = np.dot(d2d.T, self.n2)

        return d, v

    @property
    def get_velocity_tangential(self):
        # location of bodies
        r010 = self.body1.r0S0
        r020 = self.body2.r0S0

        # velocities of bodies
        v010 = self.body1.v0S0
        v020 = self.body2.v0S0

        # rotation matrices
        A01 = self.body1.A0K
        A02 = self.body2.A0K

        # derivation of rotation matrices
        A01d = self.body1.A0Kd
        A02d = self.body2.A0Kd

        # local location of Points
        r1P1 = self.p1.rSPK
        r2P2 = self.p2.rSPK

        # Velocity Vector betwwen Contact Points
        d0d = v010 + np.dot(A01d, r1P1) - v020 - np.dot(A02d, r2P2)

        # Transform to plane coordinate system
        d2d = np.dot(A02.T, d0d)

        # Perpendicular Vector to plane
        v = np.dot(d2d.T, self.n2)

        # Tangential velocity
        vt2 = d2d - v * self.n2
        vt2n = norm(vt2)

        # Tangential direction
        if vt2n != 0:
            et2 = vt2 / vt2n
        else:
            et2 = np.array([0, 0, 0])

        return vt2, et2


class KelvinVoigtContact(Contact):
    def __init__(self, body1: bodies.RigidBody, body2: bodies.RigidBody, p1: bodies.Marker, p2: bodies.Marker, n2: np.array, k, d, fric=None, save=True, name='KelvinVoigtContact'):
        Contact.__init__(self, body1, body2, p1, p2,
                         n2, k, d, fric, save, name)

    def get_normal_force(self, dn, vn):
        Fk = self.k * dn
        Fd = self.d * vn

        # Damping !< Contact Force to prevent contact sticking
        if np.abs(Fd) > np.abs(Fk):
            Fd = np.sign(Fd)*np.abs(Fk)
        F = Fk + Fd
        return F


class Friction:
    def __init__(self, mud, vd):
        self.mud = mud
        self.vd = vd

    def get_friction_force(self, Fn, vt):
        return 0


class SimpleFriction(Friction):
    def __init__(self, mud, vd):
        Friction.__init__(self, mud, vd)

    def get_friction_force(self, Fn, vt):
        # absolute tangential velocity
        vtabs = np.linalg.norm(vt)

        # linear Friction force when 0<v<vd
        if vtabs < self.vd:
            Ft = self.mud * vtabs * Fn / self.vd
        else:
            Ft = self.mud * Fn

        return Ft


class StribeckFriction(Friction):
    def __init__(self, mus, vs, mud, vd):
        Friction.__init__(self, mud, vd)
        self.mus = mus
        self.vs = vs

    def get_friction_force(self, Fn, vt):
        # absolute tangential velocity
        vtabs = np.linalg.norm(vt)

        # linear Friction force when 0<v<vd
        if 0 <= np.abs(vtabs) <= self.vs:
            mu = self.mus * vtabs / self.vs
        elif self.vs < np.abs(vtabs) <= self.vd:
            m = (self.mud - self.mus) / (self.vd - self.vs)
            t = np.sign(vtabs) * (self.mus * self.vd - self.mud *
                                  self.vs) / (self.vd - self.vs)
            mu = m * vtabs + t
        else:
            mu = np.sign(vtabs) * self.mud

        Ft = mu * Fn

        return Ft


class BilinearStribeckFriction(Friction):
    def __init__(self, mus, vs, mud, vd, m):
        Friction.__init__(self, mud, vd)
        self.mus = mus
        self.vs = vs
        self.m = m

    def get_friction_force(self, Fn, vt):
        # absolute tangential velocity
        vtabs = np.linalg.norm(vt)

        # linear Friction force when 0<v<vd
        if 0 <= np.abs(vtabs) <= self.vs:
            mu = self.mus * vtabs / self.vs
        elif self.vs < np.abs(vtabs) <= self.vd:
            m = (self.mud - self.mus) / (self.vd - self.vs)
            t = np.sign(vtabs) * (self.mus * self.vd - self.mud *
                                  self.vs) / (self.vd - self.vs)
            mu = m * vtabs + t
        else:
            t = np.sign(vtabs) * (self.mud - self.m * self.vd)
            mu = (self.m * vtabs + t)

        Ft = mu * Fn

        return Ft
