# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['jisx0402']
install_requires = \
['pydantic>=1.6.1,<2.0.0']

setup_kwargs = {
    'name': 'jisx0402',
    'version': '0.1.2',
    'description': '全国地方公共団体コードを扱うライブラリ.',
    'long_description': '# JIS X 0402\n\n![status](https://github.com/kitagawa-hr/JIS_X_0402_py/workflows/Python%20package/badge.svg)\n\nこのライブラリはJIS X 0402で規定されている全国地方公共団体コードを扱うライブラリです。\n\n参照しているデータは[総務省のホームページ](https://www.soumu.go.jp/denshijiti/code.html)からダウンロードしたものです。\n\n## Installation\n\n```sh\npip install jisx0402\n```\n\n## Usage\n\n### Recordクラス\n\nデータはこのRecordクラスのインスタンス単位で扱います。\nこのクラスはフィールドとして下記を持っています。\n\n- 全国地方公共団体コード\n- 都道府県名\n- 都道府県名(半角カナ)\n- 市町村名\n- 市町村名(半角カナ)\n\n#### 例\n\n```py\nRecord(code="010006", prefecture="北海道", prefecture_kana="ﾎｯｶｲﾄﾞｳ", city="", city_kana="")\n\nRecord(code="011002", prefecture="北海道", prefecture_kana="ﾎｯｶｲﾄﾞｳ", city="札幌市", city_kana="ｻｯﾎﾟﾛｼ")\n\n```\n\n### code2name\n\n全国地方公共団体コード -> Recordの変換を行います。\n\n#### 例\n\n```py\n>>> code2name("010006")\nRecord(code="010006", prefecture="北海道", prefecture_kana="ﾎｯｶｲﾄﾞｳ", city="", city_kana="")\n```\n\n### search\n\nフィールド名と正規表現を用いてRecordの検索を行います。\n\n#### 例\n\n```py\n>>> search("full_city_name", r"福.県$")\n[\n    Record(code=\'070009\', prefecture=\'福島県\', prefecture_kana=\'ﾌｸｼﾏｹﾝ\', city=\'\', city_kana=\'\'),\n    Record(code=\'180009\', prefecture=\'福井県\', prefecture_kana=\'ﾌｸｲｹﾝ\', city=\'\', city_kana=\'\'),\n    Record(code=\'400009\', prefecture=\'福岡県\', prefecture_kana=\'ﾌｸｵｶｹﾝ\', city=\'\', city_kana=\'\')\n]\n```\n',
    'author': 'kitagawa-hr',
    'author_email': 'kitagawa@cancerscan.jp',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/kitagawa-hr/JIS_X_0402_py',
    'py_modules': modules,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
