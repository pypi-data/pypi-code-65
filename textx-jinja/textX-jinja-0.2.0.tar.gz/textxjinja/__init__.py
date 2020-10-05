import os
import re
import shutil
import click
from jinja2 import Environment, FileSystemLoader


__version__ = "0.2.0"


# Compatibility with Python 2.7
try:
    FileExistsError
except NameError:
    FileExistsError = OSError

placeholder_re = re.compile(r'__[^_]\w+?[^_]__')


class SkipFile(Exception):
    pass


class FileCount:
    def __init__(self):
        self.created = 0
        self.overwritten = 0
        self.skipped = 0

    def __str__(self):
        return '{}/{}/{}'.format(self.created, self.overwritten, self.skipped)


def textx_jinja_generator(templates_path, target_path, config, overwrite=False,
                          filters=None):
    """
    Generates a set of files using Jinja templates.
    """

    """
    Args:
        templates_path (str): A path to templates.
        target_path (str): The path where files should be generated.
        config (dict): A config contains any data necessary
            for rendering files using Jinja engine.
        overwrite (bool): If the target files should be overwritten.
        filters(dict): Optional Jinja filters.
    """
    def eval_file_name(file_name):
        """
        Replaces all `__<var>__` if `var` is in config dict.
        Strips .jinja extension.
        Raises SkipFile if file shouldn't be processed.
        """
        # Replace placeholders in the target file name.
        placeholders = placeholder_re.findall(file_name)

        for placeholder in placeholders:
            ph_value = config.get(placeholder.strip('_'))
            if ph_value is False:
                raise SkipFile
            elif ph_value is True:
                file_name = file_name.replace(placeholder, '')
            elif ph_value is not None:
                file_name = file_name.replace(placeholder, ph_value)

        if file_name.endswith('.jinja'):
            file_name = '.'.join(file_name.split('.')[:-1])
        return file_name

    def generate_file(src_rel_file, src_file, target_file):
        """
        Generate a single target file from the given source file.
        """
        if overwrite or not os.path.exists(target_file):

            if os.path.exists(target_file):
                click.echo('Overwriting {}'.format(target_file))
                file_count.overwritten += 1
            else:
                click.echo('Creating {}'.format(target_file))
                file_count.created += 1

            if src_file.endswith('.jinja'):
                # Render using Jinja template
                with open(target_file, 'w') as f:
                    f.write(
                        env.get_template(src_rel_file).render(**config))
            else:
                # Just copy
                if not src_file == target_file:
                    shutil.copy(src_file, target_file)

        else:
            click.echo('Skipping {}'.format(target_file))
            file_count.skipped += 1

    file_count = FileCount()

    if os.path.isfile(templates_path):
        search_path = os.path.dirname(templates_path)
        env = Environment(loader=FileSystemLoader(searchpath=search_path),
                          trim_blocks=True, lstrip_blocks=True)
        if filters:
            env.filters.update(filters)

        src_file = templates_path
        src_rel_file = os.path.basename(templates_path)

        try:
            if not os.path.isdir(target_path):
                target_file = eval_file_name(target_path)
            else:
                target_file = os.path.join(target_path, eval_file_name(src_rel_file))
            generate_file(src_rel_file, src_file, target_file)
        except SkipFile:
            click.echo("\nFile skipped due to configuration.")
    else:
        search_path = templates_path
        env = Environment(loader=FileSystemLoader(searchpath=search_path),
                          trim_blocks=True, lstrip_blocks=True)
        if filters:
            env.filters.update(filters)

        click.echo("\nStarted generating files in {}".format(target_path))
        for root, dirs, files in os.walk(templates_path):
            for f in files:
                src_file = os.path.join(root, f)
                src_rel_file = os.path.relpath(src_file, templates_path)
                target_file = os.path.join(target_path, src_rel_file)

                try:
                    # Replace placeholders in the target file name.
                    target_file = eval_file_name(target_file)
                except SkipFile:
                    continue

                # Create necessary folders.
                try:
                    os.makedirs(os.path.dirname(target_file))
                except FileExistsError:
                    pass

                generate_file(src_rel_file, src_file, target_file)

    click.echo('Done. Files created/overwritten/skipped = {}'
               .format(file_count))
