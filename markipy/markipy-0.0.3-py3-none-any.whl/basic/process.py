from pathlib import Path
import asyncio
from asyncio.subprocess import PIPE

from .perf import Performance
from .logger import Logger

_process_ = {'class': 'Process', 'version': 4}


class Process(Logger):

    def __init__(self, process_name, cmd=None, console=False):
        Logger.__init__(self, console=console, file_log=f'Process.{process_name}')
        self._init_atom_register_class(_process_)
        self.proc = None
        self.loop = None
        self.cmd = cmd

    def _clean_out_line(self, line):
        return str(line, 'utf-8').replace('\r', '').replace('\n', '')

    async def _read_stream(self, stream, cb):
        while True:
            line = await stream.readline()
            if line:
                cb(self._clean_out_line(line))
            else:
                break

    async def _stream_subprocess(self, cmd):
        process = await asyncio.create_subprocess_exec(*cmd, stdout=PIPE, stderr=PIPE)
        await asyncio.wait([self._read_stream(process.stdout, self.stdout_callback),
                            self._read_stream(process.stderr, self.stderr_callback)])
        return await process.wait()

    def stdout_callback(self, line):
        self.log.debug(line)

    def stderr_callback(self, line):
        self.log.error(line)

    @Performance.collect
    def execute(self, cmd):
        self.log.debug(f'Process executing: {self.cyan(cmd)}')
        self.loop = asyncio.get_event_loop()
        rc = self.loop.run_until_complete(self._stream_subprocess(cmd))
        return rc

    def start(self):
        if self.cmd:
            self.execute(self.cmd)
