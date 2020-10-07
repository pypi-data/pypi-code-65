#!/usr/bin/env python


from __future__ import print_function
from builtins import input
import datetime
import os
import re
import subprocess
import sys
from distutils.version import LooseVersion
from shutil import rmtree

from git import InvalidGitRepositoryError, Repo

PROD_PYPI_INDEX = u"https://pypi.org/simple/"
TEST_PYPI_INDEX = u"https://test.pypi.org/simple/"


def green(rhs):
    return "\033[92m{}\033[0m".format(rhs)


def red(rhs):
    return "\033[91m{}\033[0m".format(rhs)


def main():

    repo = get_repo()

    which_pypi = get_pypi()

    version_file = get_version_file(repo)
    print(version_file)
    changelog = get_changelog(repo)

    __version__ = resolve_version(repo, version_file, which_pypi)

    resolve_changelog(repo, __version__, changelog)

    check_clean(repo)

    tag = create_tag(repo, __version__)

    push_branch_and_tag(repo, tag)

    publish(repo, which_pypi, __version__)


def get_repo():
    try:
        repo = Repo(".")
    except InvalidGitRepositoryError:
        sys.stderr.write("Not a git repo.\n")
        sys.exit(1)
    if repo.untracked_files:
        sys.stderr.write("Untracked files.\n")
        sys.exit(1)
    if repo.is_dirty():
        sys.stderr.write("Dirty repo.\n")
        sys.exit(1)
    return repo


def get_pypi():
    print("Choose a PyPi repo ...")
    options = ["Don't publish", "Test PyPi", "Prod PyPi"]
    for i, opt in enumerate(options):
        print("{}:{}".format(i, opt))

    inp = int(input(green("Enter a number: ")))
    if inp in [0, 1, 2]:
        print("You chose: {}".format(options[inp]))
        return inp
    else:
        sys.stderr.write(
            "Bad input: {}\n".format(inp))
        sys.exit(1)


def get_version_file(repo):
    version_file = os.path.join(repo.working_dir, "VERSION")
    if not os.path.isfile(version_file):
        sys.stderr.write(
            "VERSION file does not exist in top level of repo.\n")
        sys.exit(1)
    return version_file


def get_pip_name(repo):

    manifest_file = os.path.join(repo.working_dir, "MANIFEST.in")
    if os.path.isfile(manifest_file):
        with open(manifest_file) as f:
            first_line = f.readline().strip().split(" ")
            if len(first_line) == 2 and first_line[0] == "#":
                return first_line[1]

    return os.path.basename(repo.working_dir)


def get_changelog(repo):
    changelog = os.path.join(
        repo.working_dir, "CHANGELOG.md")
    if not os.path.isfile(changelog):
        sys.stderr.write(
            "Skipping - CHANGELOG does not exist: {}\n".format(changelog))
        sys.exit(1)
    return changelog


def resolve_version(repo, version_file, which_pypi):

    with open(version_file) as vf:
        __version__ = vf.read().strip()

    git_tags = [str(tag) for tag in numeric_tags(repo.tags)]
    if git_tags:
        print("Git tags: ", git_tags)
    else:
        print("No Git tags exist.")

    name = get_pip_name(repo)

    pypi_versions = get_pypi_versions(name, which_pypi)
    print("PyPi versions:", pypi_versions)

    print("__version__ is:", __version__)
    version_ok = False
    change_version = False
    while not version_ok:
        version_problems = get_version_problems(
            __version__, pypi_versions, git_tags)
        if version_problems:
            print(version_problems)
            __version__ = input(green("Enter a valid version: "))
            change_version = True
        else:
            print("No version problems. ")
            version_ok = True

    print("YAY! __version__ {} is valid".format(__version__))

    if change_version:
        print("Overwriting version file...")
        with open(version_file, "w") as f:
            f.write(__version__)

        if repo.is_dirty():
            repo.index.add([version_file])
            repo.index.commit("Bump version file to {}".format(__version__))
            print("Committed version bump...")
    return __version__


def resolve_changelog(repo, __version__, changelog):
    print("resolve changelog here:")

    print("Edit the changelog now. Here are some recent commits...")

    most_recent_messages = []

    git_tags = list(reversed(numeric_tags(repo.tags)[-3:]))
    numtags = len(git_tags)
    print("num tags:", numtags)
    # git_tags = git_tags[-3:]

    tagid = 0
    currtag = git_tags[tagid] if numtags else None

    print("=" * 30)
    if not currtag:
        for commit in repo.iter_commits(repo.head):
            msg = commit.message.encode('utf-8').strip()
            # print("msg", msg)
            print("{} {}".format(commit.hexsha[:7], msg))
            most_recent_messages.append(
                "* {}. [{}]".format(msg.capitalize(),  commit.hexsha[:7]))

    else:  # tags exist
        counter = 0
        on_first_tag = True
        for commit in repo.iter_commits(repo.head):
            if currtag and commit.hexsha == currtag.commit.hexsha:
                print("TAG {} {}".format(currtag.commit.hexsha[:7], currtag))
                tagid += 1
                currtag = git_tags[tagid] if tagid < numtags else None

            if tagid == numtags:  # currtag is last tag
                counter += 1

            msg = commit.message.encode('utf-8').strip()
            print("{} {}".format(commit.hexsha[:7], msg))

            if on_first_tag:  # sti8ll looking for tagid 0
                most_recent_messages.append(
                    "* {}. [{}]".format(msg.capitalize(),  commit.hexsha[:7]))
                if tagid > 0:
                    on_first_tag = False
            elif counter >= 20:
                break

    print ("=" * 30)

    today = datetime.date.today().strftime("%d %b %Y")
    recent_block = "### Version:{} -- {}\n\n".format(__version__, today)
    recent_block += "\n".join(most_recent_messages) or ""

    with open(changelog, 'r') as clog:
        data = clog.read() or "--"

    new_content = recent_block + "\n\n" + data

    with open(changelog, 'w') as clog:
        clog.write(new_content)

    print("A new section has been prepended to your changelog.")

    input(
        green("Please edit and save your CHANGELOG, then press enter to continue."))
    if repo.is_dirty():
        repo.index.add([changelog])
        repo.index.commit("update changelog")
        print("Commit updated misc files")


def check_clean(repo):
    options = ["Fix manually and continue",
               "Auto commit and continue", "Abort"]
    while repo.is_dirty():
        print("Repo is dirty. Maybe you changed something else along the way?")
        for i, opt in enumerate(options):
            print("{}:{}".format(i, opt))

        inp = int(input(green("Enter a number: ")))

        if inp == 1:
            repo.index.add(["*"])
            repo.index.commit(
                "Staged and committed various files to ensure clean repo")
            print("Commit misc files")
        elif inp == 2:
            sys.stderr.write("Aborted:\n")
            sys.exit(1)


def create_tag(repo, __version__):
    options = ["No", "Yes",  "Abort"]
    inp = -1
    while inp not in [0, 1, 2]:
        print("Do you want to add the tag and continue?")
        for i, opt in enumerate(options):
            print("{}:{}".format(i, opt))

        inp = int(input(green("Enter a number: ")))
        if inp == 2:
            sys.stderr.write("Aborted:\n")
            sys.exit(1)
        if inp == 1:
            tag = repo.create_tag(
                __version__, message="Tagged at version {} in release release script.".format(__version__))
            print("Created tag for version {}".format(__version__))
            return tag

    print("You chose not to make a tag!")


def push_branch_and_tag(repo, tag):
    options = ["No", "Yes",  "Abort"]
    inp = -1
    while inp not in [0, 1, 2]:
        print("Do you want to push the branch and tag?")
        for i, opt in enumerate(options):
            print("{}:{}".format(i, opt))
        inp = int(input(green("Enter a number: ")))

        if inp == 0:
            print("Skipped push...")
            return
        if inp == 2:
            sys.stderr.write("Aborted:\n")
            sys.exit(1)

    repo.remotes.origin.push(repo.head.ref)
    if tag:
        repo.remotes.origin.push(tag)
        print("Pushed branch:{} and tag: {}".format(repo.head.ref, tag))
        return
    print("Pushed branch:{} but no tag.".format(repo.head.ref))


def publish(repo, which_pypi, __version__):
    if not which_pypi:
        print("Skipped publish due to earlier choice.")
        return
    pypi_repo = [None, "Test PyPi", "Prod PyPi"][which_pypi]

    options = ["No", "Yes",  "Abort"]
    inp = -1
    while inp not in [0, 1, 2]:
        print("Do you still want to publish to the {} repo?: ".format(pypi_repo))
        for i, opt in enumerate(options):
            print("{}:{}".format(i, opt))
        inp = int(input(green("Enter a number: ")))

        if inp == 0:
            print("Skipped publish...")
            return
        if inp == 2:
            sys.stderr.write("Aborted:\n")
            sys.exit(1)

    try:
        print("Removing previous builds...")
        rmtree(os.path.join(repo.working_dir, "dist"))
    except OSError:
        pass

    print("Building Source and Wheel distribution...")
    os.system("{0} setup.py clean --all".format(sys.executable))
    os.system("{0} setup.py sdist bdist_wheel".format(sys.executable))

    print("Uploading distributions...")
    if which_pypi == 1:
        os.system("twine upload -r testpypi dist/*")
    else:
        os.system("twine upload  dist/*")
    print("Finished uploading to PyPi...")


def get_pypi_versions(name, which_pypi):
    if not which_pypi:
        return []

    result = []
    args = [
        'pip',
        'install',
        '--index-url',
        [None, TEST_PYPI_INDEX, PROD_PYPI_INDEX][which_pypi],
        "{}==".format(name)
    ]

    # print " ".join(args)
    output = subprocess.Popen(
        args, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()

    try:
        output = output[1]
    except IndexError:
        print("Can't determine existing package versions.")
        sys.exit(1)

    regex = re.compile(
        r'^.*Could not find a version.*from versions:(.*)\).*', re.DOTALL)
    match = regex.match(output.decode('utf-8'))
    if match:
        result = [v.strip() for v in match.group(1).split(r', ')]
        result = [v for v in result if v and v[0].isdigit()]
    return result


def get_version_problems(__version__, pypi_versions,  git_tags):
    if not __version__:
        return "__version__ is corrupt or non existent"
    if git_tags:
        if __version__ in git_tags or LooseVersion(__version__) <= LooseVersion(git_tags[-1]):
            return "__version__ {} invalid in git tags. You must change it!".format(__version__)
    if pypi_versions:
        if __version__ in pypi_versions or LooseVersion(__version__) <= LooseVersion(pypi_versions[-1]):
            return "__version__ {} invalid in pypi versions. You must change it!".format(__version__)


def numeric_tags(tags):
    if tags:
        return sorted([tag for tag in tags if str(tag)[0].isdigit()], key=lambda tag: LooseVersion(str(tag)))
    return []


if __name__ == "__main__":
    main()
