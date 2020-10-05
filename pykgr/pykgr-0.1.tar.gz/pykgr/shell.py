import os
import subprocess
import sys

class Shell(object):
    working_dir = None
    # A pythonic shell

    def __getattribute__(self, key):
        try:
            data = object.__getattribute__(self, key)
            return data
        except AttributeError as err:
            if key in os.environ:
                return os.environ.get(key)
            else:
                return Command(key)

    def __new__(cls, *args, **kwargs):
        # `args` are treated as arguments into a shell,
        # e.g. `Shell("ls -l")` or `Shell("ls", "-l")`
        # returns the stdout of `/bin/sh -c "ls -l"`
        # while `Shell("ls")` returns a "program" (below.)
        #
        # Kwargs are environment variables, e.g.
        # Shell("echo $test", test="world") is akin
        # to test="world" echo $test.
        #
        # An empty class returns a blank shell instance,
        # for "interactive" mode like `sh = Shell(); sh.command("ls -l")`
        #
        # For a blank shell in a given folder you would, e.g.
        # Shell(PWD="/my/source/code/folder").command("configure -flag")
        # or
        # Shell(PWD="/my/source/code/folder").configure("-flag")
        if len(args):
            print(args)

        if len(kwargs):
            for key in kwargs:
                if key == "PWD":
                    os.chdir(kwargs.get("PWD"))
                os.environ[key] = kwargs.get(key)

        self = super(Shell, cls).__new__(cls)
        return self

    def __str__(self):
        return "<Shell @ %s>" % (
            os.environ.get('PWD')
        )

    def cd(self, directory):
        os.chdir(directory)
        os.environ["PWD"] = directory

    def command(self, *args):
        cmd = args[0]
        arguments = []
        if len(args) >= 2:
            arguments = args[1:]

        return Command(cmd, *arguments)

class Command:
    args = None
    env = None
    program = None

    def __call__(self, *args, **kwargs):
        self.args = args

        return self.run(display_output=kwargs.get('display_output'))

    def __init__(self, command, *args, **kwargs):
        self.program = command
        self.args = args
        self.env = kwargs

    def run(self, display_output = False):
        command_line = [
            self.program
        ] + list(self.args)

        process = subprocess.Popen(
            command_line,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        if display_output:
            for line in iter(process.stdout.readline, b''):
                sys.stdout.write(line.decode())

        output, error = process.communicate()
        if type(output) == bytes:
            output = output.decode()

        return output