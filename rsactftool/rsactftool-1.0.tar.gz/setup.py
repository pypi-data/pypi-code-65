# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src/rsactftool'}

packages = \
['attacks',
 'attacks.multi_keys',
 'attacks.single_key',
 'lib',
 'rsactftool',
 'rsactftool.attacks',
 'rsactftool.attacks.multi_keys',
 'rsactftool.attacks.single_key',
 'rsactftool.lib',
 'rsactftool.sage']

package_data = \
{'': ['*']}

install_requires = \
['cryptography==2.8',
 'gmpy2==2.0.8',
 'gmpy==1.17',
 'pycryptodome==3.9.7',
 'requests==2.20.0',
 'six==1.11.0',
 'sympy==1.3',
 'urllib3==1.24.2']

entry_points = \
{'console_scripts': ['rsactftool = rsactftool.RsaCtfTool:main']}

setup_kwargs = {
    'name': 'rsactftool',
    'version': '1.0',
    'description': 'RSA attack tool (mainly for ctf) - retreive private key from weak public key and/or uncipher data',
    'long_description': '# RsaCtfTool\n\n![lint_python](https://github.com/Ganapati/RsaCtfTool/workflows/lint_python/badge.svg)\n[![GitHub issues](https://img.shields.io/github/issues/Ganapati/RsaCtfTool.svg)](https://github.com/Ganapati/RsaCtfTool/issues)\n[![GitHub forks](https://img.shields.io/github/forks/Ganapati/RsaCtfTool.svg)](https://github.com/Ganapati/RsaCtfTool/network)\n[![GitHub stars](https://img.shields.io/github/stars/Ganapati/RsaCtfTool.svg)](https://github.com/Ganapati/RsaCtfTool/stargazers)\n[![Rawsec\'s CyberSecurity Inventory](https://inventory.rawsec.ml/img/badges/Rawsec-inventoried-FF5050_flat.svg)](https://inventory.rawsec.ml/tools.html#RsaCtfTool)\n[![GitHub license](https://img.shields.io/github/license/Ganapati/RsaCtfTool.svg)](https://github.com/Ganapati/RsaCtfTool)\n\nRSA multi attacks tool : uncipher data from weak public key and try to recover private key\nAutomatic selection of best attack for the given public key\n\nAttacks :\n\n- Weak public key factorization\n- Wiener\'s attack\n- Hastad\'s attack (Small public exponent attack)\n- Small q (q < 100,000)\n- Common factor between ciphertext and modulus attack\n- Fermat\'s factorisation for close p and q\n- Gimmicky Primes method\n- Past CTF Primes method\n- Self-Initializing Quadratic Sieve (SIQS) using Yafu (<https://github.com/DarkenCode/yafu.git>)\n- Common factor attacks across multiple keys\n- Small fractions method when p/q is close to a small fraction\n- Boneh Durfee Method when the private exponent d is too small compared to the modulus (i.e d < n^0.292)\n- Elliptic Curve Method\n- Pollards p-1 for relatively smooth numbers\n- Mersenne primes factorization\n- Factordb\n- Londahl\n- Noveltyprimes\n- Partial q\n- Primefac\n- Qicheng\n- Same n, huge e\n\n## Usage\n\n```bash\nusage: RsaCtfTool.py [-h] [--publickey PUBLICKEY] [--timeout TIMEOUT]\n                     [--createpub] [--dumpkey] [--ext]\n                     [--uncipherfile UNCIPHERFILE] [--uncipher UNCIPHER]\n                     [--verbosity {CRITICAL,ERROR,WARNING,DEBUG,INFO}]\n                     [--private] [--ecmdigits ECMDIGITS] [-n N] [-p P] [-q Q]\n                     [-e E] [--key KEY]\n                     [--attack {mersenne_primes,pollard_p_1,smallfraction,smallq,boneh_durfee,noveltyprimes,ecm,factordb,wiener,siqs,pastctfprimes,partial_q,comfact_cn,hastads,fermat,nullattack,commonfactors,same_n_huge_e,all}]\n```\n\nMode 1 : Attack RSA (specify --publickey or n and e)\n\n- publickey : public rsa key to crack. You can import multiple public keys with wildcards.\n- uncipher : cipher message to decrypt\n- private : display private rsa key if recovered\n\nMode 2 : Create a Public Key File Given n and e (specify --createpub)\n\n- n : modulus\n- e : public exponent\n\nMode 3 : Dump the public and/or private numbers (optionally including CRT parameters in extended mode) from a PEM/DER format public or private key (specify --dumpkey)\n\n- key : the public or private key in PEM or DER format\n\n### Uncipher file\n\n`./RsaCtfTool.py --publickey ./key.pub --uncipherfile ./ciphered\\_file`\n\n### Print private key\n\n`./RsaCtfTool.py --publickey ./key.pub --private`\n\n### Attempt to break multiple public keys with common factor attacks or individually- use quotes around wildcards to stop bash expansion\n\n`./RsaCtfTool.py --publickey "*.pub" --private`\n\n### Generate a public key\n\n`./RsaCtfTool.py --createpub -n 7828374823761928712873129873981723...12837182 -e 65537`\n\n### Dump the parameters from a key\n\n`./RsaCtfTool.py --dumpkey --key ./key.pub`\n\n### Factor with ECM when you know the approximate length in digits of a prime\n\n`./RsaCtfTool.py --publickey key.pub --ecmdigits 25 --verbose --private`\n\nFor more examples, look at test.sh file\n\n## Requirements\n\n- GMPY2\n- SymPy\n- PyCrypto\n- Requests\n- Libnum\n- SageMath : optional but advisable\n- Sage binaries\n\n### Ubuntu 18.04 and Kali specific Instructions\n\n```bash\ngit clone https://github.com/Ganapati/RsaCtfTool.git\nsudo apt-get install libgmp3-dev libmpc-dev\npip3 install -r "requirements.txt"\npython3 RsaCtfTool.py\n```\n\n### MacOS-specific Instructions\n\nIf `pip3 install -r "requirements.txt"` fails to install requirements accessible within environment, the following command may work.\n\n``easy_install `cat requirements.txt` ``\n\n## Todo\n\n- Brainstorm moar attack types !\n',
    'author': 'Ganapati',
    'author_email': '@G4N4P4T1',
    'maintainer': 'borari',
    'maintainer_email': '@borari',
    'url': 'https://github.com/borari/RsaCtfTool',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.9',
}


setup(**setup_kwargs)
