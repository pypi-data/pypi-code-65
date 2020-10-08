"""
Collect dependencies
"""

import os
import re

import cioclarisse.utils as cu
import ix
from cioclarisse import frames_ui
from ciocore.gpath import Path
from ciocore.gpath_list import PathList
from ciocore.sequence import Sequence
from cioclarisse.utils import ConductorError

SCRIPTS_DIRECTORY = os.path.join(os.path.dirname(os.path.dirname(__file__)), "scripts")
 


# ciocnode: wrapper around cnode. Allows us to add flags and so on.

# cioprep.py: pre render script that operates in the Clarisse. Among other
# things, it removes drive letters on win.
CONDUCTOR_SCRIPTS = ["cioprep.py", "ciocnode"]

# clarisse.cfg: A copy of the users config file.
CLARISSE_CFG_FILENAME = "clarisse.cfg"

def system_dependencies():
    """
    Provides a list of system files to be sent to the render node.

    These will be copied to a directory in preparation for uploading.

    This is part of a strategy to satisfy 2 constraints.
    1. Dont store special logic on the sidecar.
    2. Don't make the render command un-runnable on the local machine.

    See docs in ciocnode and cioprep for more info.

    Returns:
        list: Each element is a source/destination pair of paths.
        [
            {"src": "/some/path.ext", "dest": "/other/path.ext"},
            ...
        ]
    """

    result = []

    conductor_tmp_dir = os.path.join(
        ix.application.get_factory().get_vars().get("CTEMP").get_string(), "conductor"
    )

    for script in CONDUCTOR_SCRIPTS:
        src_path = Path(os.path.join(SCRIPTS_DIRECTORY, script)).posix_path()
        dest_path = Path(os.path.join(conductor_tmp_dir, script)).posix_path()

        result.append({"src": src_path, "dest": dest_path})

    config_dir = (
        ix.application.get_factory()
        .get_vars()
        .get("CLARISSE_USER_CONFIG_DIR")
        .get_string()
    )

    config_src_file = Path(os.path.join(config_dir, CLARISSE_CFG_FILENAME)).posix_path()
    config_dest_file = Path(
        os.path.join(conductor_tmp_dir, CLARISSE_CFG_FILENAME)
    ).posix_path()

    result.append({"src": config_src_file, "dest": config_dest_file})

    return result


def _get_system_dependencies():
    """
    Extracts the destination side of system dependency files.

    Returns:
        PathList: list of system files to be uploaded
    """
    result = PathList()
    for entry in system_dependencies():
        try:
            result.add(entry["dest"])
        except ValueError as ex:
            msg = "{} - while resolving system_dependency: {}".format( str(ex), entry["dest"])
            raise ConductorError(msg)

    return result


def collect(obj, do_glob=True):
    """
    Collect ALL upload files in preparation for submission.

    Args:
        obj (ConductorJob): The item whose attributes define the scan.
    Returns:
        PathList: All file dependencies.
    """
 

    result = PathList()
    result.add(*_get_system_dependencies())
    result.add(*_get_extra_uploads(obj))
    result.add(*get_scan(obj))
    if do_glob:
        result.glob()
    return result


def _get_extra_uploads(obj):
    """
    Collects any files specified through the extra uploads window.

    They are stored in a list attribute on the ConductorJob item.

    Args:
        obj (ConductorJob): item being processed.

    Returns:
        PathList: Collected paths.
    """
    result = PathList()
    extras_attr = obj.get_attribute("extra_uploads")
    paths = ix.api.CoreStringArray()
    extras_attr.get_values(paths)
    for path in paths:
        try:
            result.add(path)
        except ValueError as ex:
            msg = "{} - while resolving extra upload path: {}".format(str(ex), path)
            raise ConductorError(msg)

    return result


def resolve_attr(attr):

    is_ex = attr.is_expression_enabled() and attr.is_expression_activated()
    original_value = attr.get_expression() if is_ex else  attr.get_string()
    modified_value = re.sub(  r"\$(\d?)F|#+|<UDIM>", "*",  original_value)
    if not is_ex:
        return modified_value

    # Its an active expression
    # Force the expression to evaluate correctly.

    attr.activate_expression(False)
    attr.set_string(modified_value)
    attr.activate_expression(True)

    resolved = attr.get_string()

    # return to orig expr
    attr.activate_expression(False)
    attr.set_string(original_value)
    attr.activate_expression(True)
    
    
    return resolved

def get_scan(obj):

    result = PathList()
    objects = ix.api.OfObjectSet()
    obj.gather_branch(objects)
    for o in objects:
        if o.is_disabled():
            continue
        for index in range(o.get_attribute_count()):
            attr =  o.get_attribute(index)
            hint = ix.api.OfAttr.get_visual_hint_name(attr.get_visual_hint())
            if hint in [ "VISUAL_HINT_FILENAME_OPEN" , "VISUAL_HINT_FOLDER" ] and not attr.get_name() == "filename_sys" :
                fn =   resolve_attr(attr) 
                if fn:
                    result.add(Path(fn)) 
                    
    return result
