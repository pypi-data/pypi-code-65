"""
Generate a reference project
"""

import argparse
import os
import logging

from k3project_generator.genproject import create_reference_project, LICENSES
from k3project_generator.main import set_log_parser_args, eval_log_parser_args
import sys

logger = logging.getLogger(__name__)

__author__ = 'Joachim Kestner <joachim.kestner@khoch3.de>'
__version__ = 0.3

_FILE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
# 
# def render_md(fileNm):
#     renderer = consolemd.Renderer()
#     with open(fileNm) as fh:
#         renderer.render( fh.read())

def main():
    parser = argparse.ArgumentParser(description=__doc__+"\n\nAuthor: {}\nVersion: {}".format(__author__,__version__), formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-l", "--licence", default="MIT", choices=LICENSES+["None"], help="The licente to initialise the project with. Default: MIT")
    parser.add_argument("-d", "--target_directory", default=".", help="Creates the reference project with the given directory. Default: cwd")
    parser.add_argument("project_name", help="the name of the project")
    
    set_log_parser_args(parser)
    
    args = parser.parse_args()
    eval_log_parser_args(args)
    try:
        tarDir = os.path.abspath(os.path.join(os.getcwd(), args.target_directory))
        if not os.path.isdir(tarDir):
            logger.error("Invalid argument given with the option -d. Needs to be a directory that exists.")
            sys.exit(2)
        logger.info(f"Creating project '{args.project_name}' within {args.target_directory}")
        logger.debug(f"Full target project path: '{tarDir}'")
        if args.licence == "None":
            lic = None
        else:
            lic = args.licence
        create_reference_project(tarDir, args.project_name, lic)
        logger.info(f"Creating project '{args.project_name}' done")
    except Exception:
        logger.exception("Create reference project exited with exception")
        sys.exit(1)
        