import dunamai as _dunamai

__version__ = _dunamai.get_version(
    "nomnomdata-nominode", third_choice=_dunamai.Version.from_any_vcs
).serialize()

__author__ = "Nom Nom Data Inc"
