from fire import Fire
from fabric import Connection


class Traxible:
    """
    This is main module that allows basic remote operations
    sush as ssh connection, send command or files, reconnect, ...

    """

    def __init__(self, host):
        self.host = host
        self.conn = Connection(self.host)

    def run(self, commands, block=True):
        for command in commands:
            print("> ", command)
            try:
                result = self.conn.run(command)
                print(result.exited, "=" * 60)

            except Exception as error:
                if block is True:
                    raise error

    def put(self, source, destination, sudo=False):
        if sudo is False:
            return self.conn.put(source, destination)

        self.conn.put(source, "/tmp/efe9e3023a502013767a0559a94a5e")
        return self.run([f"sudo mv /tmp/efe9e3023a502013767a0559a94a5e {destination}"])

    def reconnect(self):
        self.conn.close()
        self.conn.open()


if __name__ == "__main__":
    Fire(Traxible)
