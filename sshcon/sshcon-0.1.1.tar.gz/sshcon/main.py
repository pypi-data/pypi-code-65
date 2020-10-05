import socket
from ssh2.session import Session
from ssh2.sftp import (
    LIBSSH2_FXF_READ,
    LIBSSH2_SFTP_S_IRUSR,
    LIBSSH2_FXF_CREAT,
    LIBSSH2_FXF_WRITE,
    LIBSSH2_FXF_APPEND,
    LIBSSH2_SFTP_S_IRUSR,
    LIBSSH2_SFTP_S_IRGRP,
    LIBSSH2_SFTP_S_IWUSR,
    LIBSSH2_SFTP_S_IROTH,
)
from typing import Union, Optional
from pathlib import Path
from sshcon.exceptions import SshConSftpError, SshConError
import stat
from ssh2.exceptions import SFTPProtocolError
import errno
import os


class SshCon:
    def __init__(self, host: str, user: str, key, port: int = 22):
        self.user = user
        self.key = str(key)
        self.host = host
        self.port = port
        self.sftp = None
        self.session = self._make_session()

    def _make_session(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        session = Session()
        session.handshake(sock)
        session.userauth_publickey_fromfile(self.user, self.key)
        return session

    def _sftp_session(self):
        if self.sftp is None:
            self.sftp = self.session.sftp_init()
        return self.sftp

    def _lstat(self, path):
        sftp = self._sftp_session()

        try:
            fstat = sftp.lstat(str(path).encode("utf-8"))
        except SFTPProtocolError:
            err_code = sftp.last_error()
            if err_code == 2:
                return False
            else:
                raise SshConSftpError("lsstat", err_code)
        else:
            return fstat.permissions

    def run(
        self,
        cmd: Union[list, str],
        capture_output: bool = False,
        check: bool = True,
        user: Optional[str] = None,
        encoding: Optional[str] = "utf-8",
    ):
        if isinstance(cmd, list):
            cmd = [str(item) for item in cmd]
            cmd = " ".join(cmd)
        if user is not None:
            cmd = f"su - {user} -c '{cmd}'"
        channel = self.session.open_session()
        channel.execute(cmd)
        channel.wait_eof()
        channel.close()
        channel.wait_closed()
        rcode = channel.get_exit_status()
        _buffsize, stderr = channel.read_stderr()
        if check:
            if rcode:
                raise OSError(rcode, stderr.decode("utf-8").strip(), cmd)
        if capture_output:
            size, data = channel.read()
            stdout = b""
            while size > 0:
                stdout += data
                size, data = channel.read()
            if encoding:
                stderr = stderr.decode(encoding)
                stdout = stdout.decode(encoding).rstrip()
            return CompletedCommand(rcode, stdout, stderr)
        return

    def mkdir(
        self,
        path: Union[Path, str],
        mode: int = 511,
        exist_ok: bool = True,
        parents: bool = False,
    ):
        mkdir_cmd = ["mkdir", "-m", mode, path]
        if parents or exist_ok:
            mkdir_cmd.insert(1, "-p")
        self.run(mkdir_cmd, check=True)

    def remove(
        self,
        path: Union[Path, str],
        force: bool = False,
        recursive: bool = False,
    ):
        rm_cmd = ["rm", path]
        if force:
            rm_cmd.insert(1, "-f")
        if recursive:
            rm_cmd.insert(1, "-r")
        self.run(rm_cmd, check=True)

    def rmdir(self, path):
        self._sftp_session().rmdir(str(path))

    def isdir(self, path: Union[str, Path]):
        return stat.S_ISDIR(self._lstat(path))

    def isfile(self, path: Union[str, Path]):
        return stat.S_ISREG(self._lstat(path))

    def ismounted(self, mount):
        try:
            self.run(["mountpoint", mount])
        except OSError:
            return False
        else:
            return True

    def get_filemode(self, path):
        fstat = self._sftp_session().lstat(path)
        return stat.filemode(fstat.permissions)

    def mount(self, source, target, force: bool = False, mkdir: bool = False):
        if self.ismounted(target):
            if force:
                self.umount(target)
            else:
                raise SshConError("mount", f"Folder {target} is already mountpoint.")
        if mkdir:
            self.mkdir(target, exist_ok=True)
        self.run(["mount", source, target], check=True)

    def umount(self, target, rmdir: bool = False):
        self.run(["umount", target], check=True)

    def read_text(self, file, encoding: str = "utf-8"):
        text = None
        if self.isfile(file) is False:
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(file))
        with self._sftp_session().open(
            str(file), LIBSSH2_FXF_READ, LIBSSH2_SFTP_S_IRUSR
        ) as text_file:
            for _size, text_bytes in text_file:
                text = text_bytes.decode(encoding)
        return text

    def write_text(
        self,
        data: str,
        file: Union[Path, str],
        append: bool = False,
        encoding: str = "utf-8",
    ):
        file = str(file)
        if self.isdir(file):
            raise OSError(errno.EISDIR, os.strerror(errno.EISDIR), file)

        mode = (
            LIBSSH2_SFTP_S_IRUSR
            | LIBSSH2_SFTP_S_IWUSR
            | LIBSSH2_SFTP_S_IRGRP
            | LIBSSH2_SFTP_S_IROTH
        )
        f_flags = LIBSSH2_FXF_CREAT | LIBSSH2_FXF_WRITE
        if append:
            f_flags = f_flags | LIBSSH2_FXF_APPEND
        elif self.isfile(file):
            raise FileExistsError(errno.EEXIST, os.strerror(errno.EEXIST), file)

        with self._sftp_session().open(file, f_flags, mode) as text_file:
            text_file.write(data.encode(encoding))

    def chmod(self, path: Union[Path, str], mode: int, recursive: bool = False):
        chmod_cmd = ["chmod", mode, path]
        if recursive:
            chmod_cmd.insert(1, "-R")
        self.run(chmod_cmd, check=True)

    def chown(
        self,
        path: Union[Path, str],
        owner: str,
        group: str,
        recursive: bool = False,
    ):
        chown_cmd = ["chown", f"{owner}:{group}", path]
        if recursive:
            chown_cmd.insert(1, "-R")
        self.run(chown_cmd, check=True)


class CompletedCommand:
    def __init__(self, rcode: int, stdout, stderr):
        self.rcode = rcode
        self.stdout = stdout
        self.stderr = stderr
