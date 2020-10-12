import os, string


class Repository:

    id_width = 4
    hash_abbr_len = 8

    file_name = "description"
    file_about = "social-description"
    file_status = "maintainance"
    file_tags = "social-tags"

    status_set = ["new", "maintained", "discontinued", "completed"]
    git_argument_set = [
        "branch",
        "tag",
        "commit",
        "status",
        "remote",
        "ls-tree",
        "ls-files",
        "show",
        "config",
        "checkout",
        "add",
        "clone",
        "fetch",
        "merge",
        "pull",
        "push",
        "reset",
        "rev-list",
    ]

    @staticmethod
    def list(directory):
        dirList = os.listdir(directory)

        folderList = [
            d for d in dirList if (os.path.isdir(d) and d != ".git" and R.isId(d))
        ]
        folderList.sort(key=lambda s: int(s, 16), reverse=True)

        return [Repository(id) for id in folderList]

    @staticmethod
    def listIds(directory):
        return [repo.getId() for repo in Repository.list(directory)]

    @staticmethod
    def isId(hexId):
        return all(c in set(string.hexdigits) for c in hexId)

    @staticmethod
    def formatId(id):
        if isinstance(id, str):
            id = int(id, 16)

        formatedId = hex(id)[2:]

        while Repository.id_width > len(formatedId):
            formatedId = "0" + formatedId

        return formatedId

    @staticmethod
    def create(directory, name=""):
        repositories = Repository.list(directory)

        if len(repositories) == 0:
            newId = Repository.formatId(0)
        else:
            newId = int(repositories[0].getId(), 16) + 1
            newId = Repository.formatId(newId)

        os.mkdir(newId)
        r = Repository(newId)
        r.execute("git init --bare")
        r.writeFile(R.file_name, name)
        r.writeFile(R.file_status, "new")

        return r

    def __init__(self, id):
        self.id = id

    def execute(self, command):
        os.system("cd " + self.getId() + " && " + command)

    # -- Files

    def readFile(self, f):
        try:
            with open(self.getId() + "/" + f) as descriptor:
                content = descriptor.read()
        except IOError:
            content = ""

        return content.strip()

    def writeFile(self, f, data):
        with open(self.getId() + "/" + f, "w") as descriptor:
            descriptor.write(data)

    def remove(self):
        self.execute("cd .. && rm -r " + self.getId())

    # Getters and Setters
    # --- Metadata

    def getId(self):
        return self.id

    def setName(self, name):
        self.writeFile(R.file_name, name)

    def getName(self):
        return self.readFile(R.file_name)

    def setStatus(self, status):
        self.writeFile(R.file_status, status)

    def getStatus(self):
        return self.readFile(R.file_status)

    def setDescription(self, description):
        self.writeFile(R.file_about, description)

    def getDescription(self):
        return self.readFile(R.file_about)

    def setTags(self, tags):
        self.writeFile(R.file_tags, tags)

    def getTags(self):
        return self.readFile(R.file_tags)

    # --- Git - related

    def getMasterHash(self):
        return self.readFile("refs/heads/master")


R = Repo = Repository  # synonymous classes
