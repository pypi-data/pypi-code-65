# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['transfer_flatfile_format', 'transfer_flatfile_format.packages']

package_data = \
{'': ['*']}

install_requires = \
['google-api-python-client>=1.11.0,<2.0.0',
 'google-auth-httplib2>=0.0.4,<0.0.5',
 'numpy>=1.19.1,<2.0.0',
 'pandas>=1.1.1,<2.0.0',
 'pickle5>=0.0.11,<0.0.12']

setup_kwargs = {
    'name': 'transfer-flatfile-format',
    'version': '0.1.0',
    'description': 'Move data inbetween different Amazon flatfile formats to the correct locations.',
    'long_description': '# Transfer flatfile format\n\n## Overview\n\n#### Purpose:\n\nThe underlying problem, which the project tackles is that Amazon provides different flatfile formats. Either because the user chooses different elements or because amazon applies changes to an existing format. In both cases, it is impossible to simply copy and paste data in between formats, when the column headers don\'t match.\n\n#### Strategy:\n\nFind a sub-set of rows, that match a certain condition (don\'t contain any values, besides the provided SKU), pull the missing data from an external source supplied through the command line option (-o/--original). Map a fallback value for the SKU from the google sheet by searching for one inside of a plentymarkets export (this is a very specific option usable for our system). Write the data to the google-sheet in form of smaller chunks (to avoid problems occuring with uploading >10000 values at once to the API).\n\n#### Installation:\n\n- `python3 -m pip install transfer_flatfile_format --user --upgrade`\n\n- Place the credentials file from: [Google sheets tutorial](https://developers.google.com/sheets/api/quickstart/python?authuser=3) into the data folder (see section: \'Usage\'). (`~/.transfer_flatfile_format/.credentials.json`)\n\n- Enter the google-sheets document ID into the config.ini file. (see section \'Usage\')\n\n#### Usage:\n\nThere are **four** options:\n\n- --orginal / -o:\n    + File location of the flatfile format, which is used as source for the values\n- --exclude / -e:\n    + Comma-separated list of column names (3rd row of a flatfile), to exclude from writing to the google sheet (use case: some columns from the source contain outdated values)\n- --column / -c:\n    + A column name (3rd row of a flatfile), to exclusivly transfer from the source to the google sheet\n- --adjust / -a (only in combination with `--column`):\n    + Use the python expression defined within the config under section: [Adjust] option: \'command\' to modify a value from the source flatfile before writing it to the google-sheet.\n    + Example: `command=(X)*2` will multiply the numbers from the column specified with `--column` before writing it to the gsheet.\n    + These expressions are not "smart", so judge on your own if your data can be modified by a single expression.\n\nAdditionally, there is the `config.ini` file within:\n- ~/.transfer_flatfile_format/config.ini (on Linux)\n- C:\\\\Users\\{USER}\\.transfer_flatfile_format (on Windows)\n\nWhich is used to specify the ID of the google sheet and optionally a data source for alternative SKUs.\nThe alternative SKU can be used if your system maintains more than one SKU for one entity. That way you can match a product with one of two possible terms.\n\nExample:\n\nconfig.ini\n\n```\n[General]\ngoogle_sheet_id=1PB_XrUqy6qk......\n[Match table]\nwith_matchtable={y|n}\nsku_export={Link to csv file or location in file system}\nmain_sku={column_name of the column where the main SKU is located}\nalt_sku={column_name of the column where the alternative SKU is located}\n[Adjust]\ncommand=(X)+5//4\n```\n\n##### Example 1: Upload all values from the source file to the google sheet, when the google sheet has an SKU but no values in \'brand_name\' or \'item_name\':\n\n`python3 -m transfer_flatfile_format -o /home/path/to/source_file.csv`\n\n##### Example 2: Upload all values from the source file at column \'example_column\' to the google sheet:\n\n`python3 -m transfer_flatfile_format -o /home/path/to/source_file.csv -c example_column`\n\n##### Example 3: Do the same as with \'Example 1\' but do not update the columns \'example_col1\' & \'example_col2\':\n\n`python3 -m transfer_flatfile_format -o /home/path/to/source_file.csv -e example_col1,example_col2`\n\n##### Example 4: Get values from a column containing integers and add 3 to them:\n\n`python3 -m transfer_flatfile_format -o /home/path/to/source_file.csv -c numeric_column -a`\n\nConfig:\n```\n[General]\ngoogle_sheet_id=1PB_XrUqy6qk......\n[Adjust]\ncommand=(X)+3\n```\n',
    'author': 'Sebastian Fricke',
    'author_email': 'sebastian.fricke.linux@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
