#
#     This file is part of rockit.
#
#     rockit -- Rapid Optimal Control Kit
#     Copyright (C) 2019 MECO, KU Leuven. All rights reserved.
#
#     Rockit is free software; you can redistribute it and/or
#     modify it under the terms of the GNU Lesser General Public
#     License as published by the Free Software Foundation; either
#     version 3 of the License, or (at your option) any later version.
#
#     Rockit is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#     Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public
#     License along with CasADi; if not, write to the Free Software
#     Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
#

from .multiple_shooting import MultipleShooting
from .sampling_method import SamplingMethod
from acados_template import AcadosOcp, AcadosOcpSolver, AcadosSimSolver, AcadosModel
from casadi import MX, vcat
import numpy as np
import scipy


class AcadosInterface(MultipleShooting):
    def __init__(self,N=20,**args):
        self.N = N
        self.args = args
        MultipleShooting.__init__(self, N=N)

    """def register(self, stage):
        pass"""

    """def fill_placeholders_t0(self, stage, expr, *args):
        return self.t0"""

    """def fill_placeholders_T(self, stage, expr, *args):
        return self.T"""

    """def transcribe_placeholders(self, stage, placeholders):
        Transcription is the process of going from a continuous-time OCP to an NLP
        return stage._transcribe_placeholders(self, placeholders)"""

    """def fill_placeholders_sum_control(self, stage, expr, *args):
        r = 0
        for k in range(self.N):
            r = r + self.eval_at_control(stage, expr, k)
        return r"""

    """def add_parameter(self, stage, opti):
        for p in stage.parameters['']:
            self.P.append(opti.parameter(p.shape[0], p.shape[1]))
        for p in stage.parameters['control']:
            self.P_control.append([opti.parameter(p.shape[0], p.shape[1]) for i in range(self.N)])
    """

    def transcribe(self, stage, opti):

        # We are creating variables in a special order such that the resulting constraint Jacobian
        # is block-sparse
        self.X.append(vcat([MX.sym("X", s.numel()) for s in stage.states]))

        for k in range(self.N):
            self.U.append(vcat([MX.sym("U", s.numel()) for s in stage.controls]) if stage.nu>0 else MX(0,1))
            self.X.append(vcat([MX.sym("X", s.numel()) for s in stage.states]))

        # Create time grid (might be symbolic)
        self.T = self.eval(stage, stage._T)
        self.t0 = self.eval(stage, stage._t0)

        self.set_initial(stage, opti, stage._initial)
        T_init = opti.debug.value(self.T, opti.initial())
        t0_init = opti.debug.value(self.t0, opti.initial())

        # How to get initial value -> ask opti?

        control_grid_init = self.time_grid(t0_init, T_init, self.N)
        if self.time_grid.localize_t0:
            for k in range(1, self.N):
                stage.set_initial(self.t0_local[k], control_grid_init[k])
            stage.set_initial(self.t0_local[self.N], control_grid_init[self.N])
        if self.time_grid.localize_T:
            for k in range(not isinstance(self.time_grid, FreeGrid), self.N):
                stage.set_initial(self.T_local[k], control_grid_init[k+1]-control_grid_init[k])


        self.ocp = ocp = AcadosOcp()

        model = AcadosModel()
        

        f = stage._ode()
        x = stage.x
        xdot = MX.sym("xdot", stage.nx)
        u = stage.u
        p = MX.sym("p", stage.np+stage.v.shape[0])

        res = f(x=x, u=u, p=p)
        f_expl = res["ode"]

        model.f_impl_expr = xdot-f_expl
        model.f_expl_expr = f_expl
        model.x = x
        model.xdot = xdot
        model.u = u
        model.p = p
        model.name = "rockit_model"

        ocp.model = model

        # set dimensions
        ocp.dims.N = self.N

        print(symvar(stage._objective))


        print(stage._objective)

        #print(self.eval(stage, stage._objective))

        """

        # strategy 1: symvar/subst intergal parts
        # re-use multiple shooting

        # set cost module
        ocp.cost.cost_type = 'LINEAR_LS'
        ocp.cost.cost_type_e = 'LINEAR_LS'

        Q = 2*np.diag([1e3, 1e3, 1e-2, 1e-2])
        R = 2*np.diag([1e-2])

        ocp.cost.W = scipy.linalg.block_diag(Q, R)

        ocp.cost.W_e = Q

        ocp.cost.Vx = np.zeros((ny, nx))
        ocp.cost.Vx[:nx,:nx] = np.eye(nx)

        Vu = np.zeros((ny, nu))
        Vu[4,0] = 1.0
        ocp.cost.Vu = Vu

        ocp.cost.Vx_e = np.eye(nx)

        ocp.cost.yref  = np.zeros((ny, ))
        ocp.cost.yref_e = np.zeros((ny_e, ))

        # set constraints
        Fmax = 80
        x0 = np.array([0.0, np.pi, 0.0, 0.0])
        ocp.constraints.constr_type = 'BGH'
        ocp.constraints.lbu = np.array([-Fmax])
        ocp.constraints.ubu = np.array([+Fmax])
        ocp.constraints.x0 = x0
        ocp.constraints.idxbu = np.array([0])

        for k, v in self.args:
            setattr(ocp.solver_options, k, v)

        ocp.solver_options.qp_solver_cond_N = self.N

        ocp.solver_options.tf = stage.T

        acados_ocp_solver = AcadosOcpSolver(ocp, json_file = 'acados_ocp_' + model.name + '.json')
        acados_integrator = AcadosSimSolver(ocp, json_file = 'acados_ocp_' + model.name + '.json')

        """
