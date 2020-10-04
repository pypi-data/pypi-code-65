# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['berycker']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.3.1,<0.4.0',
 'paramiko>=2.7.2,<3.0.0',
 'psutil>=5.7.2,<6.0.0',
 'termcolor>=1.1.0,<2.0.0']

entry_points = \
{'console_scripts': ['berycker = berycker.cli:main']}

setup_kwargs = {
    'name': 'berycker',
    'version': '0.1.5',
    'description': 'Docker-like tool to set up a headless RaspberryPi or linux',
    'long_description': 'berycker\n========\n\nDocker-like tool to set up a headless RaspberryPi or linux\nヘッドレスでのRaspberryPiやlinuxの初期設定をdockerライクにする、コマンドラインツールです。\n\ninstall\n=======\n::\n\n    pip install berycker\n\n\n使い方\n======\n\ninit\n****\n::\n\n    berycker init\n\nwifiやsshの設定を行います。\nイメージを作ったあと、イメージを焼いたドライブを挿入したままの状態で実行してください。\n\nbuild\n*****\n::\n\n    berycker build\n\nラズパイが起動した後に実行してください。\nberyckerfileを読み込んでマシンの初期設定を行います。\nこの際、sshの接続で必要なホスト名、ユーザー名、パスワードをインタラクティブに答える必要があります。\n\nberyckerfile\n============\nshファイルと同じように書けば問題ないです。#でコメントアウトできます。\nshファイルと違うのは、中括弧で囲むことで変数を定義できることです。\n\n::\n\n    # ssh key setting\n    echo {pub_key} >> .ssh/authorized_keys\n\nパスワードなどのファイルに記入することがはばかられる値や、マシンごとに値が異なる所（ホスト名など）を変数として定義できます。\nberyckerfile内で定義した変数は、ビルドするときにインタラクティブに入力できます。\n\nberyckerfileの例はexampleディレクトリにあります。\n\n',
    'author': 'Tomoki Murayama',
    'author_email': 'muratomo.0205@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://probio.basashi.tech/introduction/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
