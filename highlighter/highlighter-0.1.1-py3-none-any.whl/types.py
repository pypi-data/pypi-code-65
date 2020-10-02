from dataclasses import asdict, dataclass
from typing import Iterable, Optional, Sequence

from packaging.markers import Marker


@dataclass
class EnvironmentMarkers:
    os_name: str = "posix"
    sys_platform: str = "linux"
    platform_machine: str = "x86_64"
    platform_python_implementation: str = "CPython"
    platform_release: Optional[str] = None
    platform_system: str = "Linux"
    platform_version: Optional[str] = None
    python_version: Optional[str] = None
    python_full_version: Optional[str] = None
    implementation_name: str = "cpython"
    # extra: Optional[str] = None  # ??

    def __post_init__(self) -> None:
        if self.sys_platform == "linux":
            if self.python_version and self.python_version[:1] == "2":
                self.sys_platform = "linux2"
        elif self.sys_platform == "win32":
            self.platform_system = "Windows"
            self.os_name = "nt"
        elif self.sys_platform == "darwin":
            self.platform_system = "Darwin"
        else:
            raise TypeError(f"Unknown sys_platform: {self.sys_platform!r}")

    @classmethod
    def for_python(cls, version: str, platform: str = "linux",) -> "EnvironmentMarkers":
        assert platform in (None, "linux", "win32", "darwin")
        assert version.count(".") == 2
        t = ".".join(version.split(".")[:2])
        return cls(sys_platform=platform, python_version=t, python_full_version=version)

    def match(self, marker: Marker, extras: Sequence[str] = ()) -> bool:
        env = dict(**asdict(self), extra=Extras(extras))
        return bool(marker.evaluate(env))


class Extras:
    """
    This is a tiny class that lets us get 'extra == "foo"' working for
    `packaging.markers`
    """

    def __init__(self, extras: Iterable[str]) -> None:
        self.extras = extras

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, str):
            return False
        return other in self.extras
