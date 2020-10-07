# Classes


class Script(object):
    """A script is a collection of commands."""

    def __init__(self, name, commands=None, functions=None, shell="bash"):
        """Initialize a script.

        :param name: The name of the script. Note: This becomes the file name.
        :type name: str

        :param commands: The commands to be included.
        :type commands: list[scripttease.library.commands.base.Command]

        :param functions: The functions to be included.
        :type functions: list[Function]

        :param shell: The shell to use for the script.
        :type shell: str

        """
        self.commands = commands or list()
        self.functions = functions
        self.name = name
        self.shell = shell

    def __str__(self):
        return self.to_string()

    def append(self, command):
        """Append a command instance to the script's commands.

        :param command: The command instance to be included.
        :type command: BaseType[Command] | ItemizedCommand

        """
        self.commands.append(command)

    def to_string(self, shebang="#! /usr/bin/env %(shell)s"):
        """Export the script as a string.

        :param shebang: The shebang to be included. Set to ``None`` to omit the shebang.
        :type shebang: str

        :rtype: str

        """
        a = list()

        if shebang is not None:
            a.append(shebang % {'shell': self.shell})
            a.append("")

        if self.functions is not None:
            for function in self.functions:
                a.append(function.to_string())
                a.append("")

            # for function in self.functions:
            #     a.append("%s;" % function.name)

            a.append("")

        for command in self.commands:
            a.append(command.get_statement(cd=True))
            a.append("")

        return "\n".join(a)
