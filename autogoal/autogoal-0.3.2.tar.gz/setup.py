# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['autogoal',
 'autogoal.contrib',
 'autogoal.contrib.gensim',
 'autogoal.contrib.keras',
 'autogoal.contrib.nltk',
 'autogoal.contrib.regex',
 'autogoal.contrib.sklearn',
 'autogoal.contrib.spacy',
 'autogoal.contrib.streamlit',
 'autogoal.contrib.telegram',
 'autogoal.contrib.torch',
 'autogoal.contrib.wikipedia',
 'autogoal.datasets',
 'autogoal.datasets.ehealthkd20',
 'autogoal.grammar',
 'autogoal.kb',
 'autogoal.ml',
 'autogoal.sampling',
 'autogoal.search',
 'autogoal.utils']

package_data = \
{'': ['*'], 'autogoal.datasets': ['data/.gitignore']}

install_requires = \
['black>=19.10b0,<20.0',
 'enlighten>=1.4.0,<2.0.0',
 'networkx>=2.4,<3.0',
 'numpy>=1.19.2,<2.0.0',
 'psutil>=5.6.7,<6.0.0',
 'pydot>=1.4.1,<2.0.0',
 'pyyaml>=5.2,<6.0',
 'scipy>=1.5.2,<2.0.0',
 'termcolor>=1.1.0,<2.0.0',
 'toml>=0.10.0,<0.11.0',
 'tqdm>=4.50.2,<5.0.0',
 'typer>=0.3.2,<0.4.0']

extras_require = \
{'contrib': ['gensim>=3.8.1,<4.0.0',
             'jupyterlab>=1.2.4,<2.0.0',
             'keras>=2.3.1,<3.0.0',
             'nltk>=3.4.5,<4.0.0',
             'nx_altair>=0.1.4,<0.2.0',
             'python-telegram-bot>=12.4.2,<13.0.0',
             'scikit-learn>=0.22,<0.23',
             'seqlearn>=0.2,<0.3',
             'sklearn_crfsuite>=0.3.6,<0.4.0',
             'spacy>=2.2.3,<3.0.0',
             'streamlit>=0.59.0,<0.60.0',
             'transformers>=2.3.0,<3.0.0',
             'wikipedia>=1.4.0,<2.0.0'],
 'dev': ['codecov>=2.0.15,<3.0.0',
         'markdown-include>=0.5.1,<0.6.0',
         'mkdocs>=1.0.4,<2.0.0',
         'mkdocs-material>=4.6.0,<5.0.0',
         'mypy>=0.761,<0.762',
         'pylint>=2.4.4,<3.0.0',
         'pytest>=5.3.2,<6.0.0',
         'pytest-cov>=2.8.1,<3.0.0'],
 'gensim': ['gensim>=3.8.1,<4.0.0'],
 'keras': ['keras>=2.3.1,<3.0.0'],
 'nltk': ['nltk>=3.4.5,<4.0.0'],
 'sklearn': ['scikit-learn>=0.22,<0.23',
             'seqlearn>=0.2,<0.3',
             'sklearn_crfsuite>=0.3.6,<0.4.0'],
 'spacy': ['spacy>=2.2.3,<3.0.0'],
 'streamlit': ['nx_altair>=0.1.4,<0.2.0', 'streamlit>=0.59.0,<0.60.0'],
 'telegram': ['python-telegram-bot>=12.4.2,<13.0.0'],
 'wikipedia': ['wikipedia>=1.4.0,<2.0.0']}

setup_kwargs = {
    'name': 'autogoal',
    'version': '0.3.2',
    'description': 'Automatic Generation Optimization And Learning',
    'long_description': '![AutoGOAL Logo](https://autogoal.github.io/autogoal-banner.png)\n\n[<img alt="PyPI" src="https://img.shields.io/pypi/v/autogoal">](https://pypi.org/project/autogoal/) [<img alt="PyPI - Python Version" src="https://img.shields.io/pypi/pyversions/autogoal">](https://pypi.org/project/autogoal/) [<img alt="PyPI - License" src="https://img.shields.io/pypi/l/autogoal">](https://autogoal.github.io/contributing) [<img alt="GitHub stars" src="https://img.shields.io/github/stars/autogoal/autogoal?style=social">](https://github.com/autogoal/autogoal/stargazers) [<img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/auto_goal?label=Followers&style=social">](https://twitter.com/auto_goal)\n\n[<img alt="GitHub Workflow Status (branch)" src="https://img.shields.io/github/workflow/status/autogoal/autogoal/CI/main?label=unit tests&logo=github">](https://github.com/autogoal/autogoal/actions)\n[<img src="https://codecov.io/gh/autogoal/autogoal/branch/main/graph/badge.svg" />](https://codecov.io/gh/autogoal/autogoal/)\n[<img alt="Docker Cloud Build Status" src="https://img.shields.io/docker/cloud/build/autogoal/autogoal">](https://hub.docker.com/r/autogoal/autogoal)\n[<img alt="Docker Image Size (CPU)" src="https://img.shields.io/docker/image-size/autogoal/autogoal/latest">](https://hub.docker.com/r/autogoal/autogoal)\n[<img alt="Docker Pulls" src="https://img.shields.io/docker/pulls/autogoal/autogoal">](https://hub.docker.com/r/autogoal/autogoal)\n\n# AutoGOAL\n\n> Automatic Generation, Optimization And Artificial Learning\n\nAutoGOAL is a Python library for automatically finding the best way to solve a given task.\nIt has been designed mainly for _Automated Machine Learning_ (aka [AutoML](https://www.automl.org))\nbut it can be used in any scenario where you have several possible ways to solve a given task.\n\nTechnically speaking, AutoGOAL is a framework for program synthesis, i.e., finding the best program to solve\na given problem, provided that the user can describe the space of all possible programs.\nAutoGOAL provides a set of low-level components to define different spaces and efficiently search in them.\nIn the specific context of machine learning, AutoGOAL also provides high-level components that can be used as a black-box in almost any type of problem and dataset format.\n\n## Quickstart\n\nAutoGOAL is first and foremost a framework for Automated Machine Learning.\nAs such, it comes pre-packaged with hundreds of low-level machine learning\nalgorithms that can be automatically assembled into pipelines for different problems.\n\nThe core of this functionality lies in the [`AutoML`](https://autogoal.github.io/api/autogoal.ml#automl) class.\n\nTo illustrate the simplicity of its use we will load a dataset and run an automatic classifier in it.\n\n```python\nfrom autogoal.datasets import cars\nfrom autogoal.ml import AutoML\n\nX, y = cars.load()\nautoml = AutoML()\nautoml.fit(X, y)\n```\n\nSensible defaults are defined for each of the many parameters of `AutoML`.\nMake sure to [read the documentation](https://autogoal.github.io/guide/) for more information.\n\n## Installation\n\nInstallation is very simple:\n\n    pip install autogoal\n\nHowever, `autogoal` comes with a bunch of optional dependencies. You can install them all with:\n\n    pip install autogoal[contrib]\n\nTo fine-pick which dependencies you want, read the [dependencies section](https://autogoal.github.io/dependencies/).\n\n### Using Docker \n\nThe easiest way to get AutoGOAL up and running with all the dependencies is to pull the development Docker image, which is somewhat big:\n\n    docker pull autogoal/autogoal\n\nInstructions for setting up Docker are available [here](https://www.docker.com/get-started).\n\nOnce you have the development image downloaded, you can fire up a console and use AutoGOAL interactively.\n\n![](https://autogoal.github.io/shell.svg)\n\n> **NOTE**: By installing through `pip` you will get the latest release version of AutoGOAL, while by installing through Docker, you will get the latest development version. The development version is mostly up-to-date with the `main` branch, hence it will probably contain more features, but also more bugs, than the release version.\n\n## CLI\n\nYou can use AutoGOAL directly from the CLI. To see options just type:\n\n    python -m autogoal\n\nRead more in the [CLI documentation](https://autogoal.github.io/cli).\n\n## Demo\n\nAn online demo app is available at [autogoal.github.io/demo](https://autogoal.github.io/demo).\nThis app showcases the main features of AutoGOAL in interactive case studies.\n\nTo run the demo locally, simply type:\n\n    docker run -p 8501:8501 autogoal/autogoal\n\nAnd navigate to [localhost:8501](http://localhost:8501).\n\n## Documentation\n\nThis documentation is available online at [autogoal.github.io](https://autogoal.github.io). Check the following sections:\n\n- [**User Guide**](https://autogoal.github.io/guide/): Step-by-step showcase of everything you need to know to use AuoGOAL.\n- [**Examples**](https://autogoal.github.io/examples/): The best way to learn how to use AutoGOAL by practice.\n- [**API**](https://autogoal.github.io/api/autogoal): Details about the public API for AutoGOAL.\n\nThe HTML version can be deployed offline by downloading the [AutoGOAL Docker image](https://hub.docker.com/autogoal/autogoal) and running:\n\n    docker run -p 8000:8000 autogoal/autogoal mkdocs serve -a 0.0.0.0:8000\n\nAnd navigating to [localhost:8000](http://localhost:8000).\n\n## Publications\n\nIf you use AutoGOAL in academic research, please cite the following paper:\n\n```bibtex\n@article{estevez2020general,\n  title={General-purpose hierarchical optimisation of machine learning pipelines with grammatical evolution},\n  author={Est{\\\'e}vez-Velarde, Suilan and Guti{\\\'e}rrez, Yoan and Almeida-Cruz, Yudivi{\\\'a}n and Montoyo, Andr{\\\'e}s},\n  journal={Information Sciences},\n  year={2020},\n  publisher={Elsevier},\n  doi={10.1016/j.ins.2020.07.035}\n}\n```\n\nThe technologies and theoretical results leading up to AutoGOAL have been presented at different venues:\n\n- [Optimizing Natural Language Processing Pipelines: Opinion Mining Case Study](https://link.springer.com/chapter/10.1007/978-3-030-33904-3_15) marks the inception of the idea of using evolutionary optimization with a probabilistic search space for pipeline optimization.\n\n- [AutoML Strategy Based on Grammatical Evolution: A Case Study about Knowledge Discovery from Text](https://www.aclweb.org/anthology/P19-1428/) applied probabilistic grammatical evolution with a custom-made grammar in the context of entity recognition in medical text.\n\n- [General-purpose Hierarchical Optimisation of Machine Learning Pipelines with Grammatical Evolution](https://doi.org/10.1016/j.ins.2020.07.035) presents a more uniform framework with different grammars in different problems, from tabular datasets to natural language processing.\n\n- [Solving Heterogeneous AutoML Problems with AutoGOAL](https://www.automl.org/wp-content/uploads/2020/07/AutoML_2020_paper_20.pdf) is the first actual description of AutoGOAL as a framework, unifying the ideas presented in the previous papers.\n\n## Contribution\n\nCode is licensed under MIT. Read the details in the [collaboration section](https://autogoal.github.io/contributing).\n',
    'author': 'Suilan Estevez-Velarde',
    'author_email': 'suilanestevez@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://autogoal.github.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
