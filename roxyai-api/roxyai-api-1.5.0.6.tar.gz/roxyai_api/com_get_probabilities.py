# (c) Roxy Corp. 2020-
# Roxy AI Analyze-Server API
import struct

from .com_definition import (
    Probability,
    CommandCode,
    CommandStatus,
)
from .com_base import BaseCommand


class GetProbabilitiesCommand(BaseCommand):

    _CODE = CommandCode.GET_PROBABILITIES
    PROB_SIZE = 13
    PROB_OFFSET = 2

    # ログの詳細出力
    verbose = False

    def __init__(
        self,
        inspect_id: int,
        connection=None,
    ):
        """ GetProbabilities コマンド制御

        Args:
            inspect_id (int):                   取得対象の検査番号
            connection (Connection, option):    通信対象のTCP接続
        """
        super().__init__(connection)
        self.inspect_id = inspect_id
        self.data = struct.pack(f'< Q', inspect_id)

    def _decode_reply(self, reply: bytes):
        """ Inspect コマンドの応答内容確認

        Args:
            reply (bytes):      受信応答データ（ヘッダ以外）
        """
        prob_size, = struct.unpack(
            '< H',
            reply[:self.PROB_OFFSET]
        )
        prob_data = reply[self.PROB_OFFSET:]

        # 受信データの格納
        self.prob_size = prob_size
        self.prob_list = []
        for offset in range(0, prob_size * self.PROB_SIZE, self.PROB_SIZE):
            x1, y1, x2, y2, typ, prob = struct.unpack(
                '< H H H H B f',
                prob_data[offset:offset + self.PROB_SIZE]
            )
            prob = Probability(x1, y1, x2, y2, typ, prob)
            self.prob_list.append(prob)

    def __str__(self):
        string = (
            f'{super().__str__()} '
            f'InspectID: {self.inspect_id}(=0x{self.inspect_id:#016X}) -> '
        )
        if self.is_received_ack:
            string += (
                f'ProbabilityList: {self.prob_size} items '
                f'({self.process_time} ms)'
            )
            if self.verbose:
                for prob in self.prob_list:
                    string += '\n    ' + str(prob)
        return string
