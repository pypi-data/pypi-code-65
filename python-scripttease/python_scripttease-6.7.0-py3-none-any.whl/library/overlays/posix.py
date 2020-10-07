# Imports

from commonkit import indent, split_csv
import os
from ..commands import Command

# Exports

__all__ = (
    "POSIX_MAPPINGS",
    "archive",
    "certbot",
    "dialog",
    "echo",
    "extract",
    "file_append",
    "file_copy",
    "file_write",
    "mkdir",
    "move",
    "perms",
    "prompt",
    "remove",
    "rename",
    "rsync",
    "scopy",
    "sed",
    "symlink",
    "touch",
    "wait",
    "Function",
    "Prompt",
)

# Functions


def archive(from_path, absolute=False, exclude=None, file_name="archive.tgz", strip=None, to_path=".", view=False,
            **kwargs):
    """Create a file archive.

    - from_path (str): The path that should be archived.
    - absolute (bool): Set to ``True`` to preserve the leading slash.
    - exclude (str): A pattern to be excluded from the archive.
    - strip (int): Remove the specified number of leading elements from the path.
    - to_path (str): Where the archive should be created. This should *not* include the file name.
    - view (bool): View the output of the command as it happens.

    """
    tokens = ["tar"]
    switches = ["-cz"]

    if absolute:
        switches.append("P")

    if view:
        switches.append("v")

    tokens.append("".join(switches))

    if exclude:
        tokens.append("--exclude %s" % exclude)

    if strip:
        tokens.append("--strip-components %s" % strip)

    to_path = os.path.join(to_path, file_name)
    tokens.append('-f %s %s' % (to_path, from_path))

    name = " ".join(tokens)

    return Command(name, **kwargs)


def certbot(domain_name, email=None, webroot=None, **kwargs):
    """Get new SSL certificate from Let's Encrypt.

    - domain_name (str): The domain name for which the SSL certificate is requested.
    - email (str): The email address of the requester sent to the certificate authority. Required.
    - webroot (str): The directory where the challenge file will be created.

    """
    _email = email or os.environ.get("SCRIPTTEASE_CERTBOT_EMAIL", None)
    _webroot = webroot or os.path.join("/var", "www", "domains", domain_name.replace(".", "_"), "www")

    if not _email:
        raise ValueError("Email is required for certbot command.")

    template = "certbot certonly --agree-tos --email %(email)s -n --webroot -w %(webroot)s -d %(domain_name)s"
    name = template % {
        'domain_name': domain_name,
        'email': _email,
        'webroot': _webroot,
    }

    return Command(name, **kwargs)


def dialog(message, height=15, title="Message", width=100, **kwargs):
    """Display a dialog message.

    - message (str): The message to be displayed.
    - height (int): The height of the dialog.
    - title (str): The title of the dialog.
    - width (int): The width of the dialog.

    """
    kwargs.setdefault("comment", "display a dialog message")

    a = list()
    a.append('dialog --clear --backtitle "%s"' % title)
    a.append('--msgbox "%s" %s %s; clear;' % (message, height, width))

    return Command(" ".join(a), **kwargs)


def echo(message, **kwargs):
    """Echo a message.

    - message (str): The message to be printed to screen.

    """
    kwargs.setdefault("comment", "print message to screen")

    return Command('echo "%s"' % message, **kwargs)


def extract(from_path, absolute=False, exclude=None, strip=None, to_path=None, view=False, **kwargs):
    """Extract a file archive.

    - from_path (str): The path that should be archived.
    - absolute (bool): Set to ``True`` to preserve the leading slash.
    - exclude (str): A pattern to be excluded from the archive.
    - strip (int): Remove the specified number of leading elements from the path.
    - to_path (str): Where the archive should be extracted. This should *not* include the file name.
    - view (bool): View the output of the command as it happens.

    """
    _to_path = to_path or "./"

    tokens = ["tar"]
    switches = ["-xz"]

    if absolute:
        switches.append("P")

    if view:
        switches.append("v")

    tokens.append("".join(switches))

    if exclude:
        tokens.append("--exclude %s" % exclude)

    if strip:
        tokens.append("--strip-components %s" % strip)

    tokens.append('-f %s %s' % (from_path, _to_path))

    name = " ".join(tokens)

    return Command(name, **kwargs)


def file_append(path, content=None, **kwargs):
    """Append content to a file.

    - path (str): The path to the file.
    - content (str): The content to be appended.

    """
    kwargs.setdefault("comment", "append to %s" % path)

    statement = 'echo "%s" >> %s' % (content or "", path)

    return Command(statement, **kwargs)


def file_copy(from_path, to_path, overwrite=False, recursive=False, **kwargs):
    """Copy a file or directory.

    - from_path (str): The file or directory to be copied.
    - to_path (str): The location to which the file or directory should be copied.
    - overwrite (bool): Indicates files and directories should be overwritten if they exist.
    - recursive (bool): Copy sub-directories.

    """
    kwargs.setdefault("comment", "copy %s to %s" % (from_path, to_path))

    a = list()
    a.append("cp")

    if not overwrite:
        a.append("-n")

    if recursive:
        a.append("-R")

    a.append(from_path)
    a.append(to_path)

    return Command(" ".join(a), **kwargs)


def file_write(path, content=None, **kwargs):
    """Write to a file.

    - path (str): The file to be written.
    - content (str): The content to be written. Note: If omitted, this command is equivalent to ``touch``.

    """
    _content = content or ""

    kwargs.setdefault("comment", "write to %s" % path)

    a = list()

    if len(_content.split("\n")) > 1:
        a.append("cat > %s << EOF" % path)
        a.append(_content)
        a.append("EOF")
    else:
        a.append('echo "%s" > %s' % (_content, path))

    return Command(" ".join(a), **kwargs)


def mkdir(path, mode=None, recursive=True, **kwargs):
    """Create a directory.

    - path (str): The path to be created.
    - mode (int | str): The access permissions of the new directory.
    - recursive (bool): Create all directories along the path.

    """
    kwargs.setdefault("comment", "create directory %s" % path)

    statement = ["mkdir"]
    if mode is not None:
        statement.append("-m %s" % mode)

    if recursive:
        statement.append("-p")

    statement.append(path)

    return Command(" ".join(statement), **kwargs)


def move(from_path, to_path, **kwargs):
    """Move a file or directory.
    
    - from_path (str): The current path.
    - to_path (str): The new path.
    
    """
    kwargs.setdefault("comment", "move %s to %s" % (from_path, to_path))
    statement = "mv %s %s" % (from_path, to_path)

    return Command(statement, **kwargs)


def perms(path, group=None, mode=None, owner=None, recursive=False, **kwargs):
    """Set permissions on a file or directory.

    - path (str): The path to be changed.
    - group (str): The name of the group to be applied.
    - mode (int | str): The access permissions of the file or directory.
    - owner (str): The name of the user to be applied.
    - recursive: Create all directories along the path.

    """
    commands = list()

    kwargs['comment'] = "set permissions on %s" % path

    if group is not None:
        statement = ["chgrp"]

        if recursive:
            statement.append("-R")

        statement.append(group)
        statement.append(path)

        commands.append(Command(" ".join(statement), **kwargs))

    if owner is not None:
        statement = ["chown"]

        if recursive:
            statement.append("-R")

        statement.append(owner)
        statement.append(path)

        commands.append(Command(" ".join(statement), **kwargs))

    if mode is not None:
        statement = ["chmod"]

        if recursive:
            statement.append("-R")

        statement.append(str(mode))
        statement.append(path)

        commands.append(Command(" ".join(statement), **kwargs))

    kwargs.setdefault("comment", "set permissions on %s" % path)

    a = list()
    for c in commands:
        a.append(c.get_statement(suppress_comment=True))

    return Command("\n".join(a), **kwargs)


def prompt(name, back_title="Input", choices=None, default=None, fancy=False, help_text=None, label=None, **kwargs):
    """Prompt the user for input.

    - name (str): The programmatic name of the input.
    - back_title (str): The back title used with the dialog command.
    - choices (str | list): A list of valid choices.
    - default: The default value.
    - fancy (bool): Use a dialog command for the prompt.
    - help_text (str): The text to display with the dialog command.
    - label (str): The label for the input.

    """
    return Prompt(
        name,
        back_title=back_title,
        choices=choices,
        default=default,
        fancy=fancy,
        help_text=help_text,
        label=label,
        **kwargs
    )


def remove(path, force=False, recursive=False, **kwargs):
    """Remove a file or directory.

    - path (str): The path to be removed.
    - force (bool): Force the removal.
    - recursive (bool): Remove all directories along the path.

    """
    kwargs.setdefault("comment", "remove %s" % path)

    statement = ["rm"]

    if force:
        statement.append("-f")

    if recursive:
        statement.append("-r")

    statement.append(path)

    return Command(" ".join(statement), **kwargs)


def rename(from_name, to_name, **kwargs):
    """Rename a file or directory.

    - from_name (str): The name (or path) of the existing file.
    - to_name (str): The name (or path) of the new file.

    """
    kwargs.setdefault("comment", "rename %s" % from_name)
    return move(from_name, to_name, **kwargs)


def rsync(source, target, delete=False, exclude=None, host=None, key_file=None, links=True, port=22,
          recursive=True, user=None, **kwargs):
    """Synchronize a directory structure.

    - source (str): The source directory.
    - target (str): The target directory.
    - delete (bool): Indicates target files that exist in source but not in target should be removed.
    - exclude (str): The path to an exclude file.
    - host (str): The host name or IP address. This causes the command to run over SSH.
    - key_file (str): The privacy SSH key (path) for remote connections. User expansion is automatically applied.
    - links (bool): Include symlinks in the sync.
    - port (int): The SSH port to use for remote connections.
    - recursive (bool): Indicates source contents should be recursively synchronized.
    - user (str): The user name to use for remote connections.

    """
    # - guess: When ``True``, the ``host``, ``key_file``, and ``user`` will be guessed based on the base name of
    #               the source path.
    # :type guess: bool
    # if guess:
    #     host = host or os.path.basename(source).replace("_", ".")
    #     key_file = key_file or os.path.expanduser(os.path.join("~/.ssh", os.path.basename(source)))
    #     user = user or os.path.basename(source)
    # else:
    #     host = host
    #     key_file = key_file
    #     user = user

    kwargs.setdefault("comment", "sync %s with %s" % (source, target))

    # rsync -e "ssh -i $(SSH_KEY) -p $(SSH_PORT)" -P -rvzc --delete
    # $(OUTPUTH_PATH) $(SSH_USER)@$(SSH_HOST):$(UPLOAD_PATH) --cvs-exclude;

    tokens = list()
    tokens.append("rsync")
    tokens.append("--cvs-exclude")
    tokens.append("--checksum")
    tokens.append("--compress")

    if links:
        tokens.append("--copy-links")

    if delete:
        tokens.append("--delete")

    if exclude is not None:
        tokens.append("--exclude-from=%s" % exclude)

    # --partial and --progress
    tokens.append("-P")

    if recursive:
        tokens.append("--recursive")

    tokens.append(source)

    conditions = [
        host is not None,
        key_file is not None,
        user is not None,
    ]
    if all(conditions):
        tokens.append('-e "ssh -i %s -p %s"' % (key_file, port))
        tokens.append("%s@%s:%s" % (user, host, target))
    else:
        tokens.append(target)

    statement = " ".join(tokens)

    return Command(statement, **kwargs)


def scopy(from_path, to_path, host=None, key_file=None, port=22, user=None, **kwargs):
    """Copy a file or directory to a remote server.

    - from_path (str): The source directory.
    - to_path (str): The target directory.
    - host (str): The host name or IP address. Required.
    - key_file (str): The privacy SSH key (path) for remote connections. User expansion is automatically applied.
    - port (int): The SSH port to use for remote connections.
    - user (str): The user name to use for remote connections.

    """
    kwargs.setdefault("comment", "copy %s to remote %s" % (from_path, to_path))

    # TODO: What to do to force local versus remote commands?
    # kwargs['local'] = True

    kwargs['sudo'] = False

    statement = ["scp"]

    if key_file is not None:
        statement.append("-i %s" % key_file)

    statement.append("-P %s" % port)
    statement.append(from_path)

    if host is not None and user is not None:
        statement.append("%s@%s:%s" % (user, host, to_path))
    elif host is not None:
        statement.append("%s:%s" % (host, to_path))
    else:
        raise ValueError("Host is a required keyword argument.")

    return Command(" ".join(statement), **kwargs)


def sed(path, backup=".b", delimiter="/", find=None, replace=None, **kwargs):
    """Find and replace text in a file.

    - path (str): The path to the file to be edited.
    - backup (str): The backup file extension to use.
    - delimiter (str): The pattern delimiter.
    - find (str): The old text. Required.
    - replace (str): The new text. Required.

    """

    kwargs.setdefault("comment", "find and replace in %s" % path)

    context = {
        'backup': backup,
        'delimiter': delimiter,
        'path': path,
        'pattern': find,
        'replace': replace,
    }

    template = "sed -i %(backup)s 's%(delimiter)s%(pattern)s%(delimiter)s%(replace)s%(delimiter)sg' %(path)s"

    statement = template % context

    return Command(statement, **kwargs)


def symlink(source, force=False, target=None, **kwargs):
    """Create a symlink.

    - source (str): The source of the link.
    - force (bool): Force the creation of the link.
    - target (str): The name or path of the target. Defaults to the base name of the source path.

    """
    _target = target or os.path.basename(source)

    kwargs.setdefault("comment", "link to %s" % source)

    statement = ["ln -s"]

    if force:
        statement.append("-f")

    statement.append(source)
    statement.append(_target)

    return Command(" ".join(statement), **kwargs)


def touch(path, **kwargs):
    """Touch a file or directory.

    - path (str): The file or directory to touch.

    """
    kwargs.setdefault("comment", "touch %s" % path)

    return Command("touch %s" % path, **kwargs)


def wait(seconds, **kwargs):
    """Pause execution for a number of seconds.

    - seconds (int): The number of seconds to wait.

    """
    kwargs.setdefault("comment", "pause for %s seconds" % seconds)

    return Command("sleep %s" % seconds, **kwargs)

# Classes


class Function(object):
    """A function that may be used to organize related commands to be called together."""

    def __init__(self, name, commands=None, comment=None):
        """Initialize a function.

        :param name: The name of the function.
        :type name: str

        :param commands: The command instances to be included in the function's output.
        :type commands: list

        :param comment: A comment regarding the function.
        :type comment: str

        """
        self.commands = commands or list()
        self.comment = comment
        self.name = name

    def to_string(self):
        """Export the function as a string.

        :rtype: str

        """
        a = list()

        if self.comment is not None:
            a.append("# %s" % self.comment)

        a.append("function %s()" % self.name)
        a.append("{")
        for command in self.commands:
            a.append(indent(command.get_statement(cd=True)))
            a.append("")

        a.append("}")

        return "\n".join(a)


class Prompt(Command):
    """Prompt the user for input."""

    def __init__(self, name, back_title="Input", choices=None, default=None, fancy=False, help_text=None, label=None,
                 **kwargs):
        """Initialize a prompt for user input.

        :param name: The variable name.
        :type name: str

        :param back_title: The back title of the input. Used only when ``dialog`` is enabled.
        :type back_title: str

        :param choices: Valid choices for the variable. May be given as a list of strings or a comma separated string.
        :type choices: list[str] | str

        :param default: The default value of the variable.

        :param fancy: Indicates the dialog command should be used.
        :type fancy: bool

        :param help_text: Additional text to display. Only use when ``fancy`` is ``True``.
        :type help_text: str

        :param label: The label of the prompt.

        """
        self.back_title = back_title
        self.default = default
        self.dialog_enabled = fancy
        self.help_text = help_text
        self.label = label or name.replace("_", " ").title()
        self.variable_name = name

        if type(choices) in (list, tuple):
            self.choices = choices
        elif type(choices) is str:
            self.choices = split_csv(choices, smart=False)
            # for i in choices.split(","):
            #     self.choices.append(i.strip())
        else:
            self.choices = None

        kwargs.setdefault("comment", "prompt user for %s input" % name)

        super().__init__(name, **kwargs)

    def get_statement(self, cd=False, suppress_comment=False):
        """Get the statement using dialog or read."""
        if self.dialog_enabled:
            return self._get_dialog_statement()

        return self._get_read_statement()

    def _get_dialog_statement(self):
        """Get the dialog statement."""
        a = list()

        a.append('dialog --clear --backtitle "%s" --title "%s"' % (self.back_title, self.label))

        if self.choices is not None:
            a.append('--menu "%s" 15 40 %s' % (self.help_text or "Select", len(self.choices)))
            count = 1
            for choice in self.choices:
                a.append('"%s" %s' % (choice, count))
                count += 1

            a.append('2>/tmp/input.txt')
        else:
            if self.help_text is not None:
                a.append('--inputbox "%s"' % self.help_text)
            else:
                a.append('--inputbox ""')

            a.append('8 60 2>/tmp/input.txt')

        b = list()

        b.append('touch /tmp/input.txt')
        b.append(" ".join(a))

        b.append('%s=$(</tmp/input.txt)' % self.variable_name)
        b.append('clear')
        b.append('rm /tmp/input.txt')

        if self.default is not None:
            b.append('if [[ -z "$%s" ]]; then %s="%s"; fi;' % (self.variable_name, self.variable_name, self.default))

        # b.append('echo "$%s"' % self.name)

        return "\n".join(b)

    def _get_read_statement(self):
        """Get the standard read statement."""
        a = list()

        if self.choices is not None:
            a.append('echo "%s "' % self.label)

            options = list()
            for choice in self.choices:
                options.append('"%s"' % choice)

            a.append('options=(%s)' % " ".join(options))
            a.append('select opt in "${options[@]}"')
            a.append('do')
            a.append('    case $opt in')

            for choice in self.choices:
                a.append('        "%s") %s=$opt; break;;' % (choice, self.variable_name))

            # a.append('        %s) %s=$opt;;' % ("|".join(self.choices), self.name))
            a.append('        *) echo "invalid choice";;')
            a.append('    esac')
            a.append('done')

            # a.append("read %s" % self.name)
        else:
            a.append('echo -n "%s "' % self.label)
            a.append("read %s" % self.variable_name)

        if self.default is not None:
            a.append('if [[ -z "$%s" ]]; then %s="%s"; fi;' % (self.variable_name, self.variable_name, self.default))

        # a.append('echo "$%s"' % self.name)

        return "\n".join(a)

# Mappings


POSIX_MAPPINGS = {
    'append': file_append,
    'archive': archive,
    'certbot': certbot,
    'copy': file_copy,
    'dialog': dialog,
    'echo': echo,
    'extract': extract,
    'func': Function,
    # 'function': Function,
    'mkdir': mkdir,
    'move': move,
    'perms': perms,
    'prompt': prompt,
    'remove': remove,
    'rename': rename,
    'rsync': rsync,
    'scopy': scopy,
    'sed': sed,
    'ssl': certbot,
    'symlink': symlink,
    'touch': touch,
    'wait': wait,
    'write': file_write,
}
