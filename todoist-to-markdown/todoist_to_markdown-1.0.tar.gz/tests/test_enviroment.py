from todoist_to_markdown import enviroment


def test_get_environment():
    actual = enviroment.get_environment('TEST')
    assert actual == 'test'
