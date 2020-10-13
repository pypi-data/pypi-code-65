import sys

import pypigeonhole_build.pip_translator as pip_translator
from pypigeonhole_build.dependency import Dependency, INSTALL, DEV, PIP

import pypigeonhole_build.conda_translator as conda_translator
from pypigeonhole_build.conda_translator import CONDA

import pypigeonhole_build.app_setup as app_setup

# ##############################################################################
# These are application specific information. We leave some flexibility here
# for further customization. Don't want to tie the knots too much.
# This file is used by setup.py for users and conda env setup script for dev.
# ##############################################################################
__python_version = 'py390'  # take 3 digits, major, minor, patch

CONDA.env = __python_version + '_' + app_setup.get_top_pkg()
CONDA.channels = ['defaults']  # update channels, if needed.

_dependent_libs = [
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

# used by setup.py, hide details - how we compute these values.
install_required = pip_translator.get_install_required(_dependent_libs)

test_required = pip_translator.get_test_required(_dependent_libs)

python_required = pip_translator.get_python_requires(_dependent_libs)

# we can't abstract this out since it knows pip and conda, maybe more tools
# later on, such as poetry.
if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError('need to pass in parameters: pip, conda, conda_env, etc')

    # scripts use these
    if sys.argv[1] == 'pip':
        pip_translator.gen_req_txt(_dependent_libs, 'requirements.txt')
    elif sys.argv[1] == 'conda':
        conda_translator.gen_conda_yaml(_dependent_libs, 'environment.yaml')
    elif sys.argv[1] == 'conda_env':
        print(CONDA.env)
    else:
        raise ValueError(f'unknown parameter {sys.argv[1]}')
