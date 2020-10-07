from .magic import line_magic, arg
from ..output import Output

from iot_device import Config    # pylint: disable=import-error
import shlex


@line_magic
def rlist_magic(kernel, _):
    "List files on microcontroller"
    with kernel.device as repl:
        repl.rlist(Output(kernel))

@arg('-p', '--projects', nargs='*', default=None, help="host projects, defaults to specifiation in hosts.py")
@line_magic
def rdiff_magic(kernel, args):
    "Show differences between microcontroller and host directories"
    projects = args.projects
    if not projects: projects = kernel.device.projects
    with kernel.device as repl:
        repl.rsync(Output(kernel), path='/', projects=projects, dry_run=True)


@arg('-p', '--projects', nargs='*', default=None, help="host projects, defaults to specifiation in hosts.py")
@line_magic
def rsync_magic(kernel, args):
    """Synchronize microcontroller to host directories
Adds files on host but not on microcontroller, updates changed files, and deletes
files on microcontroller but not on hosts. Ignores files starting with a period.

On the host, files are organized into projects (subfolders of $host_dir). Projects
for each microcontroller are specified in $host_dir/base/hosts.py or the -p option.

%rsync synchronizes the time on the microcontroller if they differ to ensure correct updates.

CircuitPython: By default, CircuitPython disables writing to the 
               microcontroller filesystem. To enable, add the line 

                   storage.remount("/", readonly=False)" 
                   
               to boot.py.
"""
    projects = args.projects
    if not projects: projects = kernel.device.projects
    with kernel.device as repl:            
        repl.rsync(Output(kernel), path='/', projects=projects, dry_run=False)
