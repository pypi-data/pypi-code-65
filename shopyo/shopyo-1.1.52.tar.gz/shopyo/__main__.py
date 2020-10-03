import sys

from shopyoapi.cmd import new_project

def main():
    args = sys.argv
    if args[1] == "new" and len(args) == 4:
        new_project(args[2], args[3])


if __name__ == "__main__":
    main()