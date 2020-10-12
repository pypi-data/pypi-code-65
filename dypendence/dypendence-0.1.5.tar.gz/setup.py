# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['dypendence']

package_data = \
{'': ['*']}

install_requires = \
['dynaconf>=3.1.2,<4.0.0']

setup_kwargs = {
    'name': 'dypendence',
    'version': '0.1.5',
    'description': 'Dependency Injection over Dynaconf',
    'long_description': '![Build Status](https://github.com/VaultVulp/dypendence/workflows/Main/badge.svg)\n![Coverage Badge](https://minio.vaultvulp.dev/coverage/VaultVulp/dypendence/coverage.svg)\n\n# Dypendence\n\nDependency Injection over Dynaconf\n\n## Usage example\n\nExample `settings.toml`\n\n```toml\n[DY.FileStorageService]\nType = "S3FileStorage"\n\n[DY.FileStorageService.LocalFileStorage]\nsome_value = "This is Local File Storage"\n\n[DY.FileStorageService.S3FileStorage]\nsome_value = "This is S3 File Storage"\n```\n\nExample application code:\n\n```python\nfrom dypendence import DY\n\n\nclass FileStorageService(DY):\n\n    def save_file(self) -> str:\n        raise NotImplementedError\n    \n    def get_value_from_settings(self):\n        return self.settings.some_value\n\n\nclass LocalFileStorage(FileStorageService):\n\n    def save_file(self) -> str:\n        return \'Saved file to local file system\'\n\n\nclass S3FileStorage(FileStorageService):\n\n    def save_file(self) -> str:\n        return \'Saved file to S3-like storage\'\n\n\nif __name__ == \'__main__\':\n    file_storage = FileStorageService(settings_files=[\'settings.toml\'])\n\n    assert isinstance(file_storage, S3FileStorage)\n    assert file_storage.save_file() == \'Saved file to S3-like storage\'\n    assert file_storage.get_value_from_settings() == \'This is S3 File Storage\'\n```\n',
    'author': 'VaultVulp',
    'author_email': 'me@vaultvulp.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/VaultVulp/dypendence',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
