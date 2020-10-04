from project_archer.environment.environment import BashEnvironment


def select_zone(args, env: BashEnvironment):
    select_zone_str(internal_run_mode=args.internalRunMode, zone=args.zone, env=env)


def select_zone_str(*, internal_run_mode: str, zone: str, env: BashEnvironment):
    env.set_envvar(
        "CIPLOGIC_ARCHER_CURRENT_" + internal_run_mode.upper() + "_ZONE", zone
    )
    env.flush()
