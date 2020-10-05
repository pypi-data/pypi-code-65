# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['invisible_hand',
 'invisible_hand.config',
 'invisible_hand.config.templates',
 'invisible_hand.core',
 'invisible_hand.core.color_text',
 'invisible_hand.scripts',
 'invisible_hand.utils']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.1,<5.0.0',
 'click>=7.1.2,<8.0.0',
 'colorama>=0.4.3,<0.5.0',
 'gitpython>=3.1.7,<4.0.0',
 'google-api-python-client>=1.10.0,<2.0.0',
 'google-auth-httplib2>=0.0.4,<0.0.5',
 'google-auth-oauthlib>=0.4.1,<0.5.0',
 'halo>=0.0.30,<0.0.31',
 'httpx>=0.14.1,<0.15.0',
 'ipython>=7.17.0,<8.0.0',
 'iso8601>=0.1.12,<0.2.0',
 'lxml>=4.5.2,<5.0.0',
 'oauth2client>=4.1.3,<5.0.0',
 'pandas>=1.1.1,<2.0.0',
 'prompt-toolkit>=3.0.6,<4.0.0',
 'pygsheets>=2.0.3,<3.0.0',
 'requests>=2.24.0,<3.0.0',
 'selenium>=3.141.0,<4.0.0',
 'tabulate>=0.8.7,<0.9.0',
 'tqdm>=4.48.2,<5.0.0',
 'trio>=0.16.0,<0.17.0',
 'xlsxwriter>=1.3.3,<2.0.0']

entry_points = \
{'console_scripts': ['hand = invisible_hand.cli:main']}

setup_kwargs = {
    'name': 'invisible-hand',
    'version': '0.2.2',
    'description': 'Automate your workflow with github classroom',
    'long_description': '# Invisible Hand\n\nInvisible Hand is a set of tools to manage your classroom inside github organization. It utilizes `Google Sheets` , `GitHub Classroom` and `GitHub` seamlessly.\n\n## Installation\n\n#### 1. Install via pip\n\n `pip install invisible-hand`\n\n#### 2. Install chromedriver\n\n* OSX\n\n `brew cask install chromedriver`\n* Ubuntu\n\n `apt install chromium-chromedriver`\n\n## Config Files\n\n__Invisible Hand__ operates on 2 config files: `github_config.ini` and `gsheet_config.ini` .\n\nCalling `hand` will automatically propagate these files into working directory with default template. Make sure you have configured them correctly before using them.\n\nAdditionally, if you want to use [ `Announce Grade` ](#announce-grade), follow [here](https://pygsheets.readthedocs.io/en/stable/authorization.html) to get your client secret file and rename it to __client_secret.json__\n\n## Usage\n\n### hand\n\nThe root command\n\n<details>\n<summary><b>Show Detail Information</b></summary>\n\n#### Help Message\n\nappend `-h` or `--help` options get help messages\n\n``` sh\n$ hand -h\nUsage: hand [OPTIONS] COMMAND [ARGS]...\n\n    Toolkits for compiler-f19\n\nOptions:\n    -h, --help         Show this message and exit.\n\nCommands:\n    add-students       student_ids: ids to add\n    announce-grade     announce student grades to each hw repo\n    event-times        repo-hashes : list of <repo>:<hash> strings ex:...\n    grant-team-access  Add students into a github team hw-prefix: prefix for...\n    patch-project      Patch to student homeworks\n```\n\n</details>\n\n---\n\n### Add Students\n\ninvite users into your github organization\n\n<details><summary><b>Show Detail Information</b></summary>\n\n#### Format\n\n``` sh\nhand add-students [github_handle]...\n```\n\n> Use `-h` to see more detailed information about this command.\n\ngithub_handle: github accounts\n\n#### Example\n\n``` sh\nhand add-students ianre657 cmprfk1 cmprfk2 cmprfk3\n```\n\n#### Config file\n\n* github_config.ini\n  + `[github]:personal_access_token`\n  + `[github]:organization`\n  + `[add_students]:default_team_slug`\n\n#### FAQ\n\n* Some students report that they didn\'t get the invitation email.\n\n    Invite student into your organization from their email. This should be Github\'s issue.\n\n    > about 2 of 80 students got this issue from our previous experience.\n\n</details>\n\n---\n\n### Grant specific team read access to H. W. repos\n\nGrant read access right of TA\'s group to students\' homework repo\n\n<details><summary><b>Show Detail Information</b></summary>\n\n#### Config File\n\n* __github_config.ini__:\n  + `[grant_read_access]:reader_team_slug` : team slug of your TA\'s group\n\n#### Format\n\n``` shell\nhand grant-read-access <hw_title>\n```\n\n#### Example\n\n``` shell\nhand grant-read-access hw3\n```\n\n</details>\n\n---\n\n### Patch Project\n\nPatch to student homework repositories.\n\n<details><summary><b>Show Detail Information</b></summary>\n\n#### Config File\n\n* __github_config.ini__:\n  + `[github]:personal_access_token`\n  + `[github]:organization`\n* __gsheet_config.ini__\n  + `[google_spreadsheet]:spreadsheet_url`\n\n#### Format\n\n``` sh\nhand patch-project <hw_title> [--only-repo] <patch_branch>\n```\n\n> Use `-h` to see more detailed information about this command.\n\nBelow is the standard workflow to follow.\n\n#### Workflow\n\ntake homework : __ `hw3` __(the title of your homework in github classroom) for example:\n\n1. The repo __ `tmpl-hw3` __ would be your template for initializing homeworks.\n2. Create another repo to update your template, let\'s say: __ `tmpl-hw3-revise` __\n3. Inside __ `tmpl-hw3-revise` __, create a revision branch __ `1-add-some-new-feature` __ (whatever you like) and an issuse named as the branch name (in this example, __ `1-add-some-new-feature` )__, which will be the content of your PR message.\n4. Open github-classroom, choose your assignment (__ `hw3` __) and disable `assignment invitation URL` of __ `hw3` __.\n5. Create an PR to your template repo (__ `hw3` __) by using this command.\n\n    \n\n``` sh\n    hand patch-project hw3 --only-repo="tmpl-hw3" 1-add-some-new-feature\n    ```\n\n6. Accept the PR in your template repository (__ `tmpl-hw3` __). After that, enable the `assignment invitation URL` of `hw3` in GitHub Classroom. Now you have succcessfully updated your template repo.\n7. Create PRs to students template repositories ( `hw3-<their github id>` ) by running the scirpt as followed.\n\n    \n\n``` sh\n    hand patch-project hw3 1-add-some-new-feature\n    ```\n\n    This script would patch to every repository that uses __hw3__ as the prefix under your GitHub organization.\n\n8. Merge the revision brnach __ `1-add-some-new-feature` __ into `master` in your __ `tmpl-hw3-revise` __ repo. After this step, all documents are updated.\n\n#### Demo (Deprecated)\n\n<img src="./demos/patcher.gif" alt="patcher-demo-video" width="640">\n\n</details>\n\n---\n\n### Crawl Classroom\n\nCrawling homework submission data from Github Classroom\n\n<details><summary><b>Show Detail Information</b></summary>\n\nThis is a web crawler for Github Classroom, which is the input of [ `Event Times` ](#event-times)\n\n#### Config File\n\n* __github_config.ini__:\n  + `[crawl_classroom]:login` : your login id in Github Classroom\n  + `[crawl_classroom]:classroom_id` : the id field of your classroom RESTful page URL. (see the image below)\n\n    <img src="./imgs/clsrm_id.png" alt="id field in the url of github classroom" width="640">\n\n#### Format\n\n``` sh\nhand crawl-classroom [OPTIONS] HW_TITLE OUTPUT\n```\n\n> Use `-h` to see more detailed information about this command\n\n#### Example\n\n``` shell\nhand crawl-classroom --passwd=(cat ~/cred/mypass) hw5 hw5_handle.txt\n```\n\n> This example suppose you use Fish Shell and store your password inside `~/cred/mypass`\nUsers should type their passsword inside the pop-up window if they don\'t provide their password in the argument\n\n#### FAQ\n\n* ChromeDriver\n\n  \n\n``` \n  selenium.common.exceptions.SessionNotCreatedException: Message: session not created: This version of ChromeDriver only supports Chrome version 79\n  ```\n\n  upgrade your chromedriver via `brew cask upgrade chromedriver`\n* All students not submitted\n  + Remember to set deadline of hw on the GitHub classroom (note that deadline can only be set at a future time)\n\n#### Demo\n\n<img src="./demos/github_classroom_craw.gif" alt="github_classroom_craw" width="640">\n\n</details>\n\n---\n\n### Event Times\n\nRetrieve information about late submissions\n\n<details><summary><b>Show Detail Information</b></summary>\n\n#### What it actually does\n\nCompare the last publish-time of specific git commit in each repository and print out which passed the deadline.\n\n#### Config File\n\n* __github_config.ini__:\n  + `[event_times]:deadline` deadline for homework, in ISO8601 compatible format.\n\n    For example `2019-11-12 23:59:59` (the timezone is set to your local timezone as default).\n\n#### Format\n\n``` sh\nhand event-times <input_file> [--deadline="yyyy-mm-dd"]\n```\n\n__input-file__: file contains list of `repo-hash` .\n\n__repo-hash__ : in the format of `<repo>:<git commit hash>` , (for example: hw0-ianre657:cb75e99)\n\nGithub API use the first 7 characters of a commit\'s SHA-1 value to communicate, so the hash we used here is in the length of 7.\n\n> The input pairs `repo:hash` could be retrieve from [ `Crawl Classroom` ](#crawl-classroom).\n\n__ `--deadline` __: it will use the variable inside `github_config.ini` as default.\n\n__ `--target-team` __ (optional): teams to operate on (use team-slug)\n\n#### Example\n\n``` sh\nhand event-times  --target-team="2020-inservice-students" --deadline="2019-11-12 23:59:59"  hw1-handin-0408.txt\n```\n\n#### Demo (need to be updated)\n\n<img src="./demos/event_times.gif" alt="event-times-demo-video" width="640">\n\n</details>\n\n---\n\n### Announce Grade\n\nPublish feedbacks by creating Issue to student\'s homework repo.\n\n<details><summary><b>Show Detail Information</b></summary>\n\n#### Explanation\n\nIn every homework project, we would create a git repository for every student. Take homework `hw3` with two students `Anna` and `Bella` for example, we expect there would be two repos under our github organization, which is `hw3-Anna` and `hw3-Bella` .\nDuring our grading process, T. A.s would record every grade in a google sheet with a tab named `hw3` and a markdown file for each student in every assignment as their feedbacks.\nAfter their homeworks being graded, we use this code to publish student\'s grade by creating `Issue` s named `Grade for hw3` to each of their github repositories.\n\nThe markdown file for feedbacks contains python template strings, and those strings are the column names inside our google sheet tab `hw3` . One template string we used is students grades, this makes managing grades more easily.\n\nTo use this code, you need to fufill some assumptions.\n\nLets say you\'re about to announce the grade for `hw3` :\n\n* prequisite:\n  1. a git repo to store student feedback templates, which strutured as followed:\n\n``` bash\n  . Hw-manager # root of your git repo\n  ├── hw3\n  │\xa0\xa0 └── reports\n  │\xa0\xa0     ├── 0411276.md\n  │\xa0\xa0     ├── 0856039.md\n  │\xa0\xa0     └── 0956323.md\n  └── hw4 # other homework dir\n```\n\nand inside `0411276.md` , it would be:\n\n``` markdown\n  # Information\n\n  + Student Id: ${student_id}\n  + Grade : ${grade}\n\n  # <Some other important things...>\n  ...\n```\n\n  2. a google sheet to store student information\n\n    | student_id | grade |\n    | :--------: | :---: |\n    |  0856039   |  93   |\n    |  0411276   |  80   |\n\n#### Config file\n\n* __github_config.ini__\n  + `[github]:personal_access_token`\n  + `[github]:organization`\n  + `[announce_grade]:feedback_source_repo` (e.x.: Hw-manager)\n* __gsheet_config.ini__\n  + `[google_spreadsheet]:spreadsheet_id`\n* __client_secret.json__ (follow [here](https://pygsheets.readthedocs.io/en/stable/authorization.html) to download your oauth2 secret file and renamed it to __client_secret.json__)\n\n#### instructions to follow\n\n1. Edit config files properly.\n2. Create feedbacks for students in your `feedback_source_repo`\n3. use this script\n\n#### Format\n\n``` sh\nhand announce-grade <hw_title> [--only-id <student_id>]\n```\n\noption:\n\n`--only-id` : only patch to this student id\n\n#### Example\n\n``` sh\nhand announce-grade hw3 --only-id 0411276\n```\n\n</details>\n\n---\n',
    'author': 'Ian Chen',
    'author_email': 'ianre657@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
