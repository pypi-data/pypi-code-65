# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['chaospy',
 'chaospy.chol',
 'chaospy.descriptives',
 'chaospy.descriptives.correlation',
 'chaospy.descriptives.sensitivity',
 'chaospy.distributions',
 'chaospy.distributions.collection',
 'chaospy.distributions.copulas',
 'chaospy.distributions.evaluation',
 'chaospy.distributions.operators',
 'chaospy.distributions.sampler',
 'chaospy.distributions.sampler.sequences',
 'chaospy.external',
 'chaospy.orthogonal',
 'chaospy.quadrature',
 'chaospy.quadrature.genz_keister',
 'chaospy.quadrature.recurrence']

package_data = \
{'': ['*']}

install_requires = \
['numpoly==1.0.6', 'numpy', 'scipy']

extras_require = \
{':python_version >= "2.7" and python_version < "3.0"': ['functools32']}

setup_kwargs = {
    'name': 'chaospy',
    'version': '3.3.9',
    'description': 'Numerical tool for perfroming uncertainty quantification',
    'long_description': '.. image:: docs/.static/chaospy_logo.svg\n   :height: 200 px\n   :width: 200 px\n   :align: center\n\n|circleci| |codecov| |pypi| |readthedocs|\n\n.. |circleci| image:: https://circleci.com/gh/jonathf/chaospy/tree/master.svg?style=shield\n    :target: https://circleci.com/gh/jonathf/chaospy/tree/master\n.. |codecov| image:: https://codecov.io/gh/jonathf/chaospy/branch/master/graph/badge.svg\n    :target: https://codecov.io/gh/jonathf/chaospy\n.. |pypi| image:: https://badge.fury.io/py/chaospy.svg\n    :target: https://badge.fury.io/py/chaospy\n.. |readthedocs| image:: https://readthedocs.org/projects/chaospy/badge/?version=master\n    :target: http://chaospy.readthedocs.io/en/master/?badge=master\n\nChaospy is a numerical tool for performing uncertainty quantification using\npolynomial chaos expansions and advanced Monte Carlo methods implemented in\nPython.\n\n.. contents:: Table of Contents:\n\nInstallation\n------------\n\nInstallation should be straight forward::\n\n    pip install chaospy\n\nAnd you should be ready to go.\n\nExample Usage\n-------------\n\n``chaospy`` is created to be simple and modular. A simple script to implement\npoint collocation method will look as follows:\n\n.. code-block:: python\n\n    import numpy\n    import chaospy\n\n    # your code wrapper goes here\n    coordinates = numpy.linspace(0, 10, 100)\n    def foo(coordinates, params):\n        """Function to do uncertainty quantification on."""\n        param_init, param_rate = params\n        return param_init*numpy.e**(-param_rate*coordinates)\n\n    # bi-variate probability distribution\n    distribution = chaospy.J(chaospy.Uniform(1, 2), chaospy.Uniform(0.1, 0.2))\n\n    # polynomial chaos expansion\n    polynomial_expansion = chaospy.generate_expansion(8, distribution)\n\n    # samples:\n    samples = distribution.sample(1000)\n\n    # evaluations:\n    evals = numpy.array([foo(coordinates, sample) for sample in samples.T])\n\n    # polynomial approximation\n    foo_approx = chaospy.fit_regression(\n        polynomial_expansion, samples, evals)\n\n    # statistical metrics\n    expected = chaospy.E(foo_approx, distribution)\n    deviation = chaospy.Std(foo_approx, distribution)\n\nFor a more extensive guides on what is going on, see the `tutorial collection`_.\n\n.. _tutorial collection: https://chaospy.readthedocs.io/en/master/tutorals\n\nRelated Projects\n----------------\n\nChaospy is being used in other related projects that requires uncertainty\nquantification components ``chaospy`` provides.\n\n+-----------------+-----------------------------------------------------------+\n| `easyVVUQ`_     | Library designed to facilitate verification, validation   |\n|                 | and uncertainty quantification.                           |\n+-----------------+-----------------------------------------------------------+\n| `STARFiSh`_     | Shell-based, scientific simulation program                |\n|                 | for blood flow in mammals.                                |\n+-----------------+-----------------------------------------------------------+\n| `Profit`_       | Probabilistic response model fitting via interactive      |\n|                 | tools.                                                    |\n+-----------------+-----------------------------------------------------------+\n| `UncertainPy`_  | Uncertainty quantification and sensitivity analysis,      |\n|                 | tailored towards computational neuroscience.              |\n+-----------------+-----------------------------------------------------------+\n| `SparseSpACE`_  | Spatially adaptive combination technique targeted to      |\n|                 | solve high dimensional numerical integration.             |\n+-----------------+-----------------------------------------------------------+\n\n.. _easyVVUQ: https://github.com/UCL-CCS/EasyVVUQ\n.. _STARFiSh: https://www.ntnu.no/starfish\n.. _Profit: https://github.com/redmod-team/profit\n.. _UncertainPy: https://github.com/simetenn/uncertainpy\n.. _SparseSpACE: https://github.com/obersteiner/sparseSpACE\n\nAlso a few shout-outs:\n\n+--------------+--------------------------------------------------------------+\n| `OpenTURNS`_ | Thanks to `Régis Lebrun`_ for both proposing a collaboration |\n|              | and creating an initial implementation of both               |\n|              | `Chaospy Compatibility`_ in `OpenTURNS`_ and                 |\n|              | `OpenTURNS Compatibility`_ in ``chaospy``.                   |\n+--------------+--------------------------------------------------------------+\n| `orthopy`_   | Thanks to `Nico Schlömer`_ for providing the implementation  |\n| `quadpy`_    | for several of the quadrature integration methods.           |\n+--------------+--------------------------------------------------------------+\n| ``UQRF``     | Thanks to `Florian Künzner`_ for providing the               |\n|              | implementation for `sample distribution`_.                   |\n+--------------+--------------------------------------------------------------+\n\n.. _OpenTURNS: http://openturns.github.io/openturns/latest\n.. _Régis Lebrun: https://github.com/regislebrun\n.. _Chaospy Compatibility: http://openturns.github.io/openturns/latest/user_manual/_generated/openturns.ChaospyDistribution.html\n.. _OpenTURNS Compatibility: https://chaospy.readthedocs.io/en/master/recipes/external.html#module-chaospy.external.openturns_\n.. _orthopy: https://github.com/nschloe/orthopy\n.. _quadpy: https://github.com/nschloe/quadpy\n.. _Nico Schlömer: https://github.com/nschloe\n.. _Florian Künzner: https://github.com/flo2k\n.. _sample distribution: https://chaospy.readthedocs.io/en/master/recipes/external.html#module-chaospy.external.samples\n\nQuestions and Contributions\n---------------------------\n\nPlease feel free to\n`file an issue <https://github.com/jonathf/chaospy/issues>`_ for:\n\n* bug reporting\n* asking questions related to usage\n* requesting new features\n* wanting to contribute with code\n\nIf you are using this software in work that will be published, please cite the\njournal article: `Chaospy: An open source tool for designing methods of\nuncertainty quantification <http://dx.doi.org/10.1016/j.jocs.2015.08.008>`_\n',
    'author': 'Jonathan Feinberg',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/jonathf/chaospy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
}


setup(**setup_kwargs)
