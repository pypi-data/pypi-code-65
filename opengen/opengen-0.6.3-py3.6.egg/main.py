import opengen as og
import casadi as cs

build = False


if build:

    u = cs.SX.sym("u", 5)                 # decision variable (nu = 5)
    p = cs.SX.sym("p", 2)                 # parameter (np = 2)
    phi = og.functions.rosenbrock(u, p)   # cost function

    ball = og.constraints.Ball2(None, 1.5)  # ball centered at origin
    Rn = og.constraints.NoConstraints()
    rect = og.constraints.Rectangle(xmin=[-1, -2, -3], xmax=[0, 10, -1])

    # Segments: [0, 1], [2, 3, 4]
    segment_ids = [1, 4]
    bounds =  og.constraints.CartesianProduct(segment_ids, [ball, Rn])
    bounds2 = og.constraints.CartesianProduct(segment_ids, [Rn, rect])

    problem = og.builder.Problem(u, p, phi)\
              .with_constraints(bounds2)
    # problem.with_constraints(bounds)

    meta = og.config.OptimizerMeta()                \
        .with_optimizer_name("buggy_optimizer")

    build_config = og.config.BuildConfiguration()\
        .with_build_directory("my_optimizers")\
        .with_build_mode(og.config.BuildConfiguration.DEBUG_MODE)\
        .with_tcp_interface_config()

    solver_config = og.config.SolverConfiguration()   \
                .with_lbfgs_memory(15)                \
                .with_tolerance(1e-5)                 \
                .with_max_inner_iterations(155)

    builder = og.builder.OpEnOptimizerBuilder(problem,
                                              metadata=meta,
                                              build_configuration=build_config,
                                              solver_configuration=solver_config)
    builder.build()
else:

    mng = og.tcp.OptimizerTcpManager(ip='127.0.0.1', port=8333)
    # mng.start()

    pong = mng.ping()                 # check if the server is alive
    print(pong)
    response = mng.call([1.0, 50.0], initial_guess=[0, 0, 0, 0, 0])  # call the solver over TCP

    if response.is_ok():
        # Solver returned a solution
        solution_data = response.get()
        print(solution_data.solution)

    # mng.kill()