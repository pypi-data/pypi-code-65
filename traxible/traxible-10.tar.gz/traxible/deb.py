from traxible.traxodule import Traxodule


class Deb(Traxodule):
    def update(self):
        self.run(["sudo apt update", "sudo apt upgrade -y"])

    def install(self, packages):
        self.run([f"sudo apt install -y {packages}"])
