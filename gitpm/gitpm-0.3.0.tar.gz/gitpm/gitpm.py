import argparse, sys, os

from .repository import Repository, Repo, R
from .view import printTable


class GitPM:
    @staticmethod
    def error(e):
        GitPM.parser.error(e)

    @staticmethod
    def parseArgs(directory, argv):
        GitPM.parser = argparse.ArgumentParser(
            description="Manage multiple bare git-repositories.",
            epilog="More details at https://github.com/finnmglas/gitpm.",
        )

        subparsers = GitPM.parser.add_subparsers(
            dest="operation", help="GitPM operations."
        )
        subparsers.required = True

        # --- gipm create [name]
        parser_create = subparsers.add_parser("create", help="Create a new project.")
        parser_create.add_argument("name", help="The name of the new project.")

        # --- gitpm list [status]
        parser_list = subparsers.add_parser(
            "list", help="List projects in the current directory."
        )
        parser_list.add_argument(
            "status",
            default="all",
            choices=["all"] + Repository.status_set,
            nargs="?",
            help="The status of projects filtered for.",
        )

        # --- gitpm loop
        parser_loop = subparsers.add_parser("loop", help="Run the GitPM shell.")

        # --- gitpm project [id]
        parser_project = subparsers.add_parser(
            "project", help="Run a project operation, Modify projects."
        )
        parser_project.add_argument("id", help="The project id to work with.")

        parser_project_subparsers = parser_project.add_subparsers(
            dest="project_op", help="GitPM project operations."
        )
        parser_project_subparsers.required = True

        # --- --- gipm [project] details
        parser_project_details = parser_project_subparsers.add_parser(
            "details", help="View project details."
        )

        # --- --- gipm [project] rename
        parser_project_rename = parser_project_subparsers.add_parser(
            "rename", help="Rename a project."
        )
        parser_project_rename.add_argument("name", help="The project's new name.")

        # --- --- gipm [project] status
        parser_project_status = parser_project_subparsers.add_parser(
            "setstatus", help="Change a projects maintainance status."
        )
        parser_project_status.add_argument(
            "status", choices=Repository.status_set, help="The project's new status."
        )

        # --- --- gipm [project] describe
        parser_project_describe = parser_project_subparsers.add_parser(
            "describe", help="Edit a project's description."
        )
        parser_project_describe.add_argument(
            "description", help="The project's new desription."
        )

        # --- --- gipm [project] retag
        parser_project_retag = parser_project_subparsers.add_parser(
            "retag", help="Edit a project's tags."
        )
        parser_project_retag.add_argument(
            "tags", help="The project's new tags (comma-separated)."
        )

        # --- --- gipm [project] remove
        parser_project_remove = parser_project_subparsers.add_parser(
            "remove", help="Remove a project (irreversibly)."
        )

        # --- --- gipm [project] execute
        parser_project_execute = parser_project_subparsers.add_parser(
            "execute", help="Execute a git command."
        )

        # if argv[0] is project id: run a project op
        if (
            len(argv)
            and R.isId(argv[0])
            and R.formatId(argv[0]) in R.listIds(directory)
        ):
            argv = ["project"] + argv
        if len(argv) > 2 and argv[0] == "project":
            if argv[2] == "execute":
                argv = argv[:3]
            elif argv[2] in Repository.git_argument_set:
                argv = argv[:2] + ["execute"]
        return GitPM.parser.parse_args(argv)

    @staticmethod
    def run(directory, arguments):
        args = GitPM.parseArgs(directory, arguments)

        if args.operation == "loop":
            GitPM.run_loop(directory)
        elif args.operation == "list":
            printTable(
                [R.id_width + 4, 32, 16, R.hash_abbr_len],
                [
                    [
                        r.getId(),
                        r.getName(),
                        r.getStatus(),
                        r.getMasterHash()[0 : R.hash_abbr_len],
                    ]
                    for r in Repository.list(directory)
                    if (args.status == "all" or r.getStatus() == args.status)
                ],
            )
        elif args.operation == "create":
            r = Repo.create(directory, args.name)
            print("\nNew project id: " + r.getId() + ".\n")
        elif args.operation == "project":
            project = Repository(R.formatId(int(args.id, 16)))

            if args.project_op == "details":
                print("Project:\t" + project.getName() + " <" + project.getId() + ">\n")
                print("Status:\t" + project.getStatus() + "\n")
                print("About:\t" + project.getDescription() + "")
                print("Tags:\t" + project.getTags() + "\n")
                print("Master:\t" + project.getMasterHash() + "\n")
            elif args.project_op == "rename":
                project.setName(args.name)
            elif args.project_op == "setstatus":
                project.setStatus(args.status)
            elif args.project_op == "describe":
                project.setDescription(args.description)
            elif args.project_op == "retag":
                project.setTags(args.tags)
            elif args.project_op == "remove":
                try:
                    if input("Delete repository? (y / n) ") == "y":
                        project.remove()
                        print('Deleted repository "' + project.getName() + '".\n')
                    else:
                        raise KeyboardInterrupt
                except KeyboardInterrupt:
                    print("Canceled deletion.\n")
            elif args.project_op == "execute":
                if arguments[1] == "execute":
                    project.execute("git " + " ".join(arguments[2:]))
                else:
                    project.execute("git " + " ".join(arguments[1:]))
        else:
            GitPM.error('unrecognized operation "' + args.operation + '"')

    @staticmethod
    def run_loop(directory):
        currentProject = ""  # checkout [id]
        prompt = "gitpm > "

        print("Starting a gitPM operation loop. Type 'quit' to exit.")
        while True:
            try:
                cmd = input(prompt)
                cmd_argv = cmd.split(" ")
                if cmd.strip() == "":
                    pass
                elif cmd_argv[0] == "checkout":
                    if len(cmd_argv) == 1:
                        print("error: argument id: expected id after 'checkout'")
                    elif len(cmd_argv) > 2:
                        print("error: too many arguments for 'checkout'")
                    elif R.formatId(cmd_argv[1]) not in R.listIds(directory):
                        print("error: argument id: can't check out invalid id")
                    else:
                        currentProject = cmd_argv[1]
                        prompt = "gitpm: " + R.formatId(cmd_argv[1]) + " > "
                elif cmd in ["quit", "q", "exit"]:
                    if currentProject == "":
                        raise KeyboardInterrupt()
                    else:
                        currentProject = ""
                        prompt = "gitpm > "
                elif cmd in ["clear", "cls"]:
                    os.system("clear")
                elif cmd == "loop":  # no looping in loops
                    print("Can't start a loop within a loop. Type 'quit' to exit.")
                else:
                    if currentProject != "":
                        cmd = currentProject + " " + cmd
                    # execute
                    os.system("gitpm " + cmd)
            except KeyboardInterrupt:
                print("\nExiting loop")
                break
