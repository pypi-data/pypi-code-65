from traxible.traxodule import Traxodule


class Docker(Traxodule):
    def install(self):
        self.run(
            [
                "sudo apt-get install"
                " -y apt-transport-https"
                " ca-certificates"
                " curl gnupg-agent"
                " software-properties-common",
                "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -",
                "sudo apt-key fingerprint 0EBFCD88",
                "sudo add-apt-repository "
                '" deb [arch=amd64] https://download.docker.com/linux/ubuntu '
                '$(lsb_release -cs) stable"',
                "sudo apt-get update",
                "sudo apt-get install -y docker-ce docker-ce-cli containerd.io",
                "sudo gpasswd -a ubuntu docker",
            ]
        )

    def list(self):
        self.run(["docker container list"])

    def network(self, name, subnet):
        self.run(
            [
                "docker network create --subnet={subnet} {name} || echo fine".format(
                    subnet=subnet, name=name
                )
            ],
            block=False,
        )

    def create(
        self,
        name,
        image,
        network_name=None,
        port_expose=None,
        environ=None,
        restart="always",
        ip=None,
        command=None,
        force=False,
    ):
        command_line = "docker container run -dit --name " + name + " "

        if network_name is not None:
            command_line += " --network " + network_name

        if port_expose is not None:

            for port in port_expose:
                command_line += " -e " + str(port)

        if environ is not None:
            for key, value in environ.items():
                command_line += f" -e {key}={value} "

        if restart is not None:
            command_line += " --restart " + restart

        if ip is not None:
            command_line += " --ip " + ip

        command_line += " " + image + " "

        if command is not None:
            command_line += " " + command

        if force is True:
            self.run(["docker container rm -f {name}".format(name=name)], block=False)

        self.run([command_line])
