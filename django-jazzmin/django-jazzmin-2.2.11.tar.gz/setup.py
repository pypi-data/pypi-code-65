# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jazzmin', 'jazzmin.templatetags']

package_data = \
{'': ['*'],
 'jazzmin': ['locale/de/LC_MESSAGES/*',
             'locale/es/LC_MESSAGES/*',
             'locale/zh_Hans/LC_MESSAGES/*',
             'locale/zh_Hant/LC_MESSAGES/*',
             'static/adminlte/css/*',
             'static/adminlte/img/*',
             'static/adminlte/js/*',
             'static/adminlte/plugins/bootstrap/js/*',
             'static/adminlte/plugins/fontawesome-free/css/*',
             'static/adminlte/plugins/fontawesome-free/webfonts/*',
             'static/adminlte/plugins/jquery/*',
             'static/adminlte/plugins/select2/css/*',
             'static/adminlte/plugins/select2/js/*',
             'static/jazzmin/css/*',
             'static/jazzmin/img/*',
             'static/jazzmin/js/*',
             'templates/admin/*',
             'templates/admin/auth/user/*',
             'templates/admin/edit_inline/*',
             'templates/admin/includes/*',
             'templates/admin_doc/*',
             'templates/jazzmin/includes/*',
             'templates/jazzmin/widgets/*',
             'templates/registration/*']}

install_requires = \
['django>=2']

setup_kwargs = {
    'name': 'django-jazzmin',
    'version': '2.2.11',
    'description': "Drop-in theme for django admin, that utilises AdminLTE 3 & Bootstrap 4 to make yo' admin look jazzy",
    'long_description': "# Django jazzmin (Jazzy Admin)\n\n[![Docs](https://readthedocs.org/projects/django-jazzmin/badge/?version=latest)](https://django-jazzmin.readthedocs.io)\n![PyPI download month](https://img.shields.io/pypi/dm/django-jazzmin.svg)\n[![PyPI version](https://badge.fury.io/py/django-jazzmin.svg)](https://pypi.python.org/pypi/django-jazzmin/)\n![Python versions](https://img.shields.io/badge/python-%3E%3D3.5-brightgreen)\n![Django Versions](https://img.shields.io/badge/django-%3E%3D2-brightgreen)\n[![Coverage Status](https://coveralls.io/repos/github/farridav/django-jazzmin/badge.svg?branch=master)](https://coveralls.io/github/farridav/django-jazzmin?branch=master)\n\nDrop-in theme for django admin, that utilises AdminLTE 3 & Bootstrap 4 to make yo' admin look jazzy\n\n## Installation\n```\npip install django-jazzmin\n```\n\n## Documentation\nSee [Documentation](https://django-jazzmin.readthedocs.io) or [Test App](https://github.com/farridav/django-jazzmin/tree/master/tests/test_app/settings.py)\n\n## Demo\nLive demo https://django-jazzmin.herokuapp.com/admin\n\n**Username**: test@test.com\n\n**Password**: test\n\n*Note: Data resets nightly*\n\n## Features\n- Drop-in admin skin, all configuration optional\n- Customisable side menu\n- Customisable top menu\n- Customisable user menu\n- 4 different Change form templates (horizontal tabs, vertical tabs, carousel, collapsible)\n- Search bar for any given model admin\n- Customisable UI (via Live UI changes, or custom CSS/JS)\n- Responsive\n- Select2 drop-downs\n- Bootstrap 4 & AdminLTE UI components\n- Using the latest [adminlte](https://adminlte.io/) + [bootstrap](https://getbootstrap.com/)\n\n## Screenshots\n\n## Dashboard\n![dashboard](https://django-jazzmin.readthedocs.io/img/dashboard.png)\n\n## List view\n![table list](https://django-jazzmin.readthedocs.io/img/list_view.png)\n\n## Change form templates\n\n### Collapsed side menu\n![form page](https://django-jazzmin.readthedocs.io/img/detail_view.png)\n\n### Expanded side menu\n![Single](https://django-jazzmin.readthedocs.io/img/changeform_single.png)\n\n### Horizontal tabs\n![Horizontal tabs](https://django-jazzmin.readthedocs.io/img/changeform_horizontal_tabs.png)\n\n### Vertical tabs\n![Vertical tabs](https://django-jazzmin.readthedocs.io/img/changeform_vertical_tabs.png)\n\n### Collapsible\n![Collapsible](https://django-jazzmin.readthedocs.io/img/changeform_collapsible.png)\n\n### Carousel\n![Carousel](https://django-jazzmin.readthedocs.io/img/changeform_carousel.png)\n\n## History page\n![form page](https://django-jazzmin.readthedocs.io/img/history_page.png)\n\n## Login view\n![login](https://django-jazzmin.readthedocs.io/img/login.png)\n\n## UI Customiser\n![ui_customiser](https://django-jazzmin.readthedocs.io/img/ui_customiser.png)\n\n## Mobile layout\n![mobile](https://django-jazzmin.readthedocs.io/img/dashboard_mobile.png)\n\n## Tablet layout\n![tablet](https://django-jazzmin.readthedocs.io/img/dashboard_tablet.png)\n\n## Admin Docs (if installed)\n![admin_docs](https://django-jazzmin.readthedocs.io/img/admin_docs.png)\n\n## Thanks\nThis was initially a Fork of https://github.com/wuyue92tree/django-adminlte-ui that we refactored so much we thought it\ndeserved its own package, big thanks to @wuyue92tree for all of his initial hard work, we are still patching into that\nproject were possible, but this project has taken a different direction.\n\n- Based on AdminLTE 3: https://adminlte.io/\n- Using Bootstrap 4: https://getbootstrap.com/\n- Using Font Awesome 5: https://fontawesome.com/\n",
    'author': 'Shipit',
    'author_email': 'packages@shipit.ltd',
    'maintainer': 'Shipit',
    'maintainer_email': 'packages@shipit.ltd',
    'url': 'https://github.com/farridav/django-jazzmin',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
