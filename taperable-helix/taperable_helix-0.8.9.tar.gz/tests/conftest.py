# From: https://stackoverflow.com/a/42145604
def pytest_addoption(parser):
    parser.addoption("--view", action="store_true", default=False)
    parser.addoption("--generate", action="store_true", default=False)


def pytest_generate_tests(metafunc):
    # This is called for every test. Only get/set command line arguments
    # if the argument is specified in the list of test "fixturenames".
    option_value = metafunc.config.option.view
    if "view" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("view", [option_value])

    option_value = metafunc.config.option.generate
    if "generate" in metafunc.fixturenames and option_value is not None:
        metafunc.parametrize("generate", [option_value])
