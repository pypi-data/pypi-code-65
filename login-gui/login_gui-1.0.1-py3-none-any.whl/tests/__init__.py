"""
test folder with all tests of common lib
"""
from login_gui import MainGui

if __name__ == '__main__':
    functions = [
        "test function",
        "test function 1",
        "test function 2",
    ]
    print(MainGui(functions, 'My Gui').result)
    print(MainGui([], 'My Gui').result)
