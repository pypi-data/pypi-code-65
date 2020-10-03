import logging
import traceback
from functools import wraps
import os
from subprocess import check_output

import zmtools


LOGGER = logging.getLogger(__name__)


def _create_issue(issue_title, issue_body, repo_owner, repo_name, issue_label="crashautoreport"):
    return check_output(["gh", "issue", "create", "--title", issue_title, "--body", issue_body, "--label", issue_label, "-R", f"{repo_owner}/{repo_name}"], shell=False)


def auto_create_issue(app_name=None, repo_owner=None, repo_name=None, exceptions=[]):
    def actual_decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                nonlocal app_name, repo_name, repo_owner, exceptions
                if not exceptions or any(isinstance(e, etype) for etype in exceptions):
                    if app_name is not None:
                        with open(os.path.join(os.sep, "etc", "githubreporter", app_name)) as f:
                            repo_owner, repo_name = [
                                l.strip() for l in f.readlines()]
                    elif repo_owner is None or repo_name is None:
                        raise ValueError(
                            "No repo_owner ot repo_name specified")
                    tb = traceback.format_exc().strip()
                    issue_title = zmtools.truncate(
                        tb.split("\n")[-1], length=25)
                    issue_body = f"```python\n{tb}\n```"
                    issue = _create_issue(
                        issue_title, issue_body, repo_owner=repo_owner, repo_name=repo_name)
                    LOGGER.info(f"An issue was created at {issue}")
                raise e
        return wrapper
    return actual_decorator
