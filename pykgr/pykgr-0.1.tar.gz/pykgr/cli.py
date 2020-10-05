import os
from pykgr import config

def arguments(ap):
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--package-module", "-pm", help="Append module folder to package search path")
    ap.add_argument("--package-file", "-p", help="Pass a .py file containing a pykgr class")
    return ap.parse_args()

def initialize(conf):
    for d in [conf.main_directory, conf.source_directory, conf.source_tarballs_directory]:
        if not os.path.exists(d):
            os.mkdir(d)

def setup_paths(args):
    python_path = os.environ.get('PYTHONPATH')
    if not python_path:
        python_path = ""

    python_path = "%s:%s" % (args.package_module, python_path)
    if config.local_package_module:
        python_path = "%s:%s" % ("%s:%s" % (args.package_module, python_path), python_path)

    os.environ['PYTHONPATH'] = python_path