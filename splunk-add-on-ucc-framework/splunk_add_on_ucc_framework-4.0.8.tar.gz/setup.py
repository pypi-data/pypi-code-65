# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['splunk_add_on_ucc_framework',
 'splunk_add_on_ucc_framework.UCC-UI-lib',
 'splunk_add_on_ucc_framework.UCC-UI-lib.schema',
 'splunk_add_on_ucc_framework.alert_utils',
 'splunk_add_on_ucc_framework.alert_utils.alert_utils_common',
 'splunk_add_on_ucc_framework.alert_utils.alert_utils_common.metric_collector',
 'splunk_add_on_ucc_framework.modular_alert_builder',
 'splunk_add_on_ucc_framework.modular_alert_builder.build_core',
 'splunk_add_on_ucc_framework.uccrestbuilder',
 'splunk_add_on_ucc_framework.uccrestbuilder.endpoint']

package_data = \
{'': ['*'],
 'splunk_add_on_ucc_framework': ['arf_dir_templates/*',
                                 'arf_dir_templates/modular_alert_package/${product_id}/appserver/static/*',
                                 'package/appserver/static/css/*',
                                 'package/appserver/static/js/build/*',
                                 'package/appserver/static/styles/*',
                                 'package/appserver/templates/*',
                                 'package/default/data/ui/nav/*',
                                 'package/default/data/ui/views/*',
                                 'package/locale/*',
                                 'package/locale/zh_CN/LC_MESSAGES/*',
                                 'templates/*'],
 'splunk_add_on_ucc_framework.UCC-UI-lib': ['data/*',
                                            'package/appserver/static/css/*',
                                            'package/appserver/static/js/collections/*',
                                            'package/appserver/static/js/constants/*',
                                            'package/appserver/static/js/mixins/*',
                                            'package/appserver/static/js/models/*',
                                            'package/appserver/static/js/pages/*',
                                            'package/appserver/static/js/router/*',
                                            'package/appserver/static/js/shim/*',
                                            'package/appserver/static/js/templates/common/*',
                                            'package/appserver/static/js/templates/messages/*',
                                            'package/appserver/static/js/util/*',
                                            'package/appserver/static/js/views/*',
                                            'package/appserver/static/js/views/component/*',
                                            'package/appserver/static/js/views/configuration/*',
                                            'package/appserver/static/js/views/controls/*',
                                            'package/appserver/static/js/views/pages/*',
                                            'package/appserver/static/styles/*',
                                            'package/appserver/templates/*',
                                            'package/default/*',
                                            'package/default/data/ui/nav/*',
                                            'package/default/data/ui/views/*',
                                            'package/locale/*',
                                            'package/locale/zh_CN/LC_MESSAGES/*'],
 'splunk_add_on_ucc_framework.modular_alert_builder.build_core': ['arf_template/*',
                                                                  'arf_template/default_html_theme/*']}

install_requires = \
['future>=0,<1',
 'jinja2>=2,<3',
 'lxml>=4.3,<5.0',
 'mako>=1,<2',
 'munch>=2,<3',
 'solnlib>=3.0,<4.0',
 'splunktaucclib>=4.0,<5.0',
 'wheel']

entry_points = \
{'console_scripts': ['build-ucc = build:build_ucc',
                     'install-libs = '
                     'splunk_add_on_ucc_framework:install_requirements',
                     'ucc-gen = splunk_add_on_ucc_framework:main']}

setup_kwargs = {
    'name': 'splunk-add-on-ucc-framework',
    'version': '4.0.8',
    'description': 'Splunk Add-on SDK formerly UCC is a build and code generation framework',
    'long_description': '# splunk-add-on-ucc-framework\n\n![PyPI](https://img.shields.io/pypi/v/splunk-add-on-ucc-framework)\n![Python](https://img.shields.io/pypi/pyversions/splunk-add-on-ucc-framework.svg)\n\nA framework to generate Splunk Add-ons. It includes UI, Rest handler, Modular input, Oauth, Alert action templates.\n\n## What is UCC?\n\nUCC is Universal Configuration Console. It is a service for Generating Splunk Add-ons which is easily customizable and flexible.\nIt is helpful to control the activity by using hooks and other functionalities. UCC provides basic UI template for creating Addon\'s UI.\n\n\n## Features\n\n- Generate ucc based addons for your Splunk Technology Add-ons\n\n\n## Requirements\n\n- Addon package and globalConfig.json file\n\n> Note: You may refer the globalConfig.json file [here](tests/data/globalConfig.json)\n\n\n## Installation\n\nYou can install "splunk-add-on-ucc-framework" via `pip` from `PyPI`:\n\n```bash\n$ pip3 install splunk-add-on-ucc-framework\n```\n\n\n## How to use\n\nTo build the ucc based addon follow the below steps:\n\n1. Install the `splunk-add-on-ucc-framework` via `pip3`\n2. Run the `ucc-gen` command\n3. Make sure that `package` directory and `globalConfig.json` file present in the directory\n4. The final addon package will be generated, at `output` directory.\n\n\n## Workflow\n\nBy the running the `ucc-gen` command, the following steps came in action:\n1. Cleaning out the `output` directory\n2. Retrieve the package ID of addon\n3. Copy UCC template directory under `output/<package_ID>` directory\n4. Copy `globalConfig.json` file to `output/<package_ID>/appserver/static/js/build` directory\n5. Collect and install Addon\'s Requirements into `output/<package_ID>/lib` directory of addon\'s package\n6. For the addon\'s requirements, packages were installed according to following table.\n\n| File Name            | Description                         | Output directory in ucc build |\n|----------------------|-------------------------------------|-------------------------------|\n| requirements.txt     | Python2/python3 compatible packages | output/<package_ID>/lib       |\n| requirements_py2.txt | Only Python2 compatible packages    | output/<package_ID>/lib/py2   |\n| requirements_py3.txt | Only python3 compatible packages    | output/<package_ID>/lib/py3   |\n\n7. Replace tokens in views\n8. Copy addon\'s `package/*` to `output/<package_ID>/*` directory\n\n\n## Params\n\nsplunk-add-on-ucc-framework supports the following params:\n| Name       | Description                                                                                              |\n|------------|----------------------------------------------------------------------------------------------------------|\n| source     | Folder containing the app.manifest and app source                                                        |\n| config     | Path to the configuration file, Defaults to GlobalConfig.json in the parent directory of source provided |\n| ta-version | Current version of TA, Default version is version specified in globalConfig.json                         |',
    'author': 'rfaircloth-splunk',
    'author_email': 'rfaircloth@splunk.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/splunk/splunk-add-on-sdk-python/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
