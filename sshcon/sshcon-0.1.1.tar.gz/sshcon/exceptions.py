class SshConNonZeroReturnCode(Exception):
    def __init__(self, cmd, rcode, stderr):
        self.cmd = cmd
        self.rcode = rcode
        self.stderr = stderr

    def __str__(self):
        return f"Command:{self.cmd}, RC:{self.rcode} -> {self.stderr}."


class SshConSftpError(Exception):
    def __init__(self, cmd, rcode):
        self.cmd = cmd
        self.rcode = rcode

    def __str__(self):
        return f"Function:{self.cmd}, RC:{self.rcode} -> Function has failed."


class SshConError(Exception):
    def __init__(self, function, msg):
        self.function = function
        self.msg = msg

    def __str__(self):
        return f"Function:{self.function} -> {self.msg}"
