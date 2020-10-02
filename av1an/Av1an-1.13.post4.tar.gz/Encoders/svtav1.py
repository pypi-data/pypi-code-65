import os
import re

from Av1an.arg_parse import Args
from Chunks.chunk import Chunk
from Av1an.commandtypes import MPCommands, CommandPair, Command
from Encoders.encoder import Encoder
from Av1an.utils import list_index_of_regex, terminate


class SvtAv1(Encoder):

    def __init__(self):
        super(SvtAv1, self).__init__(
            encoder_bin='SvtAv1EncApp',
            encoder_help='SvtAv1EncApp --help',
            default_args=['--preset', '4', '--rc', '0', '--qp', '25'],
            default_passes=1,
            default_q_range=(20, 40),
            output_extension='ivf'
        )

    def compose_1_pass(self, a: Args, c: Chunk, output: str) -> MPCommands:
        return [
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['SvtAv1EncApp', '-i', 'stdin', '--progress', '2', *a.video_params, '-b', output, '-']
            )
        ]

    def compose_2_pass(self, a: Args, c: Chunk, output: str) -> MPCommands:
        return [
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['SvtAv1EncApp', '-i', 'stdin', '--progress', '2', '--irefresh-type', '2', *a.video_params,
                 '-output-stat-file', f'{c.fpf}.stat', '-b', os.devnull, '-']
            ),
            CommandPair(
                Encoder.compose_ffmpeg_pipe(a),
                ['SvtAv1EncApp', '-i', 'stdin', '--progress', '2', '--irefresh-type', '2', *a.video_params,
                 '-input-stat-file', f'{c.fpf}.stat', '-b', output, '-']
            )
        ]

    def man_q(self, command: Command, q: int) -> Command:
        """Return command with new cq value

        :param command: old command
        :param q: new cq value
        :return: command with new cq value"""

        adjusted_command = command.copy()

        i = list_index_of_regex(adjusted_command, r"(--qp|-q)")
        adjusted_command[i + 1] = f'{q}'

        return adjusted_command

    def match_line(self, line: str):
        """Extract number of encoded frames from line.

        :param line: one line of text output from the encoder
        :return: match object from re.search matching the number of encoded frames"""
        if 'error' in line.lower():
            print('\n\nERROR IN ENCODING PROCESS\n\n', line)
            terminate()
        return re.search(r"Encoding frame\s+(\d+)", line)
