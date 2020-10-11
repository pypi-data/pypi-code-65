# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vanilla_option_pricing']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.2,<2.0.0',
 'pandas>=1.1.3,<2.0.0',
 'py-lets-be-rational>=1.0.1,<2.0.0',
 'py_vollib>=1.0.1,<2.0.0',
 'scipy>=1.5.2,<2.0.0']

setup_kwargs = {
    'name': 'vanilla-option-pricing',
    'version': '0.1.0',
    'description': 'Stochastic model for vanilla option pricing',
    'long_description': "# Vanilla Option Pricing\n[![Actions Status](https://github.com/donlelef/vanilla-option-pricing/workflows/main/badge.svg)](https://github.com/donlelef/vanilla-option-pricing/actions)\n[![codecov](https://codecov.io/gh/donlelef/vanilla-option-pricing/branch/master/graph/badge.svg)](https://codecov.io/gh/donlelef/vanilla-option-pricing)\n[![Documentation Status](https://readthedocs.org/projects/vanilla-option-pricing/badge/?version=latest)](https://vanilla-option-pricing.readthedocs.io/en/latest/?badge=latest)\n[![Downloads](https://pepy.tech/badge/vanilla-option-pricing)](https://pepy.tech/project/vanilla-option-pricing)\n\nA Python package implementing stochastic models to price financial options.  \nThe theoretical background and a comprehensive explanation of models and their parameters\ncan be found is the paper *[Fast calibration of two-factor models for energy option pricing](https://arxiv.org/abs/1809.03941)*\nby Emanuele Fabbiani, Andrea Marziali and Giuseppe De Nicolao, freely available on arXiv.  \n\n### Installing\nThe preferred way to install the package is using pip,\nbut you can also download the code and install from source\n\nTo install the package using pip:\n\n```bash\npip install vanilla_option_pricing\n```\n\n### Quickstart\nLet's create a call option.\n\n```python\nfrom datetime import datetime, timedelta\nfrom vanilla_option_pricing.option import VanillaOption\n\noption = VanillaOption(\n    spot=100,\n    strike=101,\n    dividend=0,\n    date=datetime.today(),\n    maturity=datetime.today() + timedelta(days=30),\n    option_type='c',\n    price=1,\n    instrument='TTF'\n)\n```\n\nWe can compute the implied volatility and create a Geometric Brownian Motion \nmodel with it. Of course, if now we ask price the option using the Black framework, \nwe'll get back the initial price.\n\n```python\nfrom vanilla_option_pricing.models import GeometricBrownianMotion\n\nvolatility = option.implied_volatility_of_undiscounted_price\ngbm_model = GeometricBrownianMotion(volatility)\ngbm_price = gbm_model.price_option_black(option)\nprint(f'Actual price: {option.price}, model price: {gbm_price}')\n```\n\nBut, if we adopt a different model, say a Log-spot price mean reverting to \ngeneralised Wiener process model (MLR-GW), we will get a different price.\n\n```python\nimport numpy as np\nfrom vanilla_option_pricing.models import LogMeanRevertingToGeneralisedWienerProcess\n\np_0 = np.eye(2)\nmodel = LogMeanRevertingToGeneralisedWienerProcess(p_0, 1, 1, 1)\nlmrgw_price = model.price_option_black(option)\nprint(f'Actual price: {option.price}, model price: {lmrgw_price}')\n```\n\nIn the previous snippet, the parameters of the LMR-GW model were chosen\nat random. We can also calibrate the parameters of a model against \nlisted options.\n\n```python\nfrom datetime import date\nfrom vanilla_option_pricing.option import VanillaOption\nfrom vanilla_option_pricing.models import OrnsteinUhlenbeck, GeometricBrownianMotion\nfrom vanilla_option_pricing.calibration import ModelCalibration\n\ndata_set = [\n    VanillaOption('TTF', 'c', date(2018, 1, 1), 2, 101, 100, date(2018, 2, 1)),\n    VanillaOption('TTF', 'p', date(2018, 1, 1), 2, 98, 100, date(2018, 2, 1)),\n    VanillaOption('TTF', 'c', date(2018, 1, 1), 5, 101, 100, date(2018, 5, 31))\n]\n\nmodels = [\n    GeometricBrownianMotion(0.2),\n    OrnsteinUhlenbeck(p_0=0, l=100, s=2)\n]\ncalibration = ModelCalibration(data_set)\n\nprint(f'Implied volatilities: {[o.implied_volatility_of_undiscounted_price for o in data_set]}\\n')\n\nfor model in models:\n    result, trained_model = calibration.calibrate_model(model)\n    print('Optimization results:')\n    print(result)\n    print(f'Calibrated parameters: {trained_model.parameters}\\n\\n')\n```\n",
    'author': 'Emanuele Fabbiani',
    'author_email': 'donlelef@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/donlelef/vanilla-option-pricing',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
