
# Library imports
from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Dict, Any, List

# Type check imports
if TYPE_CHECKING:
    pass

# Project imports
from configg.exceptions import *
from configg.section_view import SectionView
from configg.ini_backend import IniBackend


class Configg:
    """
        Simple class that loads config data from a variety of formats (ini, json, xml etc), and presents them as a
        simple dictionary that can be read and written.

        Example:
            cfg = Configg("configg.ini")
            a = cfg.section_one["val_one"]
    """
    def __init__(self, path: str, data_backend=None, autocommit=False, readonly=False):
        """
        Configg constructor
        :param path: Path to config data file (it doesn't exist, will be created)
        :param data_backend: Backend data format (json, ini, xml etc) - defaults to ini
        :param autocommit: If true, writes to the dict will be written back to the config file
        :param readonly: Prevents modifying the dict if true
        """
        data_backend = data_backend or IniBackend
        self._backend = data_backend(path)
        self.readonly = readonly
        self.autocommit = autocommit
        self._sections = {}
        self.reload()

    @property
    def sections(self) -> List[str]:
        """ :return: List of section names """
        return list(self._sections.keys())

    def iter_sections(self):
        """ : return: Generator of Sections """
        return (getattr(self, section) for section in self.sections)

    def commit(self) -> None:
        """ Commits current configg data to file """
        self._backend.write(self._sections)

    def reload(self) -> None:
        """ Reloads configg data from file """
        self._sections = self._backend.read()

    def add_section(self, name: str, data: Optional[Dict[str, Any]] = None) -> SectionView:
        """
        Adds new section to configg data.
        :param name: Name of section (will overwrite existing section)
        :param data: Dict of data to store in section (if omitted, will create empty section)
        """
        self._sections[name] = data or {}
        if self.autocommit:
            self.commit()
        return SectionView(self, self._sections[name])

    def remove_section(self, name: str) -> None:
        """
        Removes section from configg data
        :param name: Name of section
        """
        del self._sections[name]

    def __getattr__(self, item) -> SectionView:
        return SectionView(self, self._sections[item])


