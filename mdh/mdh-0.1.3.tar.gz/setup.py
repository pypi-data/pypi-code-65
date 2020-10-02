# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mdh']

package_data = \
{'': ['*']}

install_requires = \
['attrs', 'colorama', 'numpy>=1.9', 'scipy>=1.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata']}

setup_kwargs = {
    'name': 'mdh',
    'version': '0.1.3',
    'description': 'modified dh',
    'long_description': '# Modified Denavit–Hartenberg (mdh)\n\n[![Actions Status](https://github.com/MultipedRobotics/dh/workflows/CheckPackage/badge.svg)](https://github.com/MultipedRobotics/dh/actions)\n![GitHub](https://img.shields.io/github/license/multipedrobotics/dh)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/mdh)\n![PyPI](https://img.shields.io/pypi/v/mdh)\n\n\n<img src="https://upload.wikimedia.org/wikipedia/commons/d/d8/DHParameter.png" width="600px">\n\n[Modified Denavit-Hartenberg parameters](https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters#Modified_DH_parameters)\n\n**Work in progress, use one the other libraries below (Inspiration)**\n\nBuild kinematic chains using the modified Denavit-Hartenberg paramters\n\n- d: offset along previous z to the common normal\n- theta: angle about previous z, from old x to new x\n- a: length of the common normal, assuming a revolute joint, this is the radius about previous z.\n- alpha: angle about common normal, from old z axis to new z axis\n\n## Inspiration\n\nYou should probably use one of these, they inspired me to write a simpler\nmodule for my needs:\n\n- [pybotics](https://github.com/nnadeau/pybotics)\n- [pytransform3d](https://github.com/rock-learning/pytransform3d), some matplotlib 3d examples\n- [robopy](https://github.com/adityadua24/robopy), has some good matplotlib 3d examples, but seems rather brittle and difficult to work with\n- [tinyik](https://github.com/lanius/tinyik), uses `open3d` to visualize the mechanism\n\n## Example\n\n```python\nimport numpy as np\nfrom mdh.kinematic_chain import KinematicChain\nfrom mdh import UnReachable # exception\n\n# make it print better\nnp.set_printoptions(suppress=True)\n\n# modified DH parameters: alpha a theta d\n# types: revolute=1, prismatic=2 (not implemented yet)\ndh = [\n    {\'alpha\': 0,  \'a\': 0, \'theta\': 0, \'d\': 0, \'type\': 1},\n    {\'alpha\': pi/2, \'a\': 52, \'theta\': 0, \'d\': 0, \'type\': 1},\n    {\'alpha\': 0, \'a\': 89, \'theta\': 0, \'d\': 0, \'type\': 1},\n    {\'alpha\': 0, \'a\': 90, \'theta\': 0, \'d\': 0, \'type\': 1},\n    {\'alpha\': 0, \'a\': 95, \'theta\': 0, \'d\': 0, \'type\': 1}\n]\n\nkc = KinematicChain.from_parameters(dh)\n\n# forward kinematics\nangles = np.deg2rad([-45.00, 77.41, -98.15, -69.27, 0])\nt = kc.forward(angles)\nprint(f">> {t}")\n\n# inverse kinematics\npt = [110,0,-70]\ndeg = kc.inverse(pt)\nrad = np.rad2deg(deg)\nprint(f">> {rad}")\n```\n\n# MIT License\n\n**Copyright (c) 2019 Kevin J. Walchko**\n\nPermission is hereby granted, free of charge, to any person obtaining a copy\nof this software and associated documentation files (the "Software"), to deal\nin the Software without restriction, including without limitation the rights\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell\ncopies of the Software, and to permit persons to whom the Software is\nfurnished to do so, subject to the following conditions:\n\nThe above copyright notice and this permission notice shall be included in all\ncopies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE\nSOFTWARE.\n',
    'author': 'walchko',
    'author_email': 'walchko@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/mdh/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
