# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['transfer_flatfile_format', 'transfer_flatfile_format.packages']

package_data = \
{'': ['*']}

install_requires = \
['google>=3.0.0,<4.0.0',
 'google_spreadsheet>=0.0.6,<0.0.7',
 'numpy>=1.19.1,<2.0.0',
 'pandas>=1.1.1,<2.0.0',
 'pickle5>=0.0.10,<0.0.11']

setup_kwargs = {
    'name': 'transfer-flatfile-format',
    'version': '0.1.2',
    'description': 'Move data inbetween different Amazon flatfile formats to the correct locations.',
    'long_description': "# Transfer flatfile format\n\n## Overview\n\n#### Purpose:\n\nThe underlying problem, which the project tackles is that Amazon provides different flatfile formats. Either because the user chooses different elements or because amazon applies changes to an existing format. In both cases, it is impossible to simply copy and paste data in between formats, when the column headers don't match.\n\n#### Strategy:\n\nFind a sub-set of rows, that match a certain condition (don't contain any values, besides the provided SKU), pull the missing data from an external source supplied through the command line option (-o/--original). Map a fallback value for the SKU from the google sheet by searching for one inside of a plentymarkets export (this is a very specific option usable for our system). Write the data to the google-sheet in form of smaller chunks.\n\n#### Installation:\n\n`python3 -m pip install transfer_flatfile_format --user --upgrade`\n\n#### Usage:\n\nThere are **three* options:\n\n- --orginal / -o:\n    + File location of the flatfile format, which is used as source for the values\n- --exclude / -e:\n    + Comma-separated list of column names (3rd row of a flatfile), to exclude from writing to the google sheet (use case: some columns from the source contain outdated values)\n- --column / -c:\n    + A column name (3rd row of a flatfile), to exclusivly transfer from the source to the google sheet\n\nAdditionally, there is the `config.ini` file within:\n- ~/.transfer_flatfile_format/config.ini (on Linux)\n- C:\\\\Users\\{USER}\\.transfer_flatfile_format (on Windows)\n\nWhich is used to specify the ID of the google sheet and optionally a data source for alternative SKUs.\nThe alternative SKU can be used if your system maintains more than one SKU for one entity. That way you can match a product with one of two possible terms.\n\nExample:\n\nconfig.ini\n\n```\n[General]\ngoogle_sheet_id=1PB_XrUqy6qk......\n[Match table]\nwith_matchtable={y|n}\nsku_export={Link to csv file or location in file system}\nmain_sku={column_name of the column where the main SKU is located}\nalt_sku={column_name of the column where the alternative SKU is located}\n```\n\n##### Example 1: Upload all values from the source file to the google sheet, when the google sheet has an SKU but no values in 'brand_name' or 'item_name':\n\n`python3 -m transfer_flatfile_format -o /home/path/to/source_file.csv`\n\n##### Example 2: Upload all values from the source file at column 'example_column' to the google sheet:\n\n`python3 -m transfer_flatfile_format -o /home/path/to/source_file.csv -c example_column`\n\n##### Example 3: Do the same as with 'Example 1' but do not update the columns 'example_col1' & 'example_col2':\n\n`python3 -m transfer_flatfile_format -o /home/path/to/source_file.csv -e example_col1,example_col2`\n",
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
