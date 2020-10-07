# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['basedosdados']

package_data = \
{'': ['*'],
 'basedosdados': ['configs/*',
                  'configs/templates/dataset/*',
                  'configs/templates/table/*']}

install_requires = \
['Jinja2==2.11.2',
 'click==7.1.2',
 'google-cloud-bigquery==1.28.0',
 'google-cloud-storage==1.31.2',
 'pandas-gbq==0.13.2',
 'pyaml==20.4.0',
 'tomlkit==0.7.0']

entry_points = \
{'console_scripts': ['basedosdados = basedosdados.cli:cli']}

setup_kwargs = {
    'name': 'basedosdados',
    'version': '0.1.6',
    'description': 'Organizar e facilitar o acesso a dados brasileiros através de tabelas públicas no BigQuery.',
    'long_description': '# A Base dos Dados  🗂️\n\nO intuito do projeto é organizar e facilitar o acesso a dados brasileiros através de tabelas públicas no BigQuery.\nQualquer pessoa poderá fazer queries em bases tratadas e documentadas que estarão disponíveis e estáveis.\n\nUma simples consulta de SQL será o suficiente para cruzamento de bases que você desejar. Sem precisar procurar, baixar, tratar, comprar um servidor e subir clusters.\n\n## Instale nosso CLI\n\n`pip install basedosdados\n\n**Incentivamos que outras instituições e pessoas contribuam**. Só é requerido que o processo de captura e tratamento sejam públicos e documentados, e a inserção dos dados no BigQuery siga nossa metodologia descrita abaixo.\n\n#### Porque o BigQuery?\n\nSabemos que estruturar os dados em uma plataforma privada não é o ideal para um projeto de dados abertos. Porém o BigQuery oferece uma infraestrutura com algumas vantagens:\n\n- É possível deixar os dados públicos, i.e., qualquer pessoa com uma conta no Google Cloud pode fazer uma query na base, quando quiser\n- O usuário (quem faz a query) paga por ela. Isso deixa os custos do projeto bem baixos\n- O BigQuery escala magicamente para hexabytes se necessário\n- O custo é praticamente zero para usuários. São cobrados somente 5 dólares por terabyte de dados que sua query percorrer, e os primeiros 5 terabytes são gratuitos.\n\n### Desenvolvimento\n\n#### CLI\n\nSuba o CLI localmente\n\n```sh\nmake create-env\n. .bases/bin/activate\n```\n\n#### Versionamento\n\nPublique nova versão\n\n```sh\npoetry version [patch|minor|major]\npoetry publish --build\n```\n\n#### Docs\nAtualize os docs adicionando ou editando `.md` em `docs/`.\n\nSe for adicionar um arquivo novo, adicione ele em `mkdocs.yml` sob a chave `nav`.\n\nPara testar a documentação, rode:\n\n```sh\nmkdocs serve \n```\n\n',
    'author': 'Joao Carabetta',
    'author_email': 'joao.carabetta@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/base-dos-dados/bases',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
