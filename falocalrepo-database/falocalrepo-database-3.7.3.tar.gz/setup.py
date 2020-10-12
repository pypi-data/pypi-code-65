# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['falocalrepo_database']

package_data = \
{'': ['*']}

install_requires = \
['filetype>=1.0.7,<1.1.0']

setup_kwargs = {
    'name': 'falocalrepo-database',
    'version': '3.7.3',
    'description': 'Database functionality for falocalrepo.',
    'long_description': '# FALocalRepo-Database\n\nDatabase functionality for [falocalrepo](https://gitlab.com/MatteoCampinoti94/falocalrepo).\n\n## Tables\n\nTo store its information, the database uses four tables: `SETTINGS`, `USERS`, `SUBMISSIONS` and `JOURNALS`.\n\n### Settings\n\nThe settings table contains settings for the program and statistics of the database.\n\n* `USRN` number of users in the `USERS` table\n* `SUBN` number of submissions in the `SUBMISSIONS` table\n* `HISTORY` list of executed commands in the format `[[<time1>, "<command1>"], ..., [<timeN>, "<commandN>"]]` (UNIX time in seconds)\n* `COOKIES` cookies for the scraper, stored in JSON format\n* `FILESFOLDER` location of downloaded submission files\n* `VERSION` database version, this can differ from the program version\n\n### Users\n\nThe users table contains a list of all the users that have been download with the program, the folders that have been downloaded and the submissions found in each of those.\n\nEach entry contains the following fields:\n\n* `USERNAME` The URL username of the user (no underscores or spaces)\n* `FOLDERS` the folders downloaded for that specific user.\n* `GALLERY`\n* `SCRAPS`\n* `FAVORITES`\n* `MENTIONS` this is a legacy entry used by the program up to version 2.11.2 (was named `EXTRAS`)\n* `JOURNALS`\n\n### Submissions\n\nThe submissions table contains the metadata of the submissions downloaded by the program and information on their files \n\n* `ID` the id of the submission\n* `AUTHOR` the username of the author (uploader) in full format\n* `TITLE`\n* `UDATE` upload date in the format YYYY-MM-DD\n* `DESCRIPTION` description in html format\n* `TAGS` keywords sorted alphanumerically and comma-separated\n* `CATEGORY`\n* `SPECIES`\n* `GENDER`\n* `RATING`\n* `FILELINK` the remote URL of the submission file\n* `FILEEXT` the extensions of the downloaded file. Can be empty if the file contained errors and could not be recognised upon download\n* `FILESAVED` 1 if the file was successfully downloaded and saved, 0 if there was an error during download\n\n### Journals\n\nThe journals table contains the metadata of the journals downloaded by the program.\n\n* `ID` the id of the journal\n* `AUTHOR` the username of the author (uploader) in full format\n* `TITLE`\n* `UDATE` upload date in the format YYYY-MM-DD\n* `CONTENT` content in html format\n\n## Submission Files\n\nThe `save_submission` functions saves the submission metadata in the database and stores the files.\n\nSubmission files are saved in a tiered tree structure based on their submission ID. ID\'s are zero-padded to 10 digits and then broken up in 5 segments of 2 digits; each of this segments represents a folder tha will be created in the tree.\n\nFor example, a submission `1457893` will be padded to `0001457893` and divided into `00`, `01`, `45`, `78`, `93`. The submission file will then be saved as `00/01/45/78/93/submission.file` with the correct extension extracted from the file itself - FurAffinity links do not always contain the right extension and often confuse jpg and png.\n\n## Upgrading Database\n\nThe `update_database` function allows to upgrade the database to the current version.\n\n_Note:_ Versions before 2.7.0 are not supported by falocalrepo-database version 3.0.0 and above. To update from those to the new version use [falocalrepo](https://gitlab.com/MatteoCampinoti94/FALocalRepo/-/releases/v2.11.2) version 2.11.2 to update the database to version 2.7.0\n\n### 2.7.x &rarr; 3.0.0\n\nInformation from the database are copied over to the new version, but otherwise remain unaltered save for a few changed column names in the `SUBMISSIONS` and `USERS` tables.\n\nFiles are moved to the new structure and the old files folder is deleted. Only submissions files are kept starting from version 3.0.0\n\n### 3.0.x &rarr; 3.1.0\n\n`EXTRAS` field in `USERS` table is changed to `MENTIONS`, and `extras` and `Extras` folders are renamed to `mentions` and `mentions_all` respectively.\n\n### 3.1.x &rarr; 3.2.0\n\nAdd `JOURNALS` table and `JOURNALS` field in `USERS` table.\n\n### 3.2.x &rarr; 3.3.0\n\nRemove `LASTSTART` and `LASTUPDATE` entries and add `HISTORY` entry in `SETTINGS` table.\n\n### 3.3.x &rarr; 3.4.x\n\nChanges in database functions, simply update `VERSION`.\n\n### 3.4.x &rarr; 3.5.x\n\nUpdate `HISTORY` entry in `SETTINGS` to use the `List[List[float, str]]` format. \n\n### 3.5.x, 3.6.x &rarr; 3.7.0\n\nChanges in database functions, simply update `VERSION`.',
    'author': 'Matteo Campinoti',
    'author_email': 'matteo.campinoti94@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.com/MatteoCampinoti94/falocalrepo-database',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
