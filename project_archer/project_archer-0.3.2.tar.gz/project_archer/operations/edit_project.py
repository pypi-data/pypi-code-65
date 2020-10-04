import os

from project_archer.environment.read_shell_parameters import (
    project_folder,
    current_project,
)


def edit_project(args, env):
    folder = project_folder(args)

    # if there is an argument on the shell, use that,
    # otherwise use "current project"
    if args.project:
        target_project = args.project
    else:
        target_project = current_project(args.internalRunMode)
        if not target_project:
            target_project = "undefined"

    # if the target_project is in a zone, it's prefixed by the zone name.
    # if that's the case, we need to drop the zone information.
    env.execute(
        "$EDITOR " + os.path.join(folder, os.path.basename(target_project + ".yml"))
    )
