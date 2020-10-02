# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xortool']

package_data = \
{'': ['*']}

install_requires = \
['docopt>=0.6.2,<0.7.0']

entry_points = \
{'console_scripts': ['xortool = xortool.tool_main:main',
                     'xortool-xor = xortool.tool_xor:main']}

setup_kwargs = {
    'name': 'xortool',
    'version': '1.0.0',
    'description': 'A tool to analyze multi-byte xor cipher',
    'long_description': 'xortool.py\n====================\n\nA tool to do some xor analysis:\n\n  - guess the key length (based on count of equal chars)\n  - guess the key (base on knowledge of most frequent char)\n\n**Notice:** xortool is now only running on Python 3. The old Python 2 version is accessible at the `py2` branch. The **pip** package has been updated.\n\nInstallation\n---------------------\n\n**xortool** can be installed using **pip**. The recommended way is to run the following command, which installs xortool only for current user. Remove the `--user` flag and run from root if global installation is preferred.\n\n```bash\npython3 -m pip install --user xortool\n```\n\n\nUsage\n---------------------\n\n```\nxortool\n  A tool to do some xor analysis:\n  - guess the key length (based on count of equal chars)\n  - guess the key (base on knowledge of most frequent char)\n\nUsage:\n  xortool [-x] [-m MAX-LEN] [-f] [-t CHARSET] [FILE]\n  xortool [-x] [-l LEN] [-c CHAR | -b | -o] [-f] [-t CHARSET] [-p PLAIN] [FILE]\n  xortool [-x] [-m MAX-LEN| -l LEN] [-c CHAR | -b | -o] [-f] [-t CHARSET] [-p PLAIN] [FILE]\n  xortool [-h | --help]\n  xortool --version\n\nOptions:\n  -x --hex                          input is hex-encoded str\n  -l LEN, --key-length=LEN          length of the key\n  -m MAX-LEN, --max-keylen=MAX-LEN  maximum key length to probe [default: 65]\n  -c CHAR, --char=CHAR              most frequent char (one char or hex code)\n  -b --brute-chars                  brute force all possible most frequent chars\n  -o --brute-printable              same as -b but will only check printable chars\n  -f --filter-output                filter outputs based on the charset\n  -t CHARSET --text-charset=CHARSET target text character set [default: printable]\n  -p PLAIN --known-plaintext=PLAIN  use known plaintext for decoding\n  -h --help                         show this help\n\nNotes:\n  Text character set:\n    * Pre-defined sets: printable, base32, base64\n    * Custom sets:\n      - a: lowercase chars\n      - A: uppercase chars\n      - 1: digits\n      - !: special chars\n      - *: printable chars\n\nExamples:\n  xortool file.bin\n  xortool -l 11 -c 20 file.bin\n  xortool -x -c \' \' file.hex\n  xortool -b -f -l 23 -t base64 message.enc\n  xortool -b -p "xctf{" message.enc\n```\n\nExample 1\n---------------------\n\n```bash\n# xor is xortool/xortool-xor\ntests $ xor -f /bin/ls -s "secret_key" > binary_xored\n\ntests $ xortool binary_xored\nThe most probable key lengths:\n   2:   5.0%\n   5:   8.7%\n   8:   4.9%\n  10:   15.4%\n  12:   4.8%\n  15:   8.5%\n  18:   4.8%\n  20:   15.1%\n  25:   8.4%\n  30:   14.9%\nKey-length can be 5*n\nMost possible char is needed to guess the key!\n\n# 00 is the most frequent byte in binaries\ntests $ xortool binary_xored -l 10 -c 00\n...\n1 possible key(s) of length 10:\nsecret_key\n\n# decrypted ciphertexts are placed in ./xortool_out/Number_<key repr>\n# ( have no better idea )\ntests $ md5sum xortool_out/0_secret_key /bin/ls\n29942e290876703169e1b614d0b4340a  xortool_out/0_secret_key\n29942e290876703169e1b614d0b4340a  /bin/ls\n```\n\nThe most common use is to pass just the encrypted file and the most frequent character (usually 00 for binaries and 20 for text files) - length will be automatically chosen:\n\n```bash\ntests $ xortool tool_xored -c 20\nThe most probable key lengths:\n   2:   5.6%\n   5:   7.8%\n   8:   6.0%\n  10:   11.7%\n  12:   5.6%\n  15:   7.6%\n  20:   19.8%\n  25:   7.8%\n  28:   5.7%\n  30:   11.4%\nKey-length can be 5*n\n1 possible key(s) of length 20:\nan0ther s3cret \\xdd key\n```\n\nHere, the key is longer then default 32 limit:\n\n```bash\ntests $ xortool ls_xored -c 00 -m 64\nThe most probable key lengths:\n   3:   3.3%\n   6:   3.3%\n   9:   3.3%\n  11:   7.0%\n  22:   6.9%\n  24:   3.3%\n  27:   3.2%\n  33:   18.4%\n  44:   6.8%\n  55:   6.7%\nKey-length can be 3*n\n1 possible key(s) of length 33:\nreally long s3cr3t k3y... PADDING\n```\n\nSo, if automated decryption fails, you can calibrate:\n\n- (`-m`) max length to try longer keys\n- (`-l`) selected length to see some interesting keys\n- (`-c`) the most frequent char to produce right plaintext\n\nExample 2\n---------------------\n\nWe are given a message in encoded in Base64 and XORed with an unknown key.\n\n```bash\n# xortool message.enc\nThe most probable key lengths:\n   2:   12.3%\n   4:   13.8%\n   6:   10.5%\n   8:   11.5%\n  10:   8.6%\n  12:   9.4%\n  14:   7.1%\n  16:   7.8%\n  23:   10.4%\n  46:   8.7%\nKey-length can be 4*n\nMost possible char is needed to guess the key!\n```\n\nWe can now test the key lengths while filtering the outputs so that it only keeps the plaintexts holding the character set of Base64. After trying a few lengths, we come to the right one, which gives only 1 plaintext with a percentage of valid characters above the default threshold of 95%.\n\n```bash\n$ xortool message.enc -b -f -l 23 -t base64\n256 possible key(s) of length 23:\n\\x01=\\x121#"0\\x17\\x13\\t\\x7f ,&/\\x12s\\x114u\\x170#\n\\x00<\\x130"#1\\x16\\x12\\x08~!-\\\'.\\x13r\\x105t\\x161"\n\\x03?\\x103! 2\\x15\\x11\\x0b}".$-\\x10q\\x136w\\x152!\n\\x02>\\x112 !3\\x14\\x10\\n|#/%,\\x11p\\x127v\\x143\n\\x059\\x165\\\'&4\\x13\\x17\\r{$("+\\x16w\\x150q\\x134\\\'\n...\nFound 1 plaintexts with 95.0%+ valid characters\nSee files filename-key.csv, filename-char_used-perc_valid.csv\n```\n\nBy filtering the outputs on the character set of Base64, we directly keep the only solution.\n\nInformation\n---------------------\n\nAuthor: hellman\n\nLicense: [MIT License](https://opensource.org/licenses/MIT)\n',
    'author': 'hellman',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
