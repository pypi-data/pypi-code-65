import uuid


def make_issue(
        word: str,
        start: int,
        end: int,
        issue_type: str,
        score,
        simpleDescription: str,
        description="",
        suggestions=[],
        subCategory="",
        learnMore="",
        paragraph=False,
        header="",
        metaDict={},
        accept_all_changes=False,
        debug=False,
):
    """
    reference:
    https://qordoba.atlassian.net/wiki/spaces/HOME/pages/840368141/Content-AI

    Note on duplicate value issueId / id: the platform switched this key at some point
    But I don't trust being able to delete things, so I will just duplicate it, and one day during a refactor
    we can remove it :grimace:
    """
    _uuid = str(uuid.uuid4())
    if not description:
        description = f'"{word}" is correlated with {issue_type} language.'

    issue = {
        "issueId": _uuid,
        "id": _uuid,
        "issueType": issue_type,
        "from": start,
        "until": end,
        "score": score,
        "suggestions": suggestions,
        "description": description,
        "simpleDescription": simpleDescription,
    }

    issue["meta"] = {"paragraph": paragraph}

    if subCategory:
        issue["meta"]["subCategory"] = subCategory

    if learnMore:
        issue["meta"]["learnMore"] = learnMore

    if header:
        issue["meta"]["header"] = header

    if accept_all_changes:
        issue["meta"]["acceptAllChanges"] = accept_all_changes

    # log warnings if meta_dict overwrites issue["meta"]
    if debug:
        common = [value for value in metaDict.keys() if value in issue["meta"]]
        for c in common:
            if metaDict[c] != issue["meta"][c]:
                print(f"Meta_dict {c}:{metaDict[c]} is overwriting issue meta {c}:{issue['meta'][c]}")

    issue["meta"].update(metaDict)

    return issue
