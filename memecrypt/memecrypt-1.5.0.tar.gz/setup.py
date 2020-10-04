# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['memecrypt']

package_data = \
{'': ['*']}

install_requires = \
['easyparse', 'requests']

entry_points = \
{'console_scripts': ['memecrypt = memecrypt:main']}

setup_kwargs = {
    'name': 'memecrypt',
    'version': '1.5.0',
    'description': 'An encryption tool, designed for CTF challenges and fun purposes.',
    'long_description': '# Memecrypt\n\nMemecrypt is an encryption tool designed for fun and CTF challenge use.\nIt can be imported as a python module or used as a standalone\nprogram, depending on whichever is needed.\n\n![GitHub forks](https://img.shields.io/github/forks/Sh3llcod3/Memecrypt.svg?style=for-the-badge&label=Fork)\n![GitHub stars](https://img.shields.io/github/stars/Sh3llcod3/Memecrypt.svg?style=for-the-badge&label=Stars)\n![GitHub watchers](https://img.shields.io/github/watchers/Sh3llcod3/Memecrypt.svg?style=for-the-badge&label=Watch)\n\n\n# Usage\n\nThere are 2 main ways to use memecrypt. Both ways are covered here.\n\n## Program use\n\nInstall from PyPi\n\n```shell\n$ python3 -m pip install memecrypt\n```\n\n#### Options\n\nLet\'s start by viewing all the supported arguments.\n\n```shell\n$ memecrypt\n[+] Usage: memecrypt [options]\n\n[i] Examples:\n\n      memecrypt -se -i foo -k bar\n\n      memecrypt --subs -x -f file.txt -k "a_key"\n\n      memecrypt -sx -i \'lorem ipsum\' -k \'some key\'\n\n      memecrypt --subs -e -u cat.thatlinuxbox.com -k \'ascii cat\'\n\n[i] Positional arguments:\n\n       -s --subs\n              Select the substitution cipher.\n       -e --encrypt\n              Select encryption mode.\n       -x --decrypt\n              Select decryption mode.\n       -k --key key\n              Specify key.\n       -i --input input-string\n              Specify input string.\n       -u --url url\n              GETs data from the url.\n       -f --file file-path\n              Specify input file path.\n\n[i] Optional arguments:\n\n       -h --help\n              Show this help screen and exit.\n       -v --version\n              Print version and exit.\n       -q --quiet\n              Only show output. Any errors are still displayed.\n       -o --output-file file\n              Specify a file to write to.\n       -p --pipe-input\n              Take input from stdin.\n```\n\n#### Encryption\n\n```shell\n\n# As an argument\n$ ./memecrypt.py -se -i "foo bar" -k "lorem ipsum"\n[!] Note: Please use the same key for decryption.\n[+] Encrypted result:\n---------------------\nMHFGL1AjdjpSXXx8\n\n# From a URL\n$ ./memecrypt.py --subs --encrypt --url cat.thatlinuxbox.com --key "cat"\n[+] Fetched data from URL.\n[!] Note: Please use the same key for decryption.\n[+] Encrypted result:\n---------------------\nWiJeTFoiXkxaOl5ETDpeREw6XkRMOl5ET.....(and so on).....\n\n# From a local file\n$ ./memecrypt.py -se -f <file-path> -k "foobar" -q\nNWl8eSlMd35ZXTQxU289Y0ZdNGdGTCdrU2FBQ3pM...(and so on)...\n\n```\n\n#### Decryption\n\n```shell\n\n# Decrypt as an argument.\n./memecrypt.py -sx -i bVQ0cjJfVkY1TGNCKFRWWzIkZVF... -k wow\n[+] Decrypted result:\n---------------------\nMuch encryption, very wow\n\n# Decrypt from file\n$ ./memecrypt.py --subs --decrypt -f ../../projects/outputfile -k lol\n[+] Decrypted result:\n---------------------\nCupcake ipsum dolor. Sit amet topping chocolate bar\n\n```\n\n#### Notes\n\nArguments can be placed in any order and combined however you want, as long as they don\'t need\na passed value or directly contradict.\n\n## Module use\n\nInstall using `python3 -m pip install memecrypt`\n\n#### Initialising\n\nLet\'s start by creating an instance of the `meme_cipher` class.\n\n```Python\n# Import our module\nimport memecrypt\n\n# Create an instance\ncipher = memecrypt.meme_cipher(message=None, enc_key=None, show_colors=True)\n\n# message is the message to work on\n# enc_key is the key\n# show_colors=False to turn off all colors\n```\n\n#### Setting a message\n\nSet message using method or attribute.\n\n```Python\n# Using our previous instance\ncipher.set_message("foo")\n\n# We can access/modify this by accessing the message attribute\nprint(cipher.message)\n# Prints: foo\n\n# Let\'s try and set a blank message.\ncipher.set_message(None)\n# Prints: [!] Memecrypt: Plaintext/Ciphertext cannot be empty.\n\n```\n\n#### Setting a key\n\nThis works the same way as setting a message. We\'ll use\nour `cipher` instance. Again, the key cannot be blank or `None`.\n\n```Python\n# Setting a key\ncipher.set_key("bar")\n\n# We can access/modify the key from the enc_key attribute\nprint(cipher.enc_key)\n# Prints: bar\n\n# Same as before, we can\'t set a blank key\ncipher.set_key(\'\')\n# Prints: [!] Memecrypt: Key value cannot be empty.\n\n```\n\n#### Encrypting\n\nEncrypt the values. If key or message is missing, error.\n\n```Python\n# message => foo, key => bar\ncipher.encrypt()\n# Returns: \'NEgydQ==\'\n\n```\n\n#### Decrypting\n\nPerform decryption\n\n```Python\n# message => NEgydQ==, key=> bar\ncipher.decrypt()\n# Returns: \'foo\'\n\n```\n\n#### Input sources\n\nTake input from file.\n\n```Python\n# transfer the contents of the url.\ncat = cipher.fetch_url("cat.thatlinuxbox.com")\n# Returns a ascii cat.\ncipher.set_message(cat)\n# We just set our message as the ascii cat!\n\n# Read a local file.\nfoo_file = cipher.read_file("/path/to/file/file.txt")\n# foo_file will have contents of file.txt\n\n# Set our message to contents of file.txt\ncipher.set_message(foo_file)\n\n```\n\n#### Output files\n\nWrite output to a file.\n\n```Python\n# Append to a file. Create file if file non-existent.\ncipher.write_to("path/to/file/file.txt", "lorem ipsum dolor")\n\n# Let\'s put our encrypted output to a file.\ncipher.write_to("foo_bar.txt", cipher.encrypt())\n```\n',
    'author': 'Sh3llcod3',
    'author_email': '28938427+Sh3llcod3@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Sh3llcod3/Memecrypt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
