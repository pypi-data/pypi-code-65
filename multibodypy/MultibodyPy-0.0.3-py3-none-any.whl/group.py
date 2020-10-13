import numpy as np
import sys
from MultibodyPy import bodies, forces, constraints
from typing import List
from scipy import sparse
from functools import partialmethod
from scipy import optimize
import csv
import pickle


class Group:
    def __init__(self, body, force, constraint, moving_marker=[], animated_ground=[],
                 data_filename='data.csv', save_acceleration=False, animation_filename='animation.bin'):
        self.bodies: List[bodies.RigidBody] = body
        self.n = len(self.bodies)
        self.forces: List[forces] = force
        self.constraints: List[constraints] = constraint
        self.moving_marker = moving_marker
        self.animated_ground = animated_ground

        self.numDof = self.set_num_dof
        self.dim_y = self.dimension_y()
        self.dim_z = self.dimension_z()

        self.qglobal = self.initialize_qglobal
        self.q0global = self.qglobal

        self.solve = self.assemble_mass
        self.qe = self.assemble_force()

        self.qd = np.zeros(self.numDof)
        self.g1 = []

        self.save_acceleration = save_acceleration
        header = self.get_header()
        self.data_saver = DataSaver(data_filename, header)

        self.animation_saver = AnimationSaver(animation_filename)

    def qdot(self, t, qglobal):
        # Update locations of moving marker if not empty
        if self.moving_marker:
            self.update_moving_marker(t)

        # Update state of bodies
        self.update_body_states(qglobal)

        # get global y and z
        y_global, z_global = self.get_position_velocity

        # Apply forces to bodies
        self.update_body_forces()

        # get global forces
        self.qe = self.forces_global

        # get global global jacobian and Lagrange-Multiplicators
        c_global = 0
        if len(self.constraints) > 0:
            Jg, la, mue = self.jacobi_lagrange_multiplicators(z_global)
            c_global = np.dot(Jg.transpose(), la)
            self.c_global = c_global

            # Update Gear-Gupta-Leimkuhler-corrected velocities
            z_global = z_global + np.dot(Jg.transpose(), mue)
            self.update_body_velocities(np.concatenate((y_global, z_global)))

            # Add constraint dampings
            for con in self.constraints:
                if isinstance(con, (constraints.Joint, constraints.Hinge, constraints.PrismaticHinge)):
                    self.add_constraint_damping(con)
            self.qe = self.forces_global

            # Update all constraint forces
            self.qe = self.qe + c_global

        # get kinematic ode
        yp_global = self.kinematic_ode_global

        # dynamic ode
        zp_global = sparse.linalg.spsolve(self.solve, self.qe)

        # state change
        qp_global = np.concatenate((yp_global, zp_global))

        if self.save_acceleration:
            for body in self.bodies:
                body.update_acceleration(qp_global)

        return qp_global

    def update_body_forces(self):
        for f in self.forces:
            F1, M1, F2, M2 = f.get_force()
            f.body1.add_external_force_moment(F1, M1)
            f.body2.add_external_force_moment(F2, M2)

    def update_moving_marker(self, t):
        for mm in self.moving_marker:
            mm.update_location(t)

    def dimension_y(self):
        dim = 0
        for body in self.bodies:
            if type(body) is bodies.RigidBody:
                dim += 7
            elif type(body) is bodies.RigidBody1D:
                dim += 1
        return dim

    def dimension_z(self):
        dim = 0
        for body in self.bodies:
            if type(body) is bodies.RigidBody:
                dim += 6
            elif type(body) is bodies.RigidBody1D:
                dim += 1
        return dim
    #
    # def save_forces_positions(self):
    #     for f in self.forces:
    #         if f.save is True:
    #             f.force_saver.save(f.F1)
    #     for mm in self.moving_marker:
    #         if mm.save is True or mm.animation is not None:
    #             mm.position_saver.save(mm.rSPK)

    def save_data(self, t, dt):
        data = {}
        data['Time'] = t
        data['Step'] = dt
        for f in self.forces:
            if f.save is True:
                data[f.name + '_x'] = f.F1[0]
                data[f.name + '_y'] = f.F1[1]
                data[f.name + '_z'] = f.F1[2]
                data[f.name + '_mx'] = f.M1[0]
                data[f.name + '_my'] = f.M1[1]
                data[f.name + '_mz'] = f.M1[2]
        for b in self.bodies:
            if type(b) is bodies.RigidBody:
                data[b.name + '_x'] = b.r0S0[0]
                data[b.name + '_y'] = b.r0S0[1]
                data[b.name + '_z'] = b.r0S0[2]
                data[b.name + '_vx'] = b.v0S0[0]
                data[b.name + '_vy'] = b.v0S0[1]
                data[b.name + '_vz'] = b.v0S0[2]
                if self.save_acceleration:
                    data[b.name + '_ax'] = b.a0S0[0]
                    data[b.name + '_ay'] = b.a0S0[1]
                    data[b.name + '_az'] = b.a0S0[2]
            elif type(b) is bodies.RigidBody1D:
                data[b.name + '_r'] = b.r
                data[b.name + '_v'] = b.v

        self.data_saver.save(data)

    def save_animation(self, t, q):
        self.animation_saver.save(
            t, q, self.bodies, self.moving_marker, self.dim_y)

    def save_constraints(self):
        for c in self.constraints:
            if c.save is True:
                c.constraint_equations.append(c.g())

    @staticmethod
    def add_constraint_damping(con):
        dom = np.dot(con.body1.A0K, con.body1.om0KK) - \
            np.dot(con.body2.A0K, con.body2.om0KK)
        M = con.damp * dom
        con.body1.add_external_force_moment(np.zeros(3), -M)
        con.body2.add_external_force_moment(np.zeros(3), M)

        if isinstance(con, constraints.PrismaticHinge):
            dv = con.body1.v0S0 - con.body2.v0S0
            F = con.damp_translational * dv
            con.body1.add_external_force_moment(-F, np.zeros(3))
            con.body2.add_external_force_moment(F, np.zeros(3))

    def update_body_states(self, qglobal):
        for body in self.bodies:
            body.update_state(qglobal)
            body.reset_external_force_moment()

    def update_body_velocities(self, qglobal):
        for body in self.bodies:
            body.update_velocities(qglobal)

    @property
    def initialize_qglobal(self):
        y = []
        z = []
        py = 0
        pz = 0
        p = 0
        for body in self.bodies:
            yb, zb = np.array_split(body.q0, 2)
            y = y + yb.tolist()
            z = z + zb.tolist()
            body.posy = py
            body.posz = pz
            body.pos = p
            p = p + 1
            if type(body) is bodies.RigidBody1D:
                py += 1
                pz += 1
            elif type(body) is bodies.RigidBody:
                py += 7
                pz += 6

        q0 = np.array(y + z)
        for body in self.bodies:
            body.posz = body.posz + len(y)
        return q0

    @property
    def set_num_dof(self):
        numDof = 0
        for body in self.bodies:
            numDof = numDof + body.dof
        return numDof

    @property
    def assemble_mass(self):
        m = np.zeros([self.dim_z, self.dim_z])
        a1 = 0
        for body in self.bodies:
            if type(body) is bodies.RigidBody:
                e1 = a1 + 6
            elif type(body) is bodies.RigidBody1D:
                e1 = a1 + 1

            m[a1:e1, a1:e1] = body.M

            a1 = e1
        msp = sparse.csc_matrix(m)
        mlu = sparse.linalg.factorized(msp)
        return msp

    def assemble_force(self):
        return np.zeros(self.dim_z)

    @property
    def kinematic_ode_global(self):
        a2 = 0
        yp = np.zeros(self.dim_y)
        for body in self.bodies:
            if type(body) is bodies.RigidBody:
                e2 = a2 + 7
            elif type(body) is bodies.RigidBody1D:
                e2 = a2 + 1
            # collect kinematic equations
            yp[a2:e2] = body.kinematic_ode()
            a2 = e2
        return yp

    @property
    def forces_global(self):
        b = np.zeros(self.dim_z)
        a1 = 0
        for body in self.bodies:
            if type(body) is bodies.RigidBody:
                e1 = a1 + 6
            elif type(body) is bodies.RigidBody1D:
                e1 = a1 + 1
            # collect kinematic equations
            b[a1:e1] = body.force_moment()
            a1 = e1
        return b

    def jacobi_lagrange_multiplicators(self, z):
        num_c = len(self.constraints)
        dof_c = 0
        for con in self.constraints:
            dof_c = dof_c + con.dof

        Jg = np.zeros([dof_c, self.dim_z])
        Jgpz = np.zeros(dof_c)
        g = np.zeros(dof_c)
        j = 0

        # Fill global Jacobian and derivation
        for con in self.constraints:
            G1, G2 = con.jacobian()
            if not isinstance(con.body1, bodies.Ground):
                pos1 = int(con.body1.pos * 6)
                Jg[j:j + con.dof, pos1:pos1 + 6] = G1

            if not isinstance(con.body2, bodies.Ground):
                pos2 = int(con.body2.pos * 6)
                Jg[j:j + con.dof, pos2:pos2 + 6] = G2

            # g[j:j + con.dof] = con.g()

            Jgpz[j:j + con.dof] = con.djacobian_z()

            j = j + con.dof
            con.g()

        T1 = sparse.csc_matrix(
            np.dot(Jg, sparse.linalg.spsolve(self.solve, Jg.transpose())))
        T2 = -Jgpz + np.dot(Jg, sparse.linalg.spsolve(self.solve, self.qe))
        la = -sparse.linalg.spsolve(T1, T2)
        mue = -sparse.linalg.spsolve(sparse.csc_matrix(
            np.dot(Jg, Jg.transpose())), np.dot(Jg, z))
        return Jg, la, mue

    @property
    def get_position_velocity(self):
        y = np.zeros(self.dim_y)
        z = np.zeros(self.dim_z)
        a1 = 0
        a2 = 0
        for body in self.bodies:
            if type(body) is bodies.RigidBody:
                e1 = a1 + 7
                e2 = a2 + 6
            elif type(body) is bodies.RigidBody1D:
                e1 = a1 + 1
                e2 = a2 + 1
            y[a1:e1] = body.y
            z[a2:e2] = body.z
            a1 = e1
            a2 = e2
        return y, z

    def equilibrium(self):
        # Gleichgewichtslage
        qG = optimize.fsolve(self.qdot_time_fixed, self.qglobal)
        return qG

    def jacobian(self, x, epsilon):
        func = self.qdot_time_fixed
        x0 = np.asfarray(x)
        f0 = func(x0)
        jac = np.zeros([len(x0), len(f0)])
        dx = np.zeros(len(x0))
        for i in range(len(x0)):
            dx[i] = epsilon
            jac[i] = (func(x0 + dx) - func(x0 - dx)) / (2 * epsilon)
            dx[i] = 0.0
        return jac.transpose()

    def jacobian2(self, x, dx=10 ^ -8):
        f = self.qdot_time_fixed
        n = len(x)
        func = f(x)
        jac = np.zeros((n, n))
        for j in range(n):  # through columns to allow for vector addition
            Dxj = (abs(x[j]) * dx if x[j] != 0 else dx)
            x_plus = [(xi if k != j else xi + Dxj) for k, xi in enumerate(x)]
            jac[:, j] = (f(x_plus) - func) / Dxj
        return jac

    qdot_time_fixed = partialmethod(qdot, 0)

    def get_header(self):
        header = ['Time', 'Step']
        for b in self.bodies:
            header += b.header(self.save_acceleration)
        for f in self.forces:
            if f.save is True:
                header.append(f.name + '_x')
                header.append(f.name + '_y')
                header.append(f.name + '_z')
                header.append(f.name + '_mx')
                header.append(f.name + '_my')
                header.append(f.name + '_mz')
        return header


class DataSaver:
    def __init__(self, filename, header):
        self.filename = filename
        self.header = header

        with open(self.filename, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.header)
            writer.writeheader()

    def save(self, data):
        with open(self.filename, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.header)
            writer.writerow(data)


class AnimationSaver:
    def __init__(self, filename):
        self.filename = filename

    def save(self, t, q, b, mm, dim_y):
        ta = np.array(t)
        qa = np.array(q)
        Y = qa[:, 0:int(dim_y)]

        for m in mm:
            if m.animation is not None:
                m.animation.position_saver.save(m.r0P0)

        with open(self.filename, 'wb') as file:
            pickle.dump(ta, file)
            pickle.dump(Y, file)
            pickle.dump(b, file)
            pickle.dump([m.animation for m in mm], file)

        # class Group_DAE(Group, DASSL):
        #     def __init__(self, body, force, constraint, moving_marker=[]):
        #         super().__init__(body, force, constraint, moving_marker)
        #         self.q0 = self.initialize_q()
        #         self.dqdt0 = np.zeros(len(self.q0))
        #
        #     def qdot(self, t, qglobal):
        #         pass
        #
        #     def residual(self, t, q, dqdt):
        #         qglobal = q[0:self.numDof]
        #         # Update locations of moving marker if not empty
        #         if self.moving_marker:
        #             self.update_moving_marker(t)
        #
        #         # Update state of bodies
        #         self.update_body_states(qglobal)
        #
        #         # get global y and z
        #         y_global, z_global = self.get_position_velocity
        #
        #         # Apply forces to bodies
        #         self.update_body_forces()
        #
        #         # get global forces
        #         self.qe = self.forces_global
        #
        #         # Add constraint dampings
        #         for con in self.constraints:
        #             if isinstance(con, (constraints.Joint, constraints.Hinge, constraints.PrismaticHinge)):
        #                 self.add_constraint_damping(con)
        #         self.qe = self.forces_global
        #
        #         # get global global jacobian and Lagrange-Multiplicators
        #         Jg, Jgpz, la, mue = self.jacobi_lagrange_multiplicators(z_global)
        #
        #         # Update Gear-Gupta-Leimkuhler-corrected velocities
        #         z_global = z_global + np.dot(Jg.transpose(), mue)
        #         self.update_body_velocities(np.concatenate((y_global, z_global)))
        #
        #         # derivatives
        #         ny = int(self.numDof / 13 * 7)
        #         nz = int(self.numDof / 13 * 6)
        #
        #         yp = dqdt[0:ny]
        #         zp = dqdt[ny:ny + nz]
        #         gp = dqdt[ny + nz:]
        #
        #         # DAE in general Form
        #         # kinematic ode
        #         delta_yp = self.kinematic_ode_global - yp
        #
        #         # dynamic ode
        #         MassM = np.array(self.solve.todense())
        #         delta_zp = self.qe - np.dot(MassM, zp) + np.dot(Jg.transpose(), la)
        #
        #         # constraint equation
        #         delta_gp = np.dot(Jg, z_global) - gp
        #
        #         delta = np.concatenate((delta_yp, delta_zp, delta_gp))
        #         return delta, 0
        #
        #     def jacobi_lagrange_multiplicators(self, z):
        #         num_c = len(self.constraints)
        #         dof_c = 0
        #         for con in self.constraints:
        #             dof_c = dof_c + con.dof
        #
        #         Jg = np.zeros([dof_c, 6 * len(self.bodies)])
        #         Jgpz = np.zeros(dof_c)
        #         g = np.zeros(dof_c)
        #         j = 0
        #
        #         # Fill global Jacobian and derivation
        #         for con in self.constraints:
        #             G1, G2 = con.jacobian()
        #             if not isinstance(con.body1, bodies.Ground):
        #                 pos1 = int(con.body1.pos * 6)
        #                 Jg[j:j + con.dof, pos1:pos1 + 6] = G1
        #
        #             if not isinstance(con.body2, bodies.Ground):
        #                 pos2 = int(con.body2.pos * 6)
        #                 Jg[j:j + con.dof, pos2:pos2 + 6] = G2
        #
        #             Jgpz[j:j + con.dof] = con.djacobian_z()
        #             j = j + con.dof
        #
        #         # Calculate Lagrange Multiplicator
        #         T1 = sparse.csc_matrix(
        #             np.dot(Jg, sparse.linalg.spsolve(self.solve, Jg.transpose())))
        #         T2 = -Jgpz + np.dot(Jg, sparse.linalg.spsolve(self.solve, self.qe))
        #         la = -sparse.linalg.spsolve(T1, T2)
        #         mue = - \
        #             sparse.linalg.spsolve(sparse.csc_matrix(
        #                 np.dot(Jg, Jg.transpose())), np.dot(Jg, z))
        #         return Jg, Jgpz, la, mue
        #
        #     def initialize_q(self):
        #         qglobal = self.qglobal
        #         q0g = np.array([])
        #         for c in self.constraints:
        #             q0g = np.concatenate((q0g, np.zeros(c.dof)))
        #         return np.concatenate((qglobal, q0g))
