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
    'version': '0.2.0',
    'description': 'Docker-like tool to set up a headless RaspberryPi or linux',
    'long_description': 'berycker\n========\n\nDocker-like tool to set up a headless RaspberryPi\nヘッドレスでのRaspberryPiやlinuxの初期設定をdockerライクにする、コマンドラインツールです。\n現時点ではラズパイのみ対応\n\ninstall\n=======\n::\n\n    pip install berycker\n\n\nコマンド一覧\n==============\n\ninit\n****\n::\n\n    berycker init\n\nwifiやsshの設定を行います。\nイメージを作ったあと、イメージを焼いたドライブを挿入したままの状態で実行してください。\n\nbuild\n*****\n::\n\n    berycker build\n\nラズパイが起動した後に実行してください。\nberyckerfileを読み込んでマシンの初期設定を行います。\nこの際、sshの接続で必要なホスト名、ユーザー名、パスワードをインタラクティブに答える必要があります。\n\nberyckerfile\n============\nDockerFileにインスパイアされたものなので、Dockerを使ったことがある方は親しみやすいでしょう。\n基本的には関数を実行していく順に並べるだけです。\n関数を先頭に書き、スペースに続けて引数を書きます。\n**関数名は大文字で書くことに注意してください。**\n関数は5つあります。\n::\n\n    FUNCTION_NAME arg\n\nberyckerfileの例はexampleディレクトリにあります。\n\nRUN\n***\n::\n\n    RUN command\n\nこの関数は任意のコマンドを実行します。\n\nADD\n***\n::\n\n    ADD "string" path\n\nこの関数は任意の文字列を既存のファイルに書き込みます。\n絶対パスとホームディレクトリに対しての相対パスをpathに入力できます。\n**任意の文字列はダブルクォーテーションで囲む必要があることに注意してください。**\n\nIP\n**\n::\n\n    IP ip_adress\n\nこの関数はIPアドレスを任意のIPアドレスに固定します。\n\nSSH\n***\n::\n\n    SSH pub_key\n\nこの関数はSSHの公開鍵をマシンに登録します。公開鍵はテキストファイルに保存するべきではないので、以下の変数を使うことをおすすめします。\n\nHOSTNAME\n********\n\n::\n\n    HOSTNAME any_name\n\nこの関数は任意のホスト名をマシンに割り当てます。\n\n変数\n****\n::\n\n    SSH {pub_key}\n\nパスワードなどのファイルに記入することがはばかられる値や、マシンごとに値が異なる所（ホスト名など）を変数として定義できます。\nberyckerfile内で定義した変数は、ビルドするときにインタラクティブに入力できます。\n\n\n\n\n',
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
