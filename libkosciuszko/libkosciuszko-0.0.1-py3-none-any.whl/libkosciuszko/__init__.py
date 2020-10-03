import os
import subprocess
import asyncio
import logging

#  (i) cleanup
#  (ii) write unittests
#  (iii) document
#  (iiii) write cli
#  (v) publish
#  (vi) add to email client

class Kosciuszko():
    def __init__(self, gpg_address, store, debug=False, loglevel="NOTSET"):
        self.sanitation()
        self.debug = debug
        self.loglevel = loglevel
        self.gpg_address = gpg_address
        self.store = store

        if self.debug:
            if loglevel is not None:
                numeric_level = getattr(logging, loglevel.upper(), None)
                if not isinstance(numeric_level, int):
                    raise ValueError(f"Invalid log level: {loglevel}")
            else:
                numeric_level = logging.WARNING
            formatter = '[%(asctime)s] [%(levelname)s] %(message)s'
            logging.basicConfig(level=numeric_level, format=formatter)

    def new(self):
        tmp_dir = subprocess.run(['mktemp', '-p', '/dev/shm', '-d'], capture_output=True)
        assert tmp_dir.returncode == 0, "Failed to create temp directory!"
        tmp_dir = tmp_dir.stdout
        tmp_dir = tmp_dir.decode('utf-8').strip()

        tmp_out = subprocess.run(['mktemp', '-p', '/dev/shm'], capture_output=True)
        assert tmp_out.returncode == 0, "Failed to create temp file!"
        tmp_out = tmp_out.stdout
        tmp_out = tmp_out.decode('utf-8').strip()

        # Make the base image
        rc = subprocess.run([
            'mksquashfs', tmp_dir, tmp_out,
            '-comp', 'zstd',            # Use Zstd compression, as it tends to be better than gzip
            #  '-reproducible',            # Make sure the squash image is still reproducible
            '-xattrs',                  # Preserve our x-attrs!
            '-nopad',                   # Don't make the file bigger than it needs to be
            '-no-recovery',             # Don't generate a recovery file if anything goes wrong. No traces on the users disk
            '-noappend'                 # Force mksquashfs to realise a temporary file isn't an existing squash file
        ], capture_output=True)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to make the base image: {stderr}")
            self.killfile(tmp_out)
            self.killfolder(tmp_dir)
            raise RuntimeError("Failed to make the base image!")

        # Encrypt it
        rc = subprocess.run([
            'gpg', '-q', '--batch', '--yes', '--output', self.store, '-r', self.gpg_address, '--encrypt', tmp_out
        ], capture_output=True)
        self.killfile(tmp_out)
        self.killfolder(tmp_dir)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to encrypt the base image: {stderr}")
            raise RuntimeError("Failed to encrypt the base image!")

    def list(self, detailed=False):
        tmp_out = subprocess.run(['mktemp', '-p', '/dev/shm'], capture_output=True)
        assert tmp_out.returncode == 0, "Failed to create temp file!"
        tmp_out = tmp_out.stdout
        tmp_out = tmp_out.decode('utf-8').strip()

        rc = subprocess.run([
            'gpg', '-q', '--batch', '--yes', '--output', tmp_out, '-r', self.gpg_address, '--decrypt', self.store
        ], capture_output=True)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to decrypt the store: {stderr}")
            self.killfile(tmp_out)
            raise RuntimeError("Failed to decrypt the store!")

        if detailed:
            l = '-lls'
        else:
            l = '-l'
        rc = subprocess.run([
            'unsquashfs', '-no-progress', l, tmp_out
        ], capture_output=True)
        self.killfile(tmp_out)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to unpack the store: {stderr}")
            raise RuntimeError("Failed to unpack the store!")

        stdout = rc.stdout.decode('utf-8').strip().split('\n')
        return stdout[3:]

    def getfile(self, filename):
        tmp_out = subprocess.run(['mktemp', '-p', '/dev/shm'], capture_output=True)
        assert tmp_out.returncode == 0, "Failed to create temp file!"
        tmp_out = tmp_out.stdout
        tmp_out = tmp_out.decode('utf-8').strip()

        rc = subprocess.run([
            'gpg', '--batch', '--yes', '--output', tmp_out, '-r', self.gpg_address, '--decrypt', self.store
        ], capture_output=True)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to decrypt the store: {stderr}")
            self.killfile(tmp_out)
            raise RuntimeError("Failed to decrypt the store!")

        tmp_dir = subprocess.run(['mktemp', '-p', '/dev/shm', '-d'], capture_output=True)
        assert tmp_dir.returncode == 0, "Failed to create temp directory!"
        tmp_dir = tmp_dir.stdout
        tmp_dir = tmp_dir.decode('utf-8').strip()

        rc = subprocess.run([
            'unsquashfs', '-no-progress', 
            '-f', '-d',                     #  Overwrite the directory
            tmp_dir, tmp_out
        ], capture_output=True)
        self.killfile(tmp_out)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to unpack the store: {stderr}")
            raise RuntimeError("Failed to unpack the store!")

        try:
            with open(f'{tmp_dir}/{filename}', 'rb') as fh:
                data = fh.read()
        except:
            e = f"Failed to extract file from the store: {filename}"
            if self.debug:
                logging.error(e)
            self.killfolder(tmp_dir)
            raise RuntimeError(e)

        self.killfolder(tmp_dir)
        return data

    def addfile(self, filename, data):
        tmp_out = subprocess.run(['mktemp', '-p', '/dev/shm'], capture_output=True)
        assert tmp_out.returncode == 0, "Failed to create temp file!"
        tmp_out = tmp_out.stdout
        tmp_out = tmp_out.decode('utf-8').strip()

        rc = subprocess.run([
            'gpg', '--batch', '--yes', '--output', tmp_out, '-r', self.gpg_address, '--decrypt', self.store
        ], capture_output=True)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to decrypt the store: {stderr}")
            self.killfile(tmp_out)
            raise RuntimeError("Failed to decrypt the store!")

        tmp_dir = subprocess.run(['mktemp', '-p', '/dev/shm', '-d'], capture_output=True)
        assert tmp_dir.returncode == 0, "Failed to create temp directory!"
        tmp_dir = tmp_dir.stdout
        tmp_dir = tmp_dir.decode('utf-8').strip()

        rc = subprocess.run([
            'unsquashfs', '-no-progress', 
            '-f', '-d',                     #  Overwrite the directory
            tmp_dir, tmp_out
        ], capture_output=True)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to unpack the store: {stderr}")
            self.killfile(tmp_out)
            self.killfolder(tmp_dir)
            raise RuntimeError("Failed to unpack the store!")

        try:
            with open(f'{tmp_dir}/{filename}', 'wb') as fh:
                fh.write(data)
        except:
            e = f"Failed to add file to the store: {filename}"
            if self.debug:
                logging.error(e)
            self.killfile(tmp_out)
            self.killfolder(tmp_dir)
            raise RuntimeError(e)

        # Remake the image
        rc = subprocess.run([
            'mksquashfs', tmp_dir, tmp_out,
            '-comp', 'zstd',            # Use Zstd compression, as it tends to be better than gzip
            #  '-reproducible',            # Make sure the squash image is still reproducible 
            '-xattrs',                  # Preserve our x-attrs!
            '-nopad',                   # Don't make the file bigger than it needs to be
            '-no-recovery',             # Don't generate a recovery file if anything goes wrong. No traces on the users disk
            '-noappend'                 # Force mksquashfs to realise a temporary file isn't an existing squash file
        ], capture_output=True)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to make the base image: {stderr}")
            self.killfile(tmp_out)
            self.killfolder(tmp_dir)
            raise RuntimeError("Failed to make the base image!")

        # Encrypt it
        rc = subprocess.run([
            'gpg', '-q', '--batch', '--yes', '--output', self.store, '-r', self.gpg_address, '--encrypt', tmp_out
        ], capture_output=True)
        self.killfile(tmp_out)
        self.killfolder(tmp_dir)
        if rc.returncode != 0:
            if self.debug:
                stderr = rc.stderr.decode('utf-8').strip()
                logging.error(f"Failed to encrypt the base image: {stderr}")
            raise RuntimeError("Failed to encrypt the base image!")

        return data

    @staticmethod
    def sanitation():
        """Check dependencies before running anything"""

        if not os.path.isdir('/dev/shm'):
            raise RuntimeError("No ramdisk temporary file found. Unable to function without.")

        try:
            subprocess.run(['mksquashfs'], capture_output=True)
        except:
            raise RuntimeError("Failed to call mksquashfs. Is squashfs-tools installed?")

        try:
            subprocess.run(['unsquashfs'], capture_output=True)
        except:
            raise RuntimeError("Failed to call unsquashfs. Is squashfs-tools installed?")

        try:
            subprocess.run(['zstd'], capture_output=True)
        except:
            raise RuntimeError("Failed to call zstd. Is zstd installed?")

        try:
            subprocess.run(['gpg', '--version'], capture_output=True)
        except:
            raise RuntimeError("Failed to call gpg. Is gpg installed?")

        try:
            subprocess.run(['shred', '--version'], capture_output=True)
        except:
            raise RuntimeError("Failed to call shred. Is shred installed?")

        try:
            subprocess.run(['find', '--version'], capture_output=True)
        except:
            raise RuntimeError("Failed to call shred. Is shred installed?")

    @staticmethod
    def killfile(f):
        """
        Attempt to securely delete a file.
        Note: Many modern file systems and disks are still recoverable
        despite this. It is a 'best effort'.
        Don't rely on this if you have significant enemies.

        Usage:
        p = kosciuszko.killfile('foo')
        <do some work>
        assert p.wait() == 0
        """

        try:
            process = subprocess.Popen([
                'shred',
                '-f',                               # Force permission change
                '-n', '5000',                       # Iterations
                '--random-source=/dev/urandom',     # Shred uses Cs rand by default which is shiiiiiiit
                '-z',                               # Zero out the file as a final pass
                '-u',                               # Deallocate and remove after overwriting
                f                                   # What are we deleting?
            ])
        except:
            process = None

        return process

    def killfolder(self, d):
        """
        Attempt to securely delete an entire folder.
        For the most part, this means killing individual files.
        Folder names might be recoverable.
        Using /dev/shm makes this less likely, as it shouldn't
        persist on disk in most contexts.
        """

        if not os.path.isdir(d):
            return

        processes = [self.killfile(f'{d}/{f}') for f in os.listdir(d)]
        for p in processes:
            if p is not None:
                assert p.wait() == 0, "Failed to kill file!"
        os.rmdir(d)
