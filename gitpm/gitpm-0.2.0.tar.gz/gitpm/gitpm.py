import argparse, sys, os

from .repository import Repository, Repo, R
from .view import printTable


class GitPM:
    @staticmethod
    def error(e):
        GitPM.parser.error(e)

    @staticmethod
    def singleArgError(op, arg):
        GitPM.error(
            'expected a single argument for the "' + op + '" operation: "' + arg + '"'
        )

    @staticmethod
    def parseArgs(arguments):
        GitPM.parser = argparse.ArgumentParser(
            description="Manage multiple bare git-repositories."
        )

        GitPM.parser.add_argument(
            "operation",
            default="list",
            nargs="?",
            help="The operation to be carried out.",
        )

        GitPM.parser.add_argument("args", nargs="*", help="Operation-specific data.")

        return GitPM.parser.parse_args(arguments)

    @staticmethod
    def run(directory, arguments):
        args = GitPM.parseArgs(arguments)

        if args.operation == "loop":
            print("Starting a gitPM operation loop. Type 'quit' to exit.")
            while True:
                try:
                    cmd = input(" > ")
                    if cmd in ["quit", "q", "exit"]:
                        raise KeyboardInterrupt()
                    elif cmd in ["clear", "cls"]:
                        os.system("clear")
                    elif cmd == "loop":  # no looping in loops
                        print("Can't start a loop within a loop. Type 'quit' to exit.")
                    else:
                        os.system("gitpm " + cmd)
                except KeyboardInterrupt:
                    print("\nExiting loop")
                    break
        elif args.operation == "list":
            if len(args.args) == 0:
                status = "all"
            elif args.args[0] in R.status_set:
                status = args.args[0]
            else:
                GitPM.error('unexpected usage of the "list" operation')

            tableWidths = [R.id_width + 4, 32, 16, R.hash_abbr_len]
            printTable(
                tableWidths,
                [
                    [
                        r.id,
                        r.readFile(R.file_name),
                        r.readFile(R.file_status),
                        r.readFile("refs/heads/master")[0 : R.hash_abbr_len],
                    ]
                    for r in Repo.list(directory)
                    if (status == "all" or r.readFile(R.file_status) == args.args[0])
                ],
            )

        elif args.operation == "create":
            if len(args.args) != 1:
                GitPM.singleArgError("create", "name")

            r = Repo.create(directory, args.args[0])
            print("\nNew project id: " + r.id + ".\n")

        elif R.isId(args.operation) and os.path.isdir(R.formatId(args.operation)):
            GitPM.runProjectOperation(directory, args)

        else:
            GitPM.error('unrecognized operation "' + args.operation + '"')

    @staticmethod
    def runProjectOperation(directory, args):
        r = Repository(R.formatId(int(args.operation, 16)))

        if len(args.args) == 0:
            print("Project:\t" + r.readFile(R.file_name) + " <" + r.id + ">\n")
            print("Status:\t" + r.readFile(R.file_status) + "\n")
            print("About:\t" + r.readFile(R.file_about) + "")
            print("Tags:\t" + r.readFile(R.file_tags) + "\n")
            print("Master:\t" + r.readFile("refs/heads/master") + "\n")

        elif args.args[0] == "rename":
            if len(args.args) != 2:
                GitPM.singleArgError("rename", "new-name")
            r.writeFile(R.file_name, args.args[1])

        elif args.args[0] == "status":
            if len(args.args) != 2:
                GitPM.singleArgError("status", "new-status")
            elif args.args[1] not in R.status_set:
                GitPM.error("unknown staus, expected one in " + str(R.status_set))
            r.writeFile(R.file_status, args.args[1])

        elif args.args[0] == "describe":
            if len(args.args) != 2:
                GitPM.singleArgError("describe", "project-description")
            r.writeFile(R.file_about, args.args[1])

        elif args.args[0] == "retag":
            if len(args.args) != 2:
                GitPM.singleArgError("retag", "new-tags")
            r.writeFile(R.file_tags, args.args[1])

        elif args.args[0] == "remove":
            try:
                if input("Delete repository? (y / n) ") == "y":
                    r.remove()
                    print('Deleted repository "' + r.readFile(R.file_name) + '".\n')
                else:
                    raise KeyboardInterrupt
            except KeyboardInterrupt:
                print("Canceled deletion.\n")
