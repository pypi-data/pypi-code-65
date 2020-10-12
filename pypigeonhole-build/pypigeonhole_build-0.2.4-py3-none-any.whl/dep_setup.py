import sys
import os

import pypigeonhole_build.pip_dep_utils as pip_dep_utils
from pypigeonhole_build.pip_dep_utils import INSTALL, DEV, PIP, Dependency

import pypigeonhole_build.conda_dep_utils as conda_dep_utils
from pypigeonhole_build.conda_dep_utils import CONDA

curr_dir = os.path.dirname(os.path.realpath(__file__))
# go 2 levels above, parent(top package), "src", to the project folder
proj_dir = os.path.dirname(os.path.dirname(curr_dir))
app_name = os.path.basename(proj_dir)
top_pkg = app_name.replace('-', '_')

# ##############################################################################
# These are application specific information
# ##############################################################################
python_version = 'py390'  # take 3 digits, major, minor, patch

# release script is looking for this pattern: app_version =
# so don't use this pattern else where. we should have 2 assignment anyway.
app_version = "0.2.4"  # follow same style, 3 digits, major, minor, patch

CONDA.env = python_version + '_' + top_pkg
CONDA.channels = ['defaults']  # update channels, if needed.

dependent_libs = [
    Dependency(name='python', version='>=3.6', scope=INSTALL, installer=CONDA),
    Dependency(name='pip', installer=CONDA),  # Without this Conda complains
    Dependency(name='coverage', version='==5.3', installer=CONDA, desc='test coverage'),  # DEV
    Dependency(name='pipdeptree', scope=DEV, installer=PIP),
    Dependency(name='coverage-badge'),  # default to DEV and PIP automatically.
    Dependency(name='twine'),  # uploading to pypi
    Dependency(name='conda-build', installer=CONDA),
    Dependency(name='conda-verify', installer=CONDA),
    Dependency(name='anaconda-client', installer=CONDA),
]

# ##############################################################################
# No need to change below, unless you want to customize
# ##############################################################################

install_required = pip_dep_utils.get_install_required(dependent_libs)

test_required = pip_dep_utils.get_test_required(dependent_libs)

python_requires = pip_dep_utils.get_python_requires(dependent_libs)

# we can't abstract this out since it knows pip and conda, maybe more later on.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError('need to pass in parameters: pip, conda, conda_env')

    if sys.argv[1] == 'pip':
        pip_dep_utils.gen_req_txt(dependent_libs, 'requirements.txt')
    elif sys.argv[1] == 'conda':
        conda_dep_utils.gen_conda_yaml(dependent_libs, 'environment.yaml')
    elif sys.argv[1] == 'conda_env':
        print(CONDA.env)
    else:
        raise ValueError(f'unknown parameter {sys.argv[1]}')
