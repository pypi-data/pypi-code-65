# Classes


class Command(object):
    """A command line statement."""

    def __init__(self, statement, comment=None, condition=None, cd=None, environments=None, function=None, name=None,
                 prefix=None, register=None, shell=None, stop=False, sudo=None, tags=None, **kwargs):
        """Initialize a command.

        :param statement: The statement to be executed.
        :type statement: str

        :param comment: A comment regarding the statement.
        :type comment: str

        :param condition: A (system-specific) condition for the statement to be executed.
        :type condition: str

        :param cd: The direction from which the statement should be executed.
        :type cd: str

        :param environments: A list of target environments where the statement should be executed.
        :type environments: list[str]

        :param function: The name of the function in which the statement is executed.
        :type function: str

        :param name: The name of the command from the mapping. Not used and not required for programmatic use, but
                     automatically assigned during factory instantiation.
        :type name: str

        :param prefix: A statement to execute before the main statement is executed.
        :type prefix: str

        :param register: A variable name to use for capture the success for failure of the statement's execution.
        :type register: str

        :param shell: The shell execute through which the statement is executed.
        :type shell: str

        :param stop: Indicates process should stop if the statement fails to execute.
        :type stop: bool | None

        :param sudo: Indicates whether sudo should be invoked for the statement. Given as a bool or user name or
                     :py:class:`scripttease.library.commands.base.Sudo` instance.
        :type sudo: bool | str | Sudo

        :param tags: A list of tags describing the statement.
        :type tags: list[str]

        Additional kwargs are available as dynamic attributes of the Command instance.

        """
        self.comment = comment
        self.condition = condition
        self.cd = cd
        self.environments = environments or list()
        self.function = function
        self.name = name
        self.prefix = prefix
        self.register = register
        self.shell = shell
        self.statement = statement
        self.stop = stop
        self.tags = tags or list()

        if isinstance(sudo, Sudo):
            self.sudo = sudo
        elif type(sudo) is str:
            self.sudo = Sudo(enabled=True, user=sudo)
        elif sudo is True:
            self.sudo = Sudo(enabled=True)
        else:
            self.sudo = Sudo()

        self._attributes = kwargs

    def __getattr__(self, item):
        return self._attributes.get(item)

    def __repr__(self):
        if self.comment is not None:
            return "<%s %s>" % (self.__class__.__name__, self.comment)

        return "<%s>" % self.__class__.__name__

    def get_statement(self, cd=False, suppress_comment=False):
        """Get the full statement.

        :param cd: Include the directory change, if given.
        :type cd: bool

        :param suppress_comment: Don't include the comment.
        :type suppress_comment: bool

        :rtype: str

        """
        a = list()

        if cd and self.cd is not None:
            a.append("( cd %s &&" % self.cd)

        if self.prefix is not None:
            a.append("%s &&" % self.prefix)

        if self.sudo:
            statement = "sudo -u %s %s" % (self.sudo.user, self._get_statement())
        else:
            statement = self._get_statement()

        a.append("%s" % statement)

        if cd and self.cd is not None:
            a.append(")")

        b = list()
        if self.comment is not None and not suppress_comment:
            b.append("# %s" % self.comment)

        if self.condition is not None:
            b.append("if [[ %s ]]; then %s; fi;" % (self.condition, " ".join(a)))
        else:
            b.append(" ".join(a))

        if self.register is not None:
            b.append("%s=$?;" % self.register)

            if self.stop:
                b.append("if [[ $%s -gt 0 ]]; exit 1; fi;" % self.register)
        elif self.stop:
            b.append("if [[ $? -gt 0 ]]; exit 1; fi;")
        else:
            pass

        return "\n".join(b)

    def has_attribute(self, name):
        """Indicates whether the command has the named, dynamic attribute.

        :param name: The name of the attribute to be checked.
        :type name: str

        :rtype: bool

        """
        return name in self._attributes

    def set_attribute(self, name, value):
        """Set the value of a dynamic attribute.

        :param name: The name of the attribute.
        :type name: str

        :param value: The value of the attribute.

        """
        self._attributes[name] = value

    def _get_statement(self):
        """By default, get the statement passed upon command initialization.

        :rtype: str

        """
        return self.statement


class ItemizedCommand(object):
    """An itemized command represents multiple commands of with the same statement but different parameters."""

    def __init__(self, callback, items, *args, name=None, **kwargs):
        """Initialize the command.

        :param callback: The function to be used to generate the command.

        :param items: The command arguments.
        :type items: list[str]

        :param name: The name of the command from the mapping. Not used and not required for programmatic use, but
                     automatically assigned during factory instantiation.
        :type name: str

        :param args: The itemized arguments. ``$item`` should be included.

        Keyword arguments are passed to the command class upon instantiation.

        """
        self.args = args
        self.callback = callback
        self.items = items
        self.kwargs = kwargs
        self.name = name

    def __getattr__(self, item):
        return self.kwargs.get(item)

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, self.callback.__name__)

    def get_commands(self):
        """Get the commands to be executed.

        :rtype: list[BaseType(Command)]

        """
        kwargs = self.kwargs.copy()

        a = list()
        for item in self.items:
            args = list()
            for arg in self.args:
                args.append(arg.replace("$item", item))

            command = self.callback(*args, **kwargs)
            a.append(command)

        return a

    def get_statement(self, cd=False):
        """Override to get multiple commands."""
        kwargs = self.kwargs.copy()
        comment = kwargs.pop("comment", "execute multiple commands")

        a = list()
        # a.append("# %s" % comment)

        commands = self.get_commands()
        for c in commands:
            a.append(c.get_statement(cd=cd))
            a.append("")

        # for item in self.items:
        #     args = list()
        #     for arg in self.args:
        #         args.append(arg.replace("$item", item))
        #
        #     command = self.command_class(*args, **kwargs)
        #     a.append(command.preview(cwd=cwd))
        #     a.append("")

        return "\n".join(a)

    def has_attribute(self, name):
        """Indicates whether the command has the named, dynamic attribute.

        :param name: The name of the attribute to be checked.
        :type name: str

        :rtype: bool

        """
        return name in self.kwargs

    def set_attribute(self, name, value):
        """Set the value of a dynamic attribute.

        :param name: The name of the attribute.
        :type name: str

        :param value: The value of the attribute.

        .. note::
            This is applied to all command in the itemized list.

        """
        self.kwargs[name] = value


class Sudo(object):
    """Helper class for defining sudo options."""

    def __init__(self, enabled=False, user="root"):
        """Initialize the helper.

        :param enabled: Indicates sudo is enabled.
        :type enabled: bool

        :param user: The user to be invoked.
        :type user: str

        """
        self.enabled = enabled
        self.user = user

    def __bool__(self):
        return self.enabled
