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
    'version': '4.0.7a1',
    'description': 'Splunk Add-on SDK formerly UCC is a build and code generation framework',
    'long_description': '',
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
