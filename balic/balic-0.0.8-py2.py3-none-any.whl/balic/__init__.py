# -*- coding: utf-8 -*-
import logging
import os
import yaml

from sarge import Capture
from sarge import run


try:
    import appdirs
except ModuleNotFoundError:
    print(
        "appdirs missing - should the issue persists post install, "
        "run `pip install appdirs` manually"
    )

try:
    from pyfiglet import Figlet
except ModuleNotFoundError:
    Figlet = None


class Balic(object):
    """Balic is a toolset for working with LXC containers.
    It creates, builds and destroys LXC containers.
    """

    __version__ = "0.0.8"

    __config__ = """
---
# Log level: debug, info, warning, error, critical
log_level: info

# LXC directory
lxc_dir: ~/.local/share/lxc

# subuid subgid
subuid: 100000
subgid: 100000
        """

    def __init__(self, name):
        """Initializes Balic object with its configuration.
        """
        self.log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        self.local_path = os.getcwd()
        self.global_path = os.path.join(appdirs.user_config_dir(), "balic")

        self.config_file = "balic.yml"
        self.config_dot_file = ".balic.yml"

        self.loaded_config_file = None

        self.config = None
        self.configure()

        self.name = name
        self.lxc_dir = self.get_full_path(self.config["lxc_dir"])
        self.rootfs = self.get_full_path(f"{self.lxc_dir}/{self.name}/rootfs")
        self.build_dir = self.get_full_path(f"/tmp/balic")
        self.build_script = self.get_full_path(f"{self.build_dir}/build.sh")
        self.balic_dir = self.get_full_path(f"{self.rootfs}{self.build_dir}")

    def configure(self):
        """Tries to load Balic configuration from current working directory
        then user config directory and if none found it defaults to internal
        configuration stored in ``Balic.__config__``.
        """

        def loadrc(config_file):
            self.config = yaml.safe_load(open(config_file, "r"))
            self.loaded_config_file = config_file

        try:
            loadrc(self.config_dot_file)
        except FileNotFoundError:
            try:
                loadrc(self.config_file)
            except FileNotFoundError:
                try:
                    loadrc(
                        os.path.join(self.global_path, self.config_dot_file)
                    )
                except FileNotFoundError:
                    try:
                        loadrc(
                            os.path.join(self.global_path, self.config_file)
                        )
                    except FileNotFoundError:
                        self.config = yaml.safe_load(self.__config__)
                        self.loaded_config_file = "default"

        self.get_logger()

    def get_logger(self):
        """Sets up logger
        """
        logging.basicConfig()

        self.log = logging.getLogger(__name__)

        self.log_level = self.log_levels["INFO"]
        if "log_level" in self.config:
            self.log_level = self.log_levels[self.config["log_level"].upper()]
            self.log.debug(
               f"Set logging to {self.config['log_level'].upper()}"
            )

        self.log.setLevel(self.log_level)

    def get_full_path(self, path):
        return os.path.abspath(os.path.expanduser(path))

    @staticmethod
    def get_parser(parser):
        """Returns parser with base Balic's arguments:

        * ``-n`` ``--name`` container name
        """
        parser.add_argument("-n", "--name", required=True)
        return parser

    def ls(self, list_all=False):
        """List linux containers.
        """
        if list_all is True:
            run(f"lxc-ls -f")
        else:
            run(f"lxc-ls -n {self.name} -f")

    def create(self):
        """Creates base Debian Buster (amd64) container.
        """
        run(
            f"lxc-create -n {self.name} -t download -- "
            f"--dist debian --release buster --arch amd64"
        )

    def build(self, build_dir, environment):
        """Runs build.sh that must be present in the given
        build_dir which is copied over into the Linux container.

        The process firstly starts the container and waits for 3 seconds
        for the networking being established.

        build_dir can contain any number of files and directories
        to be copied into the container.

        Once the build directory is copied inside the container
        build.sh is run from inside the container.

        Once the process is finished the container is stopped.
        """
        run(f"lxc-start -n {self.name} && sleep 3")

        run(f"lxc-attach --clear-env -n {self.name} -- rm -r {self.build_dir}")

        if self.log_level == self.log_levels["DEBUG"]:
            run(f"sudo cp -rv {build_dir} {self.balic_dir}")
        else:
            run(f"sudo cp -r {build_dir} {self.balic_dir}")

        if self.log_level == self.log_levels["DEBUG"]:
            run(f"sudo chown "
                f"{self.config['subuid']}:{self.config['subgid']} "
                f"{self.balic_dir} -Rv")
        else:
            run(f"sudo chown "
                f"{self.config['subuid']}:{self.config['subgid']} "
                f"{self.balic_dir} -R")

        run(f"lxc-attach --clear-env -n {self.name} -- /bin/sh {self.build_script} {environment}")

        run(f"lxc-stop -n {self.name}")

    def prepare(self, build_dir, environment, something=""):
        """Runs prepare.sh that must be present in the given build_dir.

        Purpose of the prepare.sh is to prepare the build_dir before build is run.

        Example prepare.sh::
            #!/bin/bash

            # download deploy key mydeploykey.rsa from 1password Private vault
            # so that it can be used by the build.sh
            op get document --vault Private "my deploy key" > mydeploykey.rsa
        """
        prepare_script = self.get_full_path(f"{build_dir}/prepare.sh")
        if something != "":
            prepare_script = self.get_full_path(f"{build_dir}/prepare/{something}.sh")
        run(f"/bin/sh {prepare_script} {environment}")

    def pack(self, output_file):
        """Packs Linux container to given output file.

        Output file format is .tar.gz
        """
        cmd = (
            f"cd {self.rootfs} && "
            f"sudo tar czf {output_file} *"
        )
        run(cmd, shell=True)

    def destroy(self):
        """Destroys container.
        """
        run(f"lxc-destroy -n {self.name}")

    def hosts(self, site):
        """Add or update /etc/hosts file entry for given site.
        """
        get_ip = run("lxc-ls -f", stdout=Capture())
        get_ip.close()
        lines = get_ip.stdout.readlines()
        ip_address = ""
        for line in lines:
            if self.name in str(line):
                ip_address = str(line).split()[4]

        ip_address_pattern = "^\([0-9]\{1,3\}[.]\)\{3\}[0-9]\{1,3\}"

        check_hosts = run(
            f'grep -q "{ip_address_pattern} {site}$" /etc/hosts'
        )

        if check_hosts.returncode == 1:
            run(f'echo "{ip_address} {site}" | sudo tee -a /etc/hosts')
        else:
            replace = f"s/{ip_address_pattern} {site}/{ip_address} {site}/g"
            run(f"sudo sed -i '{replace}' /etc/hosts")
