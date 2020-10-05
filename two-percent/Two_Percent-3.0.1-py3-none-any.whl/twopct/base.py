# Standard library imports.
from _io import TextIOWrapper
import argparse
import io
import os
import sys


class Command(object):

    def create_argparser(self):

        # Create the argument parser.
        parser = argparse.ArgumentParser()

        # Add an optional argument prior to calling the "add_arguments"
        # method.  Any class that uses this class as a base will
        # automatically have the "add2path" functionality added.
        parser.add_argument(
            '--add2path',
            nargs = '*',
            help = 'Add to the Python path')

        # Add more arguments.  This method should be extended by any
        # classes using this class as a base.
        self.add_arguments(parser)

        return parser

    def add_arguments(self, parser):

        parser.add_argument(
            '--infile',
            type = argparse.FileType('r'),
            default = sys.stdin,
            help = 'File containing input data for this command')

        return None

    def handle(self, *args, **kwargs):

        # This is just an example of how the Command should work.
        # Child classes should override this completely.
        data_in = kwargs.get('infile').read()

        # Return the "sys.path", if the "data_in" is empty.
        if data_in == '':
            data_in = str(sys.path)

        return data_in

    def stdout(self, text):

        if not text.endswith('\r\n') or not text.endswith('\n'):
            text += '\n'

        try:

            sys.stdout.write(text)
            sys.stdout.flush()

        except BrokenPipeError as e:

            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())

            # Exit the script with an error code.
            sys.exit(1)

        return None

    def stderr(self, text):

        if not text.endswith('\r\n') or not text.endswith('\n'):
            text += '\n'

        try:

            sys.stderr.write(text)
            sys.stderr.flush()

        except BrokenPipeError as e:

            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stderr.fileno())

            # Exit the script with an error code.
            sys.exit(1)

        return None

    @staticmethod
    def add2path(new_path):

        # The "new_path" parameter may be a relative path, so get the
        # absolute path for the given parameter.
        new_path = os.path.abspath(new_path)

        # Make sure the "new_path" parameter is lowercase when running
        # on the Windows flavor of an Operating Systemp.
        if sys.platform == 'win32':
            new_path = new_path.lower()

        # Determine if the "new_path" exists.  If so, attempt to add to
        # the "sys.path".
        if os.path.exists(new_path) == True:

            # Define a flag that will indicate if the "new_path"
            # parameter should be added to the path.
            add = True

            for x in sys.path:

                # If a path in the "sys.path" is relative, get the
                # absolute path instead.  Used to check against the
                # "new_path" parameter.
                x = os.path.abspath(x)

                # Once again, make sure the path values are lowercase
                # when using on Windows.
                if sys.platform == 'win32':
                    x = x.lower()

                if new_path in (x, x + os.sep):
                    add = False

            # If a match was not found, add the "new_path" value
            # to the path.  Set the counter
            if add == True:
                sys.path.append(new_path)

        return None

    @classmethod
    def get_handled(cls, *args, **kwargs):
        """Returns the Command instance after the handle method is run.

        """
        cmd = cls()
        cmd.handle(*args, **kwargs)

        return cmd

    @classmethod
    def run(cls):

        # Creates a Two-Percent Command class instance.
        cmd = cls()

        # Parse the command line arguments into a Namespace instance.
        # Input may also include a stdin pipe, if defined in the
        # "add_arguments" method.
        parser = cmd.create_argparser()
        ns = parser.parse_args()

        # Create the kwargs variable.  Loop over the arguments to find
        # a TextIOWrapper class.  If found, then check if its name is
        # "<stdin>".  If so, check if stdin is empty.  If so, then set
        # the keyword argument to an empty StringIO class.  This fixes
        # the possibility for the program to hang.
        kwargs = vars(ns)

        for k in kwargs.keys():
            if type(kwargs[k]) == TextIOWrapper:
                if kwargs[k].name == '<stdin>':
                    if sys.stdin.isatty():
                        kwargs[k] = io.StringIO()

        # Process any new additions to the "sys.path" via the
        # "add2path" argparse argument.
        if type(kwargs.get('add2path')) == type([]):
            for new_path in kwargs['add2path']:
                if type(new_path) == type(''):
                    cls.add2path(new_path)

        # Remove the "add2path" key/value pair from the keyword
        # arguments.  Not needed in the "handle" method.
        if kwargs.get('add2path', None) is not None:
            del kwargs['add2path']

        # Run the command and write the resulting object to stdout if
        # the return value of the handle method is a string.
        output = cmd.handle(**kwargs)

        if type(output) == type(''):
            if output != '':
                cmd.stdout(output)

        return None


def main():
    Command.run()


if __name__ == '__main__':

    # Call the Command.
    main()

