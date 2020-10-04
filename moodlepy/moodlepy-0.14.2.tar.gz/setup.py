# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['moodle',
 'moodle.auth',
 'moodle.auth.email',
 'moodle.base',
 'moodle.base.preference',
 'moodle.core',
 'moodle.core.badges',
 'moodle.core.block',
 'moodle.core.blog',
 'moodle.core.calendar',
 'moodle.core.cohort',
 'moodle.core.comment',
 'moodle.core.competency',
 'moodle.core.completion',
 'moodle.core.course',
 'moodle.core.message',
 'moodle.core.notes',
 'moodle.core.user',
 'moodle.core.webservice',
 'moodle.mod',
 'moodle.mod.assign',
 'moodle.mod.folder',
 'moodle.mod.forum',
 'moodle.mod.lesson',
 'moodle.mod.resource',
 'moodle.mod.url',
 'moodle.tool',
 'moodle.tool.mobile',
 'moodle.utils']

package_data = \
{'': ['*']}

install_requires = \
['dacite>=1.5.1,<2.0.0', 'requests>=2.24.0,<3.0.0']

entry_points = \
{'console_scripts': ['moodle = moodle.__main__:main']}

setup_kwargs = {
    'name': 'moodlepy',
    'version': '0.14.2',
    'description': 'Client for moodle webservice',
    'long_description': "# moodlepy\n\n[![moodlepy - PyPi](https://img.shields.io/pypi/v/moodlepy)](https://pypi.org/project/moodlepy/)\n[![codecov](https://codecov.io/gh/hexatester/moodlepy/branch/master/graph/badge.svg)](https://codecov.io/gh/hexatester/moodlepy)\n[![BUILD](https://img.shields.io/travis/com/hexatester/moodlepy)](https://travis-ci.com/github/hexatester/moodlepy)\n[![LICENSE](https://img.shields.io/github/license/hexatester/moodlepy)](https://github.com/hexatester/moodlepy/blob/master/LICENSE)\n\nPython client for moodle webservice\n\n## Introduction\n\nThis library provide a pure Python interface for [Moodle Web Service](https://docs.moodle.org/dev/Web_services). It's compatible with Python versions 3.7+\n\n## Installing\n\nYou can install or upgrade moodlepy with:\n\n```bash\npip install moodlepy --upgrade\n```\n\nOr you can install from source with:\n\n```bash\ngit clone https://github.com/hexatester/moodlepy\ncd moodlepy\npython setup.py install\n```\n\n## Usage\n\nExample usage\n\n```python\nfrom moodle import Moodle\nurl = 'https://my.domain/webservice/rest/server.php'\ntoken = 'super secret token'\nmoodle = Moodle(url, token)\nraw_site_info = moodle('core_webservice_get_site_info')\nsite_info = moodle.core.webservice.get_site_info()  # return typed site_info\n\nprint(raw_site_info)\nprint(site_info)\n\n# or\nfrom moodle import Mdl\nfrom moodle.core.webservice import BaseWebservice\n\nmoodle = Mdl(url, token)\nwebservice = BaseWebservice(moodle)\nsite_info2 = webservice.get_site_info()\n\nassert site_info == site_info2\n```\n\nIn the future all [Web service functions](https://docs.moodle.org/dev/Web_service_API_functions) will be covered by moodlepy\n\n# Moodle Web Service support\n\n❗️ Not all types and methods are supported, since moodlepy is not yet released.\nA = Added, W = Work In Progress\n\n| Area                 | Functions | Types | Tests | Status |\n| -------------------- | --------- | ----- | ----- | ------ |\n| auth_email           | A         | A     |       |        |\n| block                |           |       |       |        |\n| core_auth            |           |       |       |        |\n| core_backup          |           |       |       |        |\n| core_badge           | A         | A     | A     |        |\n| core_blog            | A         | A     | A     |        |\n| core_calendar        | A         | A     |       | W      |\n| core_cohort          |           |       |       |        |\n| core_comment         |           |       |       | W      |\n| core_competency      |           |       |       |        |\n| core_completion      | A         | A     |       |        |\n| core_course          |           |       |       | W      |\n| core_customfield     |           |       |       |        |\n| core_enrol           |           |       |       |        |\n| core_fetch           |           |       |       | W      |\n| core_files           |           |       |       | W      |\n| core_filters         |           |       |       |        |\n| core_form            |           |       |       | W      |\n| core_get             |           |       |       | W      |\n| core_grade           |           |       |       | W      |\n| core_grades          |           |       |       |        |\n| core_grading         |           |       |       |        |\n| core_group           |           |       |       |        |\n| core_h5p             |           |       |       |        |\n| core_message         |           |       |       | W      |\n| core_notes           | A         | A     |       | W      |\n| core_output          |           |       |       |        |\n| core_question        | W         |       |       | W      |\n| core_rating          |           |       |       |        |\n| core_role            |           |       |       |        |\n| core_search          |           |       |       | W      |\n| core_session         |           |       |       | W      |\n| core_tag             |           |       |       |        |\n| core_update          |           |       |       |        |\n| core_user            |           |       |       | W      |\n| core_webservice      | A         | A     | A     | A      |\n| enrol_guest          |           |       |       |        |\n| enrol_manual         |           |       |       |        |\n| enrol_self           |           |       |       |        |\n| gradereport_overview |           |       |       |        |\n| gradereport_user     |           |       |       |        |\n| gradingform_guide    |           |       |       |        |\n| gradingform_rubric   |           |       |       |        |\n| local_mobile         |           |       |       | W      |\n| message_airnotifier  |           |       |       | W      |\n| message_popup        |           |       |       | W      |\n| mod_assign           |           |       |       | W      |\n| mod_book             |           |       |       |        |\n| mod_chat             |           |       |       | W      |\n| mod_choice           |           |       |       |        |\n| mod_data             |           |       |       |        |\n| mod_feedback         |           |       |       |        |\n| mod_folder           | A         | A     |       |        |\n| mod_forum            |           |       |       | W      |\n| mod_glossary         |           |       |       |        |\n| mod_imscp            |           |       |       |        |\n| mod_label            |           |       |       |        |\n| mod_lesson           |           |       |       | W      |\n| mod_lti              |           |       |       |        |\n| mod_page             |           |       |       | W      |\n| mod_quiz             |           |       |       | W      |\n| mod_resource         | A         | A     |       |        |\n| mod_scorm            |           |       |       |        |\n| mod_survey           |           |       |       | W      |\n| mod_url              | A         | A     |       |        |\n| mod_wiki             |           |       |       |        |\n| mod_workshop         |           |       |       |        |\n| report_competency    |           |       |       |        |\n| report_insights      |           |       |       |        |\n| tool_analytics       |           |       |       |        |\n| tool_lp              |           |       |       |        |\n| tool_mobile          | A         | A     |       | W      |\n| tool_templatelibrary |           |       |       |        |\n| tool_usertours       |           |       |       |        |\n| tool_xmldb           |           |       |       |        |\n",
    'author': 'hexatester',
    'author_email': 'habibrohman@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hexatester/moodlepy',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
