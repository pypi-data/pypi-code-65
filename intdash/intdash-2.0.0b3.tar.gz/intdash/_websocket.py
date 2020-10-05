# Copyright 2020 Aptpod, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import io
import warnings
from urllib import parse

from debtcollector import removals
from tornado import gen, httpclient, locks, queues, websocket

import intdash
from intdash import _client, _utils, protocol


class StreamAlreadyOpenException(Exception):
    pass


class ResultNGException(Exception):
    pass


__all__ = ["WebSocketConn"]


class WebSocketConn(object):
    """WebSocket 接続を表すオブジェクトです。"""

    def _init(self, client, flush_interval, auto_reconnect):
        self._client = client
        httpurl = parse.urlparse(client.url)
        scheme = "wss" if httpurl.scheme == "https" else "ws"
        self._wsurl = parse.urlunparse(
            [
                scheme,
                httpurl.netloc,
                "/api/v1/ws/measurements",
                httpurl.params,
                parse.urlencode({}),
                httpurl.fragment,
            ]
        )

        self._flush_interval = flush_interval
        self._next_stream_id = cyclic_counter256(initial=1)
        self._next_req_id = cyclic_counter256(initial=0)

        self._auto_reconnect = auto_reconnect
        self._disconnected = locks.Event()
        self._reconnecting = locks.Event()

        self._quit = locks.Event()

        self._rx_queues = {}
        self._tx_queue = queues.Queue()
        self._req_queues = {}

        self._downstreams = None
        self._upstreams = None

        self._writer = None
        self._conn = None
        self._connect()

    @gen.coroutine
    def _connect(self):
        while True:
            try:
                self._client._auth()
                headers = {
                    "Content-Type": "application/json; charset=utf-8",
                    "User-Agent": _client.USER_AGENT,
                }

                if self._client.edge_token is not None:
                    headers["X-Edge-Token"] = self._client.edge_token

                else:
                    headers["Authorization"] = "Bearer " + self._client.jwt

                req = httpclient.HTTPRequest(
                    url=self._wsurl, headers=headers, user_agent=_client.USER_AGENT
                )

                self._conn = yield websocket.websocket_connect(
                    url=req, ping_interval=10
                )
                self._reconnecting.clear()
                break

            except Exception as e:
                warnings.warn(Warning(e))
                yield gen.sleep(1.0)

        self._tx_routine()
        self._rx_routine()
        self._flush_routine()
        self._check_connection()

    @gen.coroutine
    def _check_connection(self):
        if not self._auto_reconnect:
            while not self._quit.is_set():
                if self._reconnecting.is_set():
                    self.close()

                else:
                    yield gen.sleep(1.0)
                    continue

        else:
            while not self._quit.is_set():
                if self._reconnecting.is_set():
                    self._quit.set()

                    self._tx_queue.join()
                    for q in self._rx_queues.values():
                        q.join()
                    for q in self._req_queues.values():
                        q.join()

                    if self._upstreams is not None:
                        self._upstreams._stop()

                    if self._downstreams is not None:
                        self._downstreams._stop()

                    self._quit.clear()
                    self._connect()

                    while self._reconnecting.is_set():
                        yield gen.sleep(0.1)

                    if self._upstreams is not None:
                        self._upstreams._open()

                    if self._downstreams is not None:
                        self._downstreams._open()

                    break

                else:
                    yield gen.sleep(1.0)
                    continue

    @gen.coroutine
    def _flush_routine(self):
        bio = io.BytesIO()
        bwr = io.BufferedWriter(bio)
        self._writer = protocol.Writer(bwr)

        while not self._quit.is_set():
            yield gen.sleep(self._flush_interval)

            if len(bio.getvalue()) == 0:
                yield gen.sleep(0.1)
                continue

            if self._conn is None:
                yield gen.sleep(0.1)
                continue

            try:
                msg = bio.getvalue()
                yield self._conn.write_message(message=msg, binary=True)

            except websocket.WebSocketClosedError as e:
                self._reconnecting.set()
                break

            except AttributeError:
                break

            bio = io.BytesIO()
            bwr = io.BufferedWriter(bio)
            self._writer = protocol.Writer(bwr)

    @gen.coroutine
    def _tx_routine(self):
        while not self._quit.is_set():
            if self._writer is None:
                yield gen.sleep(0.1)
                continue

            unit = yield self._tx_queue.get()
            self._writer.write_elem(unit)
            self._tx_queue.task_done()

    @gen.coroutine
    def _rx_routine(self):
        while not self._quit.is_set():
            if self._conn is None:
                yield gen.sleep(0.1)
                continue

            data = yield self._conn.read_message()
            if data is None:
                self._reconnecting.set()
                break

            bio = io.BytesIO(data)
            brd = io.BufferedReader(bio)
            rd = protocol.Reader(brd)

            while not self._quit.is_set():
                try:
                    e = rd.read_elem()
                    if isinstance(e, protocol.StreamElement):
                        yield self._rx_queues[e.stream_id].put(e)

                    elif isinstance(e, protocol.RequestElement):
                        yield self._req_queues[e.req_id].put(e)

                except EOFError:
                    break

                except KeyError:
                    continue

    def close(self):
        """WebSocket接続を閉じます。"""
        self._quit.set()

        if self._upstreams is not None:
            self._upstreams._stop()

        if self._downstreams is not None:
            self._downstreams._stop()

        self._tx_queue.join()
        for q in self._rx_queues.values():
            q.join()
        for q in self._req_queues.values():
            q.join()

        self._conn.close()

    def open_downstreams(self, specs, callbacks):
        """指定したダウンストリームスペックに従ってダウンストリームを開きます。

        Args:
            specs (list[DownstreamSpec]): ダウンストリームスペックのリスト
            callbacks (list[func]): 受信したUnitを処理する際に呼ばれるコールバック関数
        """
        if self._downstreams is not None:
            raise StreamAlreadyOpenException()

        self._downstreams = Downstreams(conn=self, specs=specs, callbacks=callbacks)

    def open_upstreams(self, specs, iterators, marker_interval=3):
        """指定したアップストリームスペックに従ってアップストリームを開きます。

        Args:
            specs (list[UpstreamSpec]): アップストリームスペックのリスト
            iterators (list[iter]): 送信するUnitを生成する際に呼ばれるイテレータ
            marker_interval (int): 秒単位のマーカー間隔
        """
        if self._upstreams is not None:
            raise StreamAlreadyOpenException()

        self._upstreams = Upstreams(
            conn=self, specs=specs, iterators=iterators, marker_interval=marker_interval
        )


class Downstreams(object):
    def __init__(self, conn, specs, callbacks):
        self.conn = conn
        self.quit = locks.Event()

        # NOTE: asign stream_id using self.conn._stream_id method
        self.specs = {}
        self.callbacks = {}
        for spec, callback in zip(specs, callbacks):
            stream_id = self.conn._next_stream_id()
            self.specs[stream_id] = spec
            self.callbacks[stream_id] = callback

        self._open()

    def _stop(self):
        self.quit.set()

        for stream_id, spec in self.specs.items():
            self.conn._rx_queues[stream_id].join()
            del self.conn._rx_queues[stream_id]

    @gen.coroutine
    def _open(self):
        self.quit.clear()

        for stream_id, spec in self.specs.items():
            self.conn._rx_queues[stream_id] = queues.Queue()

        reqs = _utils._create_req_downstream(specs=self.specs)
        for req in reqs:
            req.req_id = self.conn._next_req_id()
            self.conn._req_queues[req.req_id] = queues.Queue()
            yield self.conn._tx_queue.put(req)

        for req in reqs:
            q = self.conn._req_queues[req.req_id]
            resp = yield q.get()
            del self.conn._req_queues[req.req_id]
            q.task_done()
            if resp.result_code != protocol.ResultCode.OK:
                raise ResultNGException()

        self._receiving()

    @gen.coroutine
    def _receiving(self):
        @gen.coroutine
        def _routine(q, spec, callback):
            while not self.quit.is_set():
                unit = yield q.get()
                callback(
                    intdash.Unit(
                        elapsed_time=unit.elapsed_time,
                        channel=unit.channel,
                        data=unit.data,
                    )
                )
                q.task_done()

        for stream_id, spec in self.specs.items():
            _routine(
                self.conn._rx_queues[stream_id],
                self.specs[stream_id],
                self.callbacks[stream_id],
            )


class Upstreams(object):
    def __init__(self, conn, specs, iterators, marker_interval):
        self.conn = conn
        self.quit = locks.Event()
        self.marker_interval = marker_interval

        # NOTE: asign stream_id using self.conn._stream_id method
        self.specs = {}
        self.iterators = {}
        for spec, iterator in zip(specs, iterators):
            stream_id = self.conn._next_stream_id()
            self.specs[stream_id] = spec
            self.iterators[stream_id] = iterator

        self.stream_infos = {}
        self._open()

    def _stop(self):
        self.quit.set()

        for stream_id, spec in self.specs.items():
            self.conn._rx_queues[stream_id].join()
            del self.conn._rx_queues[stream_id]

    @gen.coroutine
    def _open(self):
        self.quit.clear()

        for stream_id, spec in self.specs.items():
            self.conn._rx_queues[stream_id] = queues.Queue()

        self.stream_infos = {}
        for stream_id, spec in self.specs.items():
            self.stream_infos[stream_id] = StreamInfo()

        reqs = _utils._create_req_upstream(specs=self.specs)
        for req in reqs:
            req.req_id = self.conn._next_req_id()
            self.conn._req_queues[req.req_id] = queues.Queue()
            yield self.conn._tx_queue.put(req)

        for req in reqs:
            q = self.conn._req_queues[req.req_id]
            resp = yield q.get()
            del self.conn._req_queues[req.req_id]
            q.task_done()
            if resp.result_code != protocol.ResultCode.OK:
                raise ResultNGException()

        self._check_section()
        self._add_section()
        self._sending()

    @gen.coroutine
    def _check_section(self):
        @gen.coroutine
        def _routine(q):
            while not self.quit.is_set():
                ack = yield q.get()
                q.task_done()

        for stream_id, spec in self.specs.items():
            _routine(self.conn._rx_queues[stream_id])

    @gen.coroutine
    def _add_section(self):
        @gen.coroutine
        def _routine(stream_id):
            stream_info = self.stream_infos[stream_id]

            while not self.quit.is_set():
                yield gen.sleep(self.marker_interval)

                if stream_info.count == 0:
                    continue

                yield self.conn._tx_queue.put(
                    protocol.EOSMarker(
                        stream_id=stream_id,
                        final=False,
                        serial_number=stream_info.serial,
                    )
                )

                stream_info.next_serial()
                yield self.conn._tx_queue.put(
                    protocol.SOSMarker(
                        stream_id=stream_id, serial_number=stream_info.serial
                    )
                )

        for stream_id, spec in self.specs.items():
            self.conn._tx_queue.put(
                protocol.SOSMarker(
                    stream_id=stream_id,
                    serial_number=self.stream_infos[stream_id].serial,
                )
            )

        for stream_id, spec in self.specs.items():
            _routine(stream_id)

    @gen.coroutine
    def _sending(self):
        @gen.coroutine
        def _routine(stream_id, iter):
            while not self.quit.is_set():
                try:
                    unit = next(iter)
                    yield
                except StopIteration:
                    break
                if unit is None:
                    continue

                self.stream_infos[stream_id].count_up()
                u = protocol.Unit(
                    stream_id=stream_id,
                    channel=unit.channel,
                    elapsed_time=unit.elapsed_time,
                    data=unit.data,
                )
                yield self.conn._tx_queue.put(u)

        for stream_id, spec in self.specs.items():
            _routine(stream_id, self.iterators[stream_id])


class StreamInfo(object):
    def __init__(self):
        self.count = 0
        self.serial = 0

    def count_up(self):
        self.count += 1

    def next_serial(self):
        self.count = 0
        self.serial += 1


def cyclic_counter256(initial):
    cnt = initial

    def inner():
        nonlocal cnt
        next = cnt
        cnt = (cnt + 1) % 256
        return next

    return inner
