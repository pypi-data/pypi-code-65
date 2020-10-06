import os
import git
import typing


def git_unstaged_and_untracked_file_list(proj_dir: [str, git.Repo]) -> typing.List[str]:
    """
    获取 一个项目下面unstaged和untacked的文件列表
    """
    if isinstance(proj_dir, str):
        repo = git.Repo(proj_dir)
    else:
        assert isinstance(proj_dir, git.Repo)
        repo = proj_dir
    file_set = set()
    for diff in repo.index.diff(None):
        file_set.add(diff.a_path)
        file_set.add(diff.b_path)
    file_list = list(file_set)
    file_list = file_list + repo.untracked_files
    filter_file_list = []
    for name in file_list:
        abs_path = os.path.abspath(repo.git_dir, name)
        if os.path.exists(abs_path):
            filter_file_list.append(name)
    return filter_file_list


def git_current_branch(proj_dir: str) -> str:
    """
    获取git当前的branch
    """
    repo = git.Repo(proj_dir)
    return repo.active_branch
