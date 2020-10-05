"""File module."""

# from files import file

# class Csv(file.File):

# def __init__(self, file):
# super().__init__(file)
# Keep as module


def check(file):
    # Type hints comments that are backwards compatiable with Python 2.
    # type: (str) -> None

    if file.endswith('csv'):
        print('file is csv')
    elif file.endswith('xlsx'):
        print('file is xlsx')
    else:
        print('no file')
