# Imports

from commonkit import parse_jinja_template, read_file
from jinja2.exceptions import TemplateError, TemplateNotFound
import logging
import os
from ...constants import LOGGER_NAME
from .base import Command

log = logging.getLogger(LOGGER_NAME)

# Exports

__all__ = (
    "Template",
)

# Classes


class Template(Command):
    """Parse a template."""

    PARSER_JINJA = "jinja2"
    PARSER_SIMPLE = "simple"

    def __init__(self, source, target, backup=True, lines=False, parser=PARSER_JINJA, pythonic=False, **kwargs):
        """Initialize the command.

        :param source: The template source file.
        :type source: str

        :param target: The path to the output file.
        :type target: str

        :param backup: Indicates a copy of an existing file should be madee.
        :type backup: bool

        :param parser: The parser to use.
        :type parser: str

        :param pythonic: Use a Python one-liner to write the file. Requires Python installation, obviously. This is
                         useful when the content of the file cannot be handled with a cat command; for example, shell
                         script templates.
        :type pythonic: bool

        """
        # Base parameters need to be captured, because all others are assumed to be switches for the management command.
        self._kwargs = {
            'comment': kwargs.pop("comment", None),
            'cd': kwargs.pop("cd", None),
            'environments': kwargs.pop("environments", None),
            'function': kwargs.pop("function", None),
            # 'local': kwargs.pop("local", False),
            'name': "template",
            'prefix': kwargs.pop("prefix", None),
            'shell': kwargs.pop("shell", "/bin/bash"),
            'stop': kwargs.pop("stop", False),
            'sudo': kwargs.pop('sudo', False),
            'tags': kwargs.pop("tags", None),
        }

        self.backup_enabled = backup
        self.context = kwargs.pop("context", dict())
        self.parser = parser or self.PARSER_JINJA
        self.pythonic = pythonic
        self.line_by_line = lines
        self.locations = kwargs.pop("locations", list())
        self.source = os.path.expanduser(source)
        self.target = target

        # Remaining kwargs are added to the context.
        # print(_kwargs['comment'], kwargs)
        self.context.update(kwargs)

        super().__init__("# template: %s" % source, **self._kwargs)

    def get_content(self):
        """Parse the template.

        :rtype: str | None

        """
        template = self.get_template()

        if self.parser == self.PARSER_SIMPLE:
            content = read_file(template)
            for key, value in self.context.items():
                replace = "$%s$" % key
                content = content.replace(replace, str(value))

            return content

        try:
            return parse_jinja_template(template, self.context)
        except TemplateNotFound:
            log.error("Template not found: %s" % template)
            return None
        except TemplateError as e:
            log.error("Could not parse %s template: %s" % (template, e))
            return None

    def get_statement(self, cd=False, suppress_comment=False):
        """Override to get the statement based on the parser."""
        if self.parser == self.PARSER_JINJA:
            return self._get_jinja2_statement(cd=cd).statement
        elif self.parser == self.PARSER_SIMPLE:
            return self._get_simple_statement(cd=cd).statement
        else:
            log.error("Unknown or unsupported template parser: %s" % self.parser)
            return None

    def get_template(self):
        """Get the template path.

        :rtype: str

        """
        source = self.source
        for location in self.locations:
            _source = os.path.join(location, self.source)
            if os.path.exists(_source):
                return _source

        return source

    def _get_command(self, content):
        """Get the cat command."""
        output = list()

        # TODO: Template backup is not system safe, but is specific to bash.
        if self.backup_enabled:
            output.append('if [[ -f "%s" ]]; then mv %s %s.b; fi;' % (self.target, self.target, self.target))

        if content.startswith("#!"):
            _content = content.split("\n")
            first_line = _content.pop(0)
            output.append('echo "%s" > %s' % (first_line, self.target))
            output.append("cat >> %s << EOF" % self.target)
            output.append("\n".join(_content))
            output.append("EOF")
        else:
            output.append("cat > %s << EOF" % self.target)
            output.append(content)
            output.append("EOF")

        statement = "\n".join(output)

        return Command(statement, **self._kwargs)

        # # BUG: This still does not seem to work, possibly because a shell script includes EOF? The work around is to use
        # # get_content(), self.target, and write the file manually.
        # if self.line_by_line:
        #     a = list()
        #     a.append('touch %s' % self.target)
        #     for i in content.split("\n"):
        #         i = i.replace('"', r'\"')
        #         a.append('echo "%s" >> %s' % (i, self.target))
        #
        #     output.append("\n".join(a))
        # elif self.pythonic:
        #     target_file = File(self.target)
        #     script_file = "write_%s_template.py" % target_file.name.replace("-", "_")
        #
        #     a = list()
        #     a.append('content = """%s' % content)
        #     a.append('"""')
        #     a.append("")
        #     a.append('with open("%s", "w") as f:' % self.target)
        #     a.append('    f.write(content)')
        #     a.append('    f.close()')
        #     a.append('')
        #     output.append('cat > %s <<EOF' % script_file)
        #     output.append("\n".join(a))
        #     output.append('EOF')
        #     output.append("")
        #     output.append("rm %s" % script_file)
        # else:
        #     output.append("cat > %s << EOF" % self.target)
        #     output.append(content)
        #     output.append("EOF")
        #
        # statement = "\n".join(output)
        # return Command(statement, **self._kwargs)

    # noinspection PyUnusedLocal
    def _get_jinja2_statement(self, cd=False):
        """Parse a Jinja2 template."""
        content = self.get_content()
        return self._get_command(content)

    # noinspection PyUnusedLocal
    def _get_simple_statement(self, cd=False):
        """Parse a "simple" template."""
        content = self.get_content()

        return self._get_command(content)
