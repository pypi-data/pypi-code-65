#!pipenv run python3
from pprint import pprint
from PyInquirer import prompt, Separator
from git import Repo
import os
import sys

def get_git_root():
    try:
        git_repo = Repo(os.getcwd(), search_parent_directories=True)
        git_root = git_repo.git.rev_parse("--show-toplevel")
        return git_root
    except:
        print("Not currently in a git repo")
        sys.exit()

repo = Repo(get_git_root())

assert not repo.bare

questions = [
    {
        'type': 'checkbox',
        # 'qmark': '😃',
        'message': 'Select Branches to Delete',
        'name': 'branches',
        'choices': [
            {
                'name': f"{b} -> {b.tracking_branch()}",
                'value': b
            }
            for b in repo.branches],
        'validate': lambda answer: 'You must choose at least one topping.' \
            if len(answer) == 0 else True
    }
]

answers = prompt(questions)
print("Deleted branches:")
try:
    for b in answers['branches']:
        # b.delete(repo, b)
        print(b)
except KeyError:
    pass

