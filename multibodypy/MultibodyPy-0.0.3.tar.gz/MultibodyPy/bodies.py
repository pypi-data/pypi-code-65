import numpy as np
import MultibodyPy
import pickle


def tilde(vec: np.array):
    til = np.array(
        [[0, -vec[2], vec[1]], [vec[2], 0, -vec[0]], [-vec[1], vec[0], 0]])
    return til


class RigidBody:
    dof = 13

    def __init__(self, mass, theta, q0, animation=None, name='RigidBody'):
        self.M = np.zeros([6, 6])
        self.M[0:3, 0:3] = np.array(mass)
        self.M[3:6, 3:6] = np.array(theta)
        self.theta = np.array(theta)
        self.mass = np.array(mass)

        self.q0 = np.array(q0)
        self.q = np.array(q0)
        self.r0S0 = np.array(q0[0:3])
        self.pE = np.array(q0[3:7])
        self.pEn = np.array(np.zeros(4))
        self.v0S0 = np.array(q0[7:10])
        self.om0KK = np.array(q0[10:13])
        self.y, self.z = self.initialize_y_z
        self.zp = np.zeros(6)

        self.qd = np.zeros(13)
        self.F = np.zeros(3)

        self.Fext = np.zeros(3)
        self.Mext = np.zeros(3)

        self.A0K = np.zeros([3, 3])
        self.A0Kd = np.zeros([3, 3])
        self.G = np.zeros([3, 3])
        self.L = np.zeros([3, 3])

        self.posy = 0
        self.posz = 0
        self.pos = 0

        self.animation = animation

        self.initialize_state()

        self.name = name

    def add_force_moment(self, force):
        self.F = self.F + np.array(force)

    def add_acceleration(self, acceleration):
        self.F = self.F + np.dot(self.mass, np.array(acceleration))

    def reset_external_force_moment(self):
        self.Fext = np.zeros(3)
        self.Mext = np.zeros(3)

    def add_external_force_moment(self, force, moment):
        self.Fext = self.Fext + force
        self.Mext = self.Mext + moment

    def update_state(self, q_global):
        self.y = q_global[self.posy:self.posy + 7]
        self.z = q_global[self.posz:self.posz + 6]
        self.r0S0 = self.y[0:3]
        self.pE = self.y[3:7]
        self.pEn = self.pE / np.linalg.norm(self.pE)
        self.v0S0 = self.z[0:3]
        self.om0KK = self.z[3:6]
        self.A0K, self.G, self.L = self.rotation_matrix(self.pEn)
        self.A0Kd = self.derivation_rotation_matrix

    def initialize_state(self):
        self.r0S0 = self.y[0:3]
        self.pE = self.y[3:7]
        self.pEn = self.pE / np.linalg.norm(self.pE)
        self.v0S0 = self.z[0:3]
        self.om0KK = self.z[3:6]
        self.A0K, self.G, self.L = self.rotation_matrix(self.pEn)

    def update_velocities(self, q_global):
        self.z = q_global[self.posz:self.posz + 6]
        self.v0S0 = self.z[0:3]
        self.om0KK = self.z[3:6]

    def update_acceleration(self, qp_global):
        self.zp = qp_global[self.posz:self.posz + 6]
        self.a0S0 = self.zp[0:3]

    def kinematic_ode(self):
        # kinematische DGL
        pEp = 0.5 * np.dot(self.L.transpose(), self.om0KK) + \
            np.linalg.norm(self.om0KK) * (self.pEn - self.pE)
        yp = np.concatenate((self.v0S0, pEp))
        return yp

    def force_moment(self):
        # forces and moments (with spin angular momentum)
        force = self.F + self.Fext
        moment = np.dot(self.A0K.transpose(), self.Mext) - \
            np.cross(self.om0KK, np.dot(self.theta, self.om0KK))
        b = np.concatenate((force, moment))
        return b

    @property
    def initialize_y_z(self):
        y, z = np.array_split(self.q0, 2)
        return y, z

    def header(self, save_acceleration=False):
        h = []
        h.append(self.name + '_x')
        h.append(self.name + '_y')
        h.append(self.name + '_z')
        h.append(self.name + '_vx')
        h.append(self.name + '_vy')
        h.append(self.name + '_vz')
        if save_acceleration:
            h.append(self.name + '_ax')
            h.append(self.name + '_ay')
            h.append(self.name + '_az')
        return h

    @staticmethod
    def rotation_matrix(pE):
        e0, e1, e2, e3 = pE
        G = np.array(
            [[-e1, e0, -e3, e2], [-e2, e3, e0, -e1], [-e3, -e2, e1, e0]])
        L = np.array(
            [[-e1, e0, e3, -e2], [-e2, -e3, e0, e1], [-e3, e2, -e1, e0]])
        A0K = np.dot(G, L.transpose())
        return A0K, G, L

    @property
    def derivation_rotation_matrix(self):
        pEp = 0.5 * np.dot(self.L.transpose(), self.om0KK)
        _, Gp, _ = self.rotation_matrix(pEp)
        A0Kd = 2 * np.dot(Gp, self.L.transpose())
        return A0Kd


class RigidBody1D(RigidBody):
    dof = 1

    def __init__(self, mass, q0, axis=[1, 0, 0], animation=None, name='RigidBody1D'):
        self.M = mass

        self.q0 = np.array(q0)
        self.q = np.array(q0)
        self.r = np.array(q0[0])
        self.v = np.array(q0[1])
        self.y = self.r
        self.z = self.v

        self.qd = np.zeros(2)
        self.F = np.zeros(1)
        self.Fext = np.zeros(1)

        self.posy = 0
        self.posz = 0
        self.pos = 0

        self.axis = np.array(axis)

        self.animation = animation

        self.name = name

    @property
    def header(self):
        h = []
        h.append(self.name + '_r')
        h.append(self.name + '_v')
        return h

    def update_state(self, q_global):
        self.r = q_global[self.posy]
        self.v = q_global[self.posz]

    def add_force_moment(self, force):
        self.F = self.F + np.array(force[0])

    def add_acceleration(self, acceleration):
        self.F = self.F + self.M * acceleration

    def reset_external_force_moment(self):
        self.Fext = np.zeros(1)

    def add_external_force_moment(self, force, moment):
        self.Fext = self.Fext + force[0]

    def force_moment(self):
        # forces
        force = self.F + self.Fext
        return force

    def kinematic_ode(self):
        return self.v


class Ground(RigidBody):
    def __init__(self, q, animation=None, name='Ground'):
        q0 = np.array(q)
        RigidBody.__init__(self, np.zeros(
            [3, 3]), np.zeros([3, 3]), q0, animation, name)
        pE = q[3:7]
        self.A0K, _, _ = self.rotation_matrix(pE)

    @staticmethod
    def qdot(t, q):
        return np.zeros(13)

    @staticmethod
    def Jg():
        Z = np.zeros([3, 3])
        return np.concatenate((Z, Z))


class BlenderAnimation:
    def __init__(self, name, blender_body):
        self.blender_body = blender_body
        self.name = name
        self.dimension = None
        self.marker_dictionary = None
        self.position_saver = PositionSaver()

    @classmethod
    def as_cube(cls, name, dimension: list):
        animation = cls(name, 'Cube')
        animation.dimension = np.array(dimension)
        return animation

    def create_marker(self, marker_dictionary):
        self.marker_dictionary = marker_dictionary


class BlenderAnimationFile:
    def __init__(self, name, time, positions, bodies, animated_ground=None, moving_marker=None):
        self.name = name
        self.time = time
        self.positions = positions
        self.bodies = bodies
        if animated_ground is None:
            self.animated_ground = []
        else:
            self.animated_ground = animated_ground

        if moving_marker is None:
            self.moving_marker = []
        else:
            self.moving_marker = moving_marker

    def save(self):
        with open(self.name, 'wb') as f:
            pickle.dump(self.time, f)
            pickle.dump(self.positions, f)
            pickle.dump(self.bodies, f)
            pickle.dump(self.animated_ground, f)
            pickle.dump(self.moving_marker, f)


class Marker:
    def __init__(self, rSPK, body):
        self.rSPK = np.array(rSPK)
        self.body = body


class MovingMarker(Marker):
    def __init__(self, r_start, body, velocity, t_start=0, save=False, animation=None):
        self.r0 = r_start
        self.body = body
        self.velocity = np.array(velocity)
        self.t_start = t_start
        self.rSPK = self.r0

        self.save = save
        if self.save or animation is not None:
            self.position_saver = PositionSaver()

        self.animation = animation

    def update_location(self, t):
        if t >= self.t_start:
            self.rSPK = self.r0 + self.velocity * (t - self.t_start)

    @property
    def r0P0(self):
        return self.body.r0S0 + np.dot(self.body.A0K, self.rSPK)


class MovingMarkerFunction(MovingMarker):
    def __init__(self, r_start, body, functions, t_start=0, save=False, animation=None):
        super().__init__(r_start, body, 0, t_start, save, animation)
        self.functions = [
            func if func is not None else self.null_function for func in functions]
        self.rSPK0 = self.rSPK

    def update_location(self, t):
        if t >= self.t_start:
            dx = self.functions[0](t - self.t_start)
            dy = self.functions[1](t - self.t_start)
            dz = self.functions[2](t - self.t_start)
            self.rSPK = self.rSPK0 + np.array([dx, dy, dz])

    @staticmethod
    def null_function(t):
        return 0


class MovingMarkerTable(MovingMarker):
    def __init__(self, r_start, body, t_data, x_data, y_data, z_data, save=False):
        super().__init__(r_start, body, 0, 0, save=False)
        self.t_data = t_data
        self.x_data = x_data
        self.y_data = y_data
        self.z_data = z_data
        self.rSPK0 = self.rSPK

    def update_location(self, t):
        dx = np.interp(t, self.t_data, self.x_data)
        dy = np.interp(t, self.t_data, self.y_data)
        dz = np.interp(t, self.t_data, self.z_data)
        self.rSPK = self.rSPK0 + np.array([dx, dy, dz])


class PositionSaver:
    def __init__(self):
        self.x = np.array([])

    def save(self, x: np.array):
        if np.size(self.x) == 0:
            self.x = x
        else:
            self.x = np.vstack((self.x, x))


def flexible_beam(dimension: np.array, location: np.array, mass_segment: np.array, inertia_segment: np.array,
                  n_segments: int,
                  rotational_stiffness: np.array, rotational_damping: np.array,
                  ground_acceleration=np.array([0, 0, 0])):
    A, b, c = dimension
    a = A / n_segments
    da, db, dc = location
    Z = np.zeros([3, 3])
    # Location, Rotation of first segment
    y = [da, db, dc, 1, 0, 0, 0]
    # Velocity of first segment
    z = [0, 0, 0, 0, 0, 0]
    # Definition of first segment
    Head = RigidBody(mass_segment, inertia_segment, np.array(y + z))
    Head.add_acceleration(ground_acceleration)
    Beam = [Head]
    Beam_Forces = []
    Beam_Constraints = []
    # All other segments and connections
    for i in range(1, n_segments):
        y = [y[0] + a, db, dc, 1, 0, 0, 0]
        Beam.append(RigidBody(mass_segment, inertia_segment, np.array(y + z)))
        Beam[i].add_acceleration(ground_acceleration)
        # Connection Points
        P0 = Marker(np.array([a / 2, 0, 0]), Beam[i - 1])
        P1 = Marker(np.array([-a / 2, 0, 0]), Beam[i])
        # Bushing
        Beam_Forces.append(MultibodyPy.forces.Bushing(
            P1, P0, Z, Z, rotational_stiffness, rotational_damping))
        Beam_Constraints.append(MultibodyPy.constraints.Joint(P1, P0))

    return Beam, Beam_Forces, Beam_Constraints


def euler_to_quaternion(euler):
    roll, pitch, yaw = euler
    cy = np.cos(yaw * 0.5)
    sy = np.sin(yaw * 0.5)
    cp = np.cos(pitch * 0.5)
    sp = np.sin(pitch * 0.5)
    cr = np.cos(roll * 0.5)
    sr = np.sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy

    return np.array([qw, qx, qy, qz])


def moment_of_inertia(mass, dim):
    x, y, z = dim
    return 1 / 12 * mass * np.array([[y ** 2 + z ** 2, 0, 0],
                                     [0, z ** 2 + x ** 2, 0],
                                     [0, 0, x ** 2 + y ** 2]])
