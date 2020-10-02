# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['orchid_python_api']

package_data = \
{'': ['*'], 'orchid_python_api': ['examples/*']}

install_requires = \
['deal==3.9.0',
 'matplotlib==3.3.0',
 'numpy==1.19.0',
 'pandas==1.0.5',
 'python-dateutil==2.8.1',
 'pythonnet==2.5.1',
 'pyyaml==5.3.1',
 'seaborn==0.10.1',
 'toolz==0.10.0',
 'typing-extensions==3.7.4.2']

entry_points = \
{'console_scripts': ['copy_orchid_examples = copy_orchid_examples:main',
                     'use_orchid_test_data = use_orchid_test_data:main']}

setup_kwargs = {
    'name': 'orchid-python-api',
    'version': '2020.4.232',
    'description': 'Defines and implements the Python API for Orchid*. (*Orchid is a mark of Reveal Energy Services, Inc.)',
    'long_description': '# Introduction \n\nThis project defines the implementation of the Python API for Orchid*.\n\n(*Orchid in a mark of Revel Energy Services. Inc.)\n\nSpecifically, the `orchid` package exposes the Orchid API to Python applications and the Python REPL.\n\n# Getting Started\n\n## Create a virtual environment\n\n# Examples\n\nAdditionally, this project installs four examples in the `examples` directory of the `orchid-python-api`\npackage:\n\n- `plot_trajectories.ipynb`\n- `plot_monitor_curves.ipynb`\n- `plot_treatment.ipynb`\n- `completion_analysis.ipynb`\n\nThe first three notebooks plot:\n\n- The well trajectories for a project\n- The monitor curves for a project\n- The treatment curves (pressure, slurry rate and concentration) for a specific stage of a well in a project\n \nAdditionally, the notebook, `completion_analysis.ipynb`, provides a more detailed analysis of the completion\nperformed on two different wells in a project.\n \nTo use these examples, you may want to invoke the commands\n\n- `copy_orchid_examples`\n- `use_orchid_test_data`\n\nUse the first command to copy the example files into your an optionally specified (virtual environment)\ndirectory. (The default destination is your current working directory.) Use the second command to change the\nexamples in an optionally specified directory (your current directory) to refer to the specified location of \nthe Orchid test data files. Both commands are \n    - Command line commands that run in a console / terminal\n    - Support a help flag (`-h` / `--help`) to provide you with help on running the commands\n\n\n## End-user preparation\n\nWe recommend the use of virtual environments to use the Orchid Python API. This choice avoids putting \nOrchid-specific-packages in your system Python environment.\n\nYou have several options to create and manage virtual environments: `venv`, `pipenv`, `poetry`, and `conda`.\nThe `venv ` is available as a standard Python package and is a spartan tool to manage environments. `poetry`\nis a tool targeting developers but can be used by end-users. Our recommended tool is `pipenv`. It provides a \ngood balance between `venv ` and `poetry`. Remember, both `pipenv` and `poetry` must be installed in your \nPython environment separately from Python itself, but can be installed using `pip`. Finally, `conda` supports \nthe creation of virtual environments, but assumes that you have installed a Python distribution using Anaconda\nor miniconda. We will not describe `conda` further.\n\nUsing any of `pipenv`, `venv` or `poetry`, your first step is to create a directory for *your* project. Then, \nchange into *your* project directory.\n\nWe recommend the use of `pipenv`. This environment hides a number of details involved in managing a virtualenv\nand yet provides a fairly simple interface. We will assume in this document that you are using `pipenv`.\n\n# Step-by-step install\n\n- Install python 3.7 by following [these instructions](https://docs.python.org/3/using/windows.html). To \n  ensure access from the command line, be sure to select the "Add Python 3.x to PATH" option on the\n  [installer start page](https://docs.python.org/3/_images/win_installer.png). \n- Installing `pipenv` by following the \n  [install documentation](https://pipenv.pypa.io/en/latest/install/#installing-pipenv).\n- Open a console using either `powershell` or the Windows console.\n- Create a directory for the virtual environment. We will symbolically call it `/path/to/orchid-virtualenv`.\n- Change the current working directory to by `chdir /path/to/orchid-virtualenv`.\n- Create an empty virtual environment by running `pipenv install`.\n- Activate the virtual environment by running `pipenv shell`\n- Install orchid by running `pip install orchid-python-api`.\n- Optionally install jupyter lab or jupyter notebook if you wish to use these tools to explore.\n\n# Verify installation\n\n## Jupyter lab\n\n- In your activated virtual environment, run `jupyter lab` to open a browser tab.\n- In the first cell, enter `import orchid`.\n- Run the cell.\n- Wait patiently.\n\nThe import should complete with no errors.\n\n## Python REPL\n\n- In your activated virtual environment, run `python` to open a REPL.\n- Enter `import orchid`.\n- Wait patiently.\n\nThe import should complete with no errors.\n\n# Run orchid examples\n\n- Navigate to the directory associated with the virtual environment\n- Run `python </path/to/virtualenv/Lib/site-packages/copy_orchid_examples.py`\n- If the script reports that it skipped notebooks, repeat the command with an additional argument:  \n  `python </path/to/virtualenv/Lib/site-packages/copy_orchid_examples.py --overwrite`\n- Verify that the current directory has four notebooks:\n    - `plot_trajectories.ipynb`\n    - `plot_monitor_curves.ipynb`\n    - `plot_treatment.ipynb`\n    - `completion_analysis.ipynb`\n- The notebooks, as installed, contain a symbolic reference to the Orchid training data. Change this\n  symbolic reference to an actual reference by:\n    - Either running \n      `python </path/to/virtualenv/Lib/site-packages/use_orchid_test_data.py </path/to/training-data>`\n    - Or by editing each notebook replacing the symbolic strings, "/path/to", with a concrete path to\n      your installed training data.\n- Activate your virtual environment by `pipenv shell` if not already activated\n- Open Jupyter by running `jupyter lab` in the shell\n- Within Jupyter,\n    Run the notebook, `plot_trajectories.ipynb`\n        1. Open notebook\n        2. Run all cells of notebook\n        3. Wait patiently\n        4. Verify that no exceptions occurred\n    - Repeat for remaining notebooks:\n        - `plot_monitor_curves.ipynb`\n        - `plot_treatment.ipynb`\n        - `completion_analysis.ipynb`\n',
    'author': 'Reveal Energy Services, Inc.',
    'author_email': 'support@reveal-energy.com',
    'maintainer': 'Reveal Energy Services, Inc.',
    'maintainer_email': 'support@reveal-energy.com',
    'url': 'https://github.com/Reveal-Energy-Services/orchid-python-api',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
