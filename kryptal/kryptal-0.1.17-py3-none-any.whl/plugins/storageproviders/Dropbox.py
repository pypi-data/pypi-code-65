from kryptal.pluginmanager import IStorageProvider
from typing_extensions import final

@final
class Dropbox(IStorageProvider.IStorageProvider):
    def name(self) -> str:
        return "Dropbox"
