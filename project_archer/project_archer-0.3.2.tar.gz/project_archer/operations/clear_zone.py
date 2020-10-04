from project_archer.environment.environment import BashEnvironment


def clear_zone(args, env: BashEnvironment):
    env.unset_envvar(
        "CIPLOGIC_ARCHER_CURRENT_" + args.internalRunMode.upper() + "_ZONE"
    )
    env.flush()
