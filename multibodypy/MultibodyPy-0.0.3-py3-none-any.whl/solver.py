import numpy as np


class ImplicitEuler:
    def __init__(self, func, t0, y0, tend, step_size, first_step=1e-6, min_step=1e-12, max_step=1e-1, jacobian_recompute=1, jacobian_recompute_max=1, jacobian_recompute_min=1, tol=1e-6, args=()):
        self.func = func
        self.t0 = t0
        self.y0 = y0
        self.tend = tend
        self.step_size = step_size
        self.dt = step_size
        self.first_step = first_step
        self.min_step = min_step
        self.max_step = max_step

        self.args = args
        self.t = t0
        self.y = y0

        self.f = 0
        self.jac = self.jacobian(self.y)
        self.jacobian_recompute = jacobian_recompute
        self.jacobian_recompute_max = jacobian_recompute_max
        self.jacobian_recompute_min = jacobian_recompute_min

        self.jacobi_count = 0
        self.tol = tol

    def step(self):
        # print(self.jacobi_count, self.jacobian_recompute)
        if self.jacobi_count >= self.jacobian_recompute:
            self.jac = self.jacobian(self.y)
            self.jacobi_count = 0
        else:
            self.jacobi_count += 1

        ykp1, err = self.simplfied_newton()
        self.t += self.dt
        self.y = ykp1

        # Error
        self.dt, self.jacobian_recompute = self.change_step_size(err)
        # ykp1 = scipy.optimize.newton(self.optimize_func, self.y,
        #                              maxiter=200,
        #                              tol=1e-3)

    def optimize_func(self, ykp1):
        dtp1 = self.t + self.dt
        return self.y + self.dt * self.func(dtp1, ykp1) - ykp1

    def simplfied_newton(self):
        A = np.identity(len(self.jac)) - self.dt * self.jac

        if self.args == ():
            f0 = self.func(self.t, self.y)
            f1 = self.func(self.t + self.dt, self.y)
        else:
            f0 = self.func(self.t, self.y, self.args)
            f1 = self.func(self.t + self.dt, self.y, self.args)

        dfdt = (f1 - f0) * (1. / self.dt)
        b = self.dt * f0 + self.dt * self.dt * dfdt
        dy = np.linalg.solve(A, b)
        y = self.y + dy

        return y, 0

    def jacobian(self, x0):
        t = self.t
        epsilon = 1e-8
        func = self.func
        if self.args == ():
            f0 = func(t, x0)
        else:
            f0 = func(t, x0, self.args)
        f0 = np.array(f0)
        jac = np.zeros([len(x0), len(f0)])
        dx = np.zeros(len(x0))
        for i in range(len(x0)):
            dx[i] = epsilon
            if self.args == ():
                f1 = func(t, x0 + dx)
            else:
                f1 = func(t, x0 + dx, self.args)
            jac[i] = (np.array(f1) - f0) / (epsilon)
            dx[i] = 0.0
        return jac.transpose()

    def change_step_size(self, err):
        if err < self.tol:
            dt = self.dt*1.1
            jr = self.jacobian_recompute + 1
        else:
            dt = self.dt*0.9
            jr = self.jacobian_recompute - 100

        if dt < self.min_step:
            dt = self.min_step
        elif dt > self.max_step:
            dt = self.max_step
        else:
            dt = dt

        if jr < self.jacobian_recompute_min:
            jr = self.jacobian_recompute_min
        elif jr > self.jacobian_recompute_max:
            jr = self.jacobian_recompute_max
        else:
            jr = jr

        return dt, jr


class Trapz(ImplicitEuler):
    def __init__(self, func, t0, y0, tend, step_size, first_step=1e-6, min_step=1e-12, max_step=1e-1, jacobian_recompute=1, jacobian_recompute_max=1, jacobian_recompute_min=1, tol=1e-6, args=()):
        ImplicitEuler.__init__(self, func, t0, y0,
                               tend, step_size, first_step, min_step, max_step, jacobian_recompute, jacobian_recompute_max, jacobian_recompute_min, tol, args)

    def simplfied_newton(self):
        if self.args == ():
            f0 = self.func(self.t, self.y)
        else:
            f0 = self.func(self.t, self.y, self.args)
        f0 = np.array(f0)
        A = 2 * np.identity(len(self.jac)) / self.dt - self.jac
        b = 2 * f0
        dy = np.linalg.solve(A, b)

        y = self.y + dy

        y_low = self.y + self.dt * f0
        err = np.linalg.norm(np.abs(y - y_low))

        return y, err
