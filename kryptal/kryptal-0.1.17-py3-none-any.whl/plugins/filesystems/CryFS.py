import json
import os
from asyncio import subprocess, create_subprocess_exec
from typing import List, Any, Dict, Optional
from kryptal.pluginmanager import IFilesystem
from kryptal.pluginmanager.IFilesystem import FilesystemException, MountedFilesystem
from typing_extensions import final
from kryptal.utils import Subprocess


async def check_call_subprocess(*args: str, input: Optional[bytes] = None, stdout: int = subprocess.PIPE, **kwargs: Any) -> bytes:
    try:
        return await Subprocess.check_call_subprocess(*args, input=input, stdout=stdout, **kwargs)
    except Subprocess.SubprocessException as e:
        raise FilesystemException(e.message())


@final
class CryFS(IFilesystem.IFilesystem):
    def name(self) -> str:
        return "CryFS"

    async def create_and_mount(self, ciphertextDir: str, plaintextDir: str, password: bytes) -> None:
        return await self.mount(ciphertextDir, plaintextDir, password)

    async def mount(self, ciphertextDir: str, plaintextDir: str, password: bytes) -> None:
        await check_call_subprocess(self._executable(), ciphertextDir, plaintextDir, input=password, stdout=subprocess.DEVNULL, env={
            "CRYFS_FRONTEND": "noninteractive",
            "CRYFS_NO_UPDATE_CHECK": "true"
        })

    def _executable(self) -> str:
        options = ["/usr/bin/cryfs", "/usr/local/bin/cryfs"]
        return next(i for i in options if os.path.isfile(i))

    async def unmount(self, plaintextDir: str) -> None:
        await check_call_subprocess("fusermount", "-u", plaintextDir, stdout=subprocess.DEVNULL)

    async def mounted_filesystems(self) -> List[MountedFilesystem]:
        stdout = await check_call_subprocess("findmnt", "-t", "fuse.cryfs", "--json")
        jsondata = stdout.decode("UTF-8")
        if jsondata == "":
            return []
        else:
            return [self._deserializeFilesystem(fs) for fs in json.loads(jsondata)['filesystems']]

    def _deserializeFilesystem(self, fs: Dict[str, Any]) -> MountedFilesystem:
        mountdir = fs['target']
        basedir = fs['source']
        if basedir.startswith("cryfs@"):
            basedir = basedir[6:]
        return MountedFilesystem(plaintextDirectory=mountdir, ciphertextDirectory=basedir)
