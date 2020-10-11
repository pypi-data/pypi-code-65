from kryptal.pluginmanager import IStorageProvider
from typing_extensions import final


@final
class LocalFolder(IStorageProvider.IStorageProvider):
    def name(self) -> str:
        return "LocalFolder"
