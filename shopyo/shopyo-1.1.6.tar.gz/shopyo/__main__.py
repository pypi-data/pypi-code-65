import sys

from .shopyoapi.utils import trymkdir
from .shopyoapi.utils import trycopytree
from .shopyoapi.utils import trycopy


def new_project(path, newfoldername):
    newfoldername = newfoldername.strip('/').strip('\\')
    print("creating new project {}".format(newfoldername))

    base_path = path + "/" + newfoldername
    trymkdir(base_path)
    print("created dir {} in {}".format(newfoldername, path))

    trycopytree("./static", base_path + "/static")
    trycopytree("./tests", base_path + "/tests")
    trycopytree("./modules/base", base_path + "/modules/base")
    trycopytree("./modules/admin", base_path + "/modules/admin")
    trycopytree("./modules/login", base_path + "/modules/login")
    trycopytree("./modules/control_panel", base_path + "/modules/control_panel")
    trycopytree("./modules/settings", base_path + "/modules/settings")
    trycopytree("./shopyoapi", base_path + "/shopyoapi")

    trycopy("app.py", base_path + "/app.py")
    trycopy("config.json", base_path + "/config.json")
    trycopy("config.py", base_path + "/config.py")
    trycopy("manage.py", base_path + "/manage.py")
    trycopy("../requirements.txt", base_path + "/requirements.txt")

def main():
    args = sys.argv
    if args[1] == "new" and len(args) == 4:
        new_project(args[2], args[3])


if __name__ == "__main__":
    main()