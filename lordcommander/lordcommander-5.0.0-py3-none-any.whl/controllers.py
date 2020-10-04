"""
---------------------------------------------------------------------
controllers.py
---------------------------------------------------------------------
This control module holds all of the controllers. There are three
controller classes defined in this file. The DirectoryController
is responsible for performing all of the directory related tasks
as its name suggests. The CommandController class runs the passed
command throughout the saved directories using saved credentials.
And the ProjectController class manipulates all project related
tasks like setting active project and adding new projects.

Version: 5.x
License: GNU General Public License 3
"""

import os
from pathlib import Path

from colr import color

from lordcommander.lcex import *
from lordcommander.output import Output


class DirectoryController:
    """
    Add, view, or delete directories/instances.
    """
    
    def __init__(self, instances):
        # instances is a list of module where all directory names are listed.
        self._instances = instances
    
    def add(self, *args):
        """
        Add directories/instances to the existing list or create a new list.
        :param args: Names of directories
        """
        try:
            if len(args) <= 0:
                raise ArgumentNotProvidedException(
                    "Aborting! No argument has been provided.")
            if self._instances is None:
                raise ActiveProjectNotSetException(
                    "May be no active project has been set. Please check.")
            
            # Process passed arguments
            directories = list(
                (filter(lambda dir: isinstance(dir, str), args)))
            
            # Append new directories to the list, no redundant value will exist
            self._instances.extend(
                [ins for ins in directories if ins not in self._instances])
        
        except ArgumentNotProvidedException as error:
            Output.danger(error)
        except ActiveProjectNotSetException as error:
            Output.danger(error)
        else:
            Output.success('Success!')
            self.view()
    
    def view(self, sort=False):
        """
        View list of added directories/instances in current active project.
        :param sort: Sort alphabetically, false by default (optional)
        """
        try:
            if self._instances is None:
                raise ActiveProjectNotSetException(
                    "May be no active project has been set. Please check.")
            
            Output.info('Listing directories...')
            directories = self._instances.copy()
            for directory in sorted(directories) if sort else directories:
                print("- {} ({})".format(directory, directories.index(directory)))
            print("\n")
            Output.normal("Total %d directories listed." % len(directories))
        except ActiveProjectNotSetException as error:
            Output.danger(error)
    
    def clear(self, *args, full=False):
        """
        Clears entire list or specified directories/instances from the active project instance list.
        :param args: Names of directories/instances
        :param full: If true, clears entire list. False by default (optional)
        """
        try:
            if len(args) <= 0 and not full:
                raise ArgumentNotProvidedException(
                    "Aborting! No argument has been provided.")
            
            if self._instances is None:
                raise ActiveProjectNotSetException(
                    "May be no active project has been set. Please check.")
            
            # If flag full is true, remove entire list
            if full:
                # Ask for confirmation
                Output.warning(
                    "This will clear the entire list, are you sure? (yes/no) [no]:")
                yes = {'yes', 'y'}
                decision = input(">> ")
                if decision not in yes:
                    raise KeyboardInterrupt("Aborted! Nothing is changed.")
                else:
                    self._instances.clear()
                    Output.success('Directory list cleared!')
                    return
            
            # Else remove specified keys only
            keys = set(filter(lambda dir: type(dir) is str, args))
            for key in keys:
                # Skip if a specified key is not in the list
                if key not in self._instances:
                    Output.danger(
                        f"{key} is not found in the list! Skipping...")
                    continue
                
                Output.warning(f"Removing {key}...")
                self._instances.remove(key)
                Output.success('Success!')
            self.view()
        
        except ArgumentNotProvidedException as error:
            Output.danger(error)
        except ActiveProjectNotSetException as error:
            Output.danger(error)
        except KeyboardInterrupt as error:
            Output.danger(error)


class CommandController:
    """
    Stirs the command executor.
    """
    
    def _get_instances(self, project, li, ui, ex, inc):
        """First, apply li and ui to slice instances/directories,
        then filter out by excluding according to ex or
        including according to inc"""
        if inc == ():
            return [ins for ins in project['instances'][li:ui]
                    if project['instances'].index(ins) not in ex]
        else:
            return [ins for ins in project['instances'][li:ui]
                    if project['instances'].index(ins) in inc]
    
    def run(self, project, cmd, li=0, ui=None, ex=(), inc=()):
        """
        Run the command.
        :param project: The active project dictionary
        :param cmd: The command to run
        :param li: Lower index (optional)
        :param ui: Upper index (optional)
        :param ex: Tuple of indices to exclude during execution (optional)
        :param inc: Tuple of indices to include only during execution (optional)
        """
        try:
            succeeded = 0
            failed = 0
            instance_root = Path(project['root'])
            instances = self._get_instances(project, li, ui, ex, inc)
            if len(instances) <= 0:
                Output.danger("No instances has been found in the list.")
            
            for instance in instances:
                # If a directory is missing, tell the user
                if not os.path.exists(instance_root.joinpath(instance)):
                    print("\n")
                    Output.write([
                        {'text': 'Directory', 'code': Output.DANGER},
                        {'text': f"'{instance}'", 'code': Output.WARNING},
                        {'text': 'is not found! Skipping...',
                         'code': Output.DANGER}
                    ])
                    failed += 1
                    continue
                
                # Omit if not a directory
                if not os.path.isdir(instance_root.joinpath(instance)):
                    print("\n")
                    Output.write([
                        {'text': f"'{instance}'", 'code': Output.WARNING},
                        {'text': 'is not a instance. Skipping...',
                         'code': Output.INFO}
                    ])
                    failed += 1
                    continue
                
                self.execute(cmd, instance_root.joinpath(instance))
                succeeded += 1
        
        except TypeError:
            Output.danger("Please provide valid integers!")
        finally:
            # Show the statistics
            Output.write([
                {'text': f"\nSuccessful run:", 'code': ''},
                {'text': succeeded, 'code': Output.SUCCESS},
                {'text': f"\nFailed run:", 'code': ''},
                {'text': failed, 'code': Output.DANGER}
            ])
    
    def execute(self, cmd, instance_path):
        """
        Execute the command to the specified directory.
        :param cmd: The command to run
        :param instance_path: Path where the command should execute
        """
        try:
            print('\n')
            Output.write([
                {'text': 'Changed directory to',
                 'code': Output.INFO},
                {'text': f"'{instance_path}'",
                 'code': Output.WARNING},
                {'text': "and running", 'code': Output.INFO},
                {'text': f"'{cmd}'", 'code': Output.WARNING}
            ])
            # Switch to the desired directory
            os.chdir(instance_path)
            # Do the mischief
            os.system(cmd)
        except OSError as error:
            # If something goes wrong...
            Output.danger(error)


class ProjectController:
    """
    Add, view, or delete projects and set active project.
    """
    
    def __init__(self, lcdb):
        self._lcdb = lcdb
    
    def active(self, project):
        """
        Set active project.
        :param project: Name of the project
        """
        try:
            if project not in self._lcdb['projects'].keys() or len(self._lcdb['projects']) <= 0:
                raise ProjectNotFoundException(
                    "Project %s is not found in the list, to see available projects run 'proj view'." % project)
            
            self._lcdb['active'] = project
            Output.success("%s is set as active project." % project)
        except ProjectNotFoundException as error:
            Output.danger(error)
    
    def add(self, strpath, name=None):
        """
        Add new project.
        :param strpath: The absolute path to the project
        :param name: The name of the project, if not specified, it will be taken from path
        """
        try:
            if not os.path.isabs(strpath):
                raise NotAnAbsolutePathException(
                    "Invalid path, it should be absolute.")
            
            if not os.path.exists(strpath):
                raise FileNotFoundError(
                    "Provided path does not exist, please enter a valid path.")
            
            path = Path(strpath)
            project_name = name if name else path.stem
            # Exit if already exists
            if project_name in self._lcdb['projects'].keys():
                Output.danger("Project already exists!")
                return

            # Add project with default structure
            data = {
                'root': str(path),
                'instances': []
            }
            self._lcdb['projects'][project_name] = data
            Output.success("%s is added to project list." % project_name)
        
        except NotAnAbsolutePathException as error:
            Output.danger(error)
        except FileNotFoundError as error:
            Output.danger(error)
    
    def view(self):
        """
        View list of added projects. Active project will be checked.
        """
        try:
            projects = list(self._lcdb['projects'].keys())
            
            if len(projects) <= 0:
                raise ProjectNotFoundException(
                    "No project has been found in the list.")
            
            Output.info('Listing projects...')
            for project in projects:
                root = self._lcdb['projects'][project]['root']
                Output.write("[%s] %s: %s" %
                             ('✓' if project == self._lcdb['active'] else ' ', project, color(root, Output.MUTED)))
            Output.normal("\nTotal %d projects listed." % len(projects))
        
        except ProjectNotFoundException as error:
            Output.danger(error)
    
    def clear(self, key):
        """
        Remove a project along with it's instances from the list.
        :param key: The name of the project
        """
        try:
            if key not in self._lcdb['projects'].keys():
                raise ProjectNotFoundException(
                    'Project is not found in the list.')
            
            # Ask for confirmation
            Output.warning(
                "Caution! This cannot be undone. Do you want to proceed? (yes/no)[no]:")
            yes = {'yes', 'y'}
            decision = input(">> ")
            if decision not in yes:
                raise KeyboardInterrupt("Aborted! Nothing is changed.")
            
            # If the key is the active project, set active project empty
            if key == self._lcdb['active']:
                self._lcdb['active'] = ''
            
            del self._lcdb['projects'][key]
            Output.success("%s is removed from LordCommander." % key)
        
        except ProjectNotFoundException as error:
            Output.danger(error)
        except KeyboardInterrupt as error:
            Output.danger(error)
            
    def rename(self, oldname, newname):
        """
        Rename an existing project.
        :param oldname: Current name of the project
        :param newname: New name of the project
        """
        try:
            if oldname not in self._lcdb['projects'].keys():
                raise ProjectNotFoundException(
                    'Project is not found in the list.')
            
            self._lcdb['projects'][newname] = self._lcdb['projects'][oldname]
            del self._lcdb['projects'][oldname]
            
            if oldname == self._lcdb['active']:
                self._lcdb['active'] = newname
            Output.success("Project %s is renamed to %s." % (oldname, newname))
        except ProjectNotFoundException as error:
            Output.danger(error)
