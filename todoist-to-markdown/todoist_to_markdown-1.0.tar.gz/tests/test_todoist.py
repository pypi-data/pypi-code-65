from todoist_to_markdown import todoist


def test_get_today_tasks():
    # エラーがなければ成功とする
    todoist.get_today_tasks()
    assert True
