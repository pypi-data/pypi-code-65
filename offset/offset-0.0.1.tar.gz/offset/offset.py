"""
Shift text with the following modes:
    - Command mode
    - Interactive mode
    - Convert file mode
"""
import os
import sys
import platform
from optparse import OptionParser
from datetime import datetime

class Offset:
    """
    - import as a module

        from offset import Offset
        TestShifter.convert(text, number)

    - Command mode:

        $python3 letter_shifter.py -n 10 -s 'Hello'

    - File mode:
        >The new file will be stored at '~/offset_export/filename_%Y%m%d_%H%M%S.ext'

        $python3 letter_shifter.py -n 10 -f 'path/filename.ext'

    - Get into interactive mode

        $python3 letter_shifter.py -i [-n int]
    """

    EXPORT_PATH = os.path.expanduser('~/offset_export/')

    OS = platform.system()  # {'Linux': 'Linux', 'Mac': 'Darwin', 'Windows': 'Windows'}

    LIMIT = 1_000_000

    @staticmethod
    def _get_args():
        option = OptionParser()
        option.add_option(
            '-i', '--interactive-mode', action='store_true', dest='interactive', default=False)
        option.add_option(
            '-o', '--open', action='store_true', dest='is_open', default=False)
        option.add_option(
            '-n', '--number', action='store', type='int', dest='number', default=None)
        option.add_option(
            '-s', '--string', action='store', type='string', dest='string', default=None)
        option.add_option(
            '-d', '--directory', action='store', type='string', dest='directory', default=None)
        return option.parse_args()[0]

    @classmethod
    def help(cls):
        print(cls.__doc__)
        sys.exit()

    @classmethod
    def _navigate(cls):
        if cls.OS == 'Darwin':
            os.system(f'open {cls.EXPORT_PATH}')
        elif cls.OS == 'Linux':
            os.system(f'xdg-open {cls.EXPORT_PATH}')
        elif cls.OS == 'Windows':
            os.system(f'start {cls.EXPORT_PATH}')
        else:
            raise SystemError(f'Unknown OS: {cls.OS}')

    @classmethod
    def convert(cls, text, number):
        """
        :param text: input string
        :type text: str
        :param number: shift value
        :type number: int
        :rtype: str
        :return: text shift result

        >>> Offset.convert(text="hello, world", number=1)
        'ifmmp-!xpsme'

        >>> Offset.convert("ifmmp-!xpsme", -1)
        'hello, world'

        >>> Offset.convert("ifmmp-!xpsme", 1000000)
        'hello, world'
        """
        if number > cls.LIMIT:
            raise ValueError(f'number must less than {cls.LIMIT:,}')
        return ''.join(chr(ord(_) + number) for _ in text)

    @classmethod
    def _interactive_mode(cls, number):
        if number:
            while True:
                text = input('input string ([ctrl-c] to quit): ')
                print(cls.convert(text=text, number=number))
            sys.exit()
        while True:
            text = input('input string ([ctrl-c] to quit): ')
            number = int(input('input shift number: '))
            print(cls.convert(text=text, number=number))

    @classmethod
    def _command_mode(cls, string, number):
        if not number:
            raise ValueError('-n --number[int] is required!')
        print(cls.convert(text=string, number=number))
        sys.exit()

    @classmethod
    def _file_mode(cls, directory, number, is_navigate):
        if not number:
            raise ValueError('-n --number[int] is required!')
        if not os.path.isfile(directory):
            raise FileNotFoundError(directory)
        name, ext = os.path.splitext(os.path.basename(directory))
        with open(directory, 'r') as file_read:
            text = file_read.read()
            text_converted = cls.convert(text=text, number=number)
        filename = f'{name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}{ext}'
        pathname = os.path.join(cls.EXPORT_PATH, filename)
        with open(pathname, 'w') as file_write:
            file_write.write(text_converted)
        if is_navigate:
            cls._navigate()
        sys.exit()

    @classmethod
    def cli(cls):
        """
        command line
        """
        os.makedirs(cls.EXPORT_PATH, exist_ok=True)

        args = cls._get_args()

        if args.interactive:
            cls._interactive_mode(number=args.number)
        if args.string:
            cls._command_mode(string=args.string, number=args.number)
        if args.directory:
            cls._file_mode(directory=args.directory, number=args.number, is_navigate=args.is_open)
        cls.help()
