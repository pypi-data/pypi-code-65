#!/usr/bin/env python
#  -*- coding: utf-8 -*-


import json
import lzma
import os
import threading
import asyncio
import urllib

import websockets
from aiohttp import web

class MockInsServer():
    def __init__(self, port):
        self.loop = asyncio.new_event_loop()
        self.port = port
        self.symbols_dir = os.path.join(os.path.dirname(__file__), 'symbols')
        self.stop_signal = self.loop.create_future()
        self.semaphore = threading.Semaphore(value=0)
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        self.semaphore.acquire()

    def close(self):
        self.loop.call_soon_threadsafe(lambda: self.stop_signal.set_result(0))
        self.thread.join()

    async def handle(self, request):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(dir_path, "symbols", request.url.name + ".lzma")
        file = lzma.open(file_path, "rt", encoding="utf-8")
        return web.json_response(json.loads(file.read()))

    async def auth_handle(self, request):
        """
        对于 mock auth 服务， 只有 auth="tianqin,tianqin" 是收费全功能用户，其他是免费用户
        """
        query_str = await request.text()
        query = urllib.parse.parse_qs(query_str)
        if query["username"][0] == "tianqin" and query["password"][0] == "tianqin":
            s = '{"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJobi1MZ3ZwbWlFTTJHZHAtRmlScjV5MUF5MnZrQmpLSFFyQVlnQ0UwR1JjIn0.eyJqdGkiOiJkODJmMzQ3OS1jNTU5LTQxNDEtOGUwYS00NTlmMTcyY2NiNzUiLCJleHAiOjE2MzEyNDE3MzQsIm5iZiI6MCwiaWF0IjoxNTk5NzA1NzM0LCJpc3MiOiJodHRwczovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsInN1YiI6IjBkZWRkNTFhLTI4MjYtNDZkMC1hZjgyLTBlMjZmZmNiNTYyNSIsInR5cCI6IkJlYXJlciIsImF6cCI6InNoaW5ueV90cSIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6IjBiZjM0MDcyLWU4MjQtNDk0MC1hZWY2LTE5NjQ4Yjg0NzFjMCIsImFjciI6IjEiLCJzY29wZSI6ImF0dHJpYnV0ZXMtZ3JhbnQtdHEgcHJvZmlsZSB1c2VybmFtZSIsImdyYW50cyI6eyJmZWF0dXJlcyI6WyJzZWMiLCJhZHYiLCJtYyIsInRxX2RsIiwib3B0IiwiY21iIiwibG10X2lkeCIsInN1cCIsInRxX2J0IiwiZnV0ciIsInRxX21hIl0sImV4cGlyeV9kYXRlIjoiMCIsImFjY291bnRzIjpbIjEwMzk4OCIsIjkwMTAxMDg3IiwiMDAwMTk5IiwiODMwMTExMTkiLCIwZGVkZDUxYS0yODI2LTQ2ZDAtYWY4Mi0wZTI2ZmZjYjU2MjUiLCI5MDA5MjMwNyIsIioiXX0sInNldG5hbWUiOnRydWUsIm5hbWUiOiJOVUxMIE5VTEwiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJtYXlhbnFpb25nMSIsImlkIjoiMGRlZGQ1MWEtMjgyNi00NmQwLWFmODItMGUyNmZmY2I1NjI1IiwiZ2l2ZW5fbmFtZSI6Ik5VTEwiLCJmYW1pbHlfbmFtZSI6Ik5VTEwiLCJ1c2VybmFtZSI6Im1heWFucWlvbmcxIn0.en9vKhjS4FX1DG2r3sfA3I0a8NQsOrZl_dPqBSydw3SiEzwoN21T2FUfUz7BzJ1WXDIMauYWSvaLr0IVRSafC715B4gmQ_24iy7S2T7OD7MECsdnQq2jzynCEsIEe4jhfBtn5vOZeVV2q2woBmYFcpYbIQjr4F60o0I5vddd7lo1kFUfLi8AkPYRRUDZ0qG8dAYKIYvewq40OS_QbrHU4JJDkFIyFMqlCkhed2b0zZanaDILuvEc190WkFs8IuKeQklZ_ZcBDUVHDD3kgKk7yErxySnWIvc0PY9oSg0rEsXG_eAS0ksnBfYtnN_CFbOwM4S2xkpuZxlFzE-hEudezQ","expires_in":31536000,"refresh_expires_in":7776000,"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmZDNjMjQwYS00ODcyLTRiYTAtODNlZC04OGRjNWU4ZDE2ODAifQ.eyJqdGkiOiJkZmEyNDIxNi1jZDljLTRlMTYtODMyNC1iNTQyNDA2MmU0ZTQiLCJleHAiOjE2MDU2NjQ3NTEsIm5iZiI6MCwiaWF0IjoxNTk3ODg4NzUxLCJpc3MiOiJodHRwczovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsImF1ZCI6Imh0dHBzOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwic3ViIjoiMGRlZGQ1MWEtMjgyNi00NmQwLWFmODItMGUyNmZmY2I1NjI1IiwidHlwIjoiUmVmcmVzaCIsImF6cCI6InNoaW5ueV90cSIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6IjdlMGMwYjE5LWJjYjUtNDdmMC1iYTI1LWQxODIwNzQ5OTVlMSIsInNjb3BlIjoiYXR0cmlidXRlcy1ncmFudC10cSBwcm9maWxlIHVzZXJuYW1lIn0.bwcuZ1fFmTsCrYNyAPD6P8b7mYOpcB9_2oLKaH-QoUY","token_type":"bearer","not-before-policy":0,"session_state":"7e0c0b19-bcb5-47f0-ba25-d182074995e1","scope":"attributes-grant-tq profile username"}'
        else:
            s = '{"access_token":"eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJobi1MZ3ZwbWlFTTJHZHAtRmlScjV5MUF5MnZrQmpLSFFyQVlnQ0UwR1JjIn0.eyJqdGkiOiI2YTFhZmE0MC1lMDczLTRhMmQtODljYy04MDFmZmRkMjgxM2YiLCJleHAiOjE2Mjk0MjQ3NDAsIm5iZiI6MCwiaWF0IjoxNTk3ODg4NzQwLCJpc3MiOiJodHRwczovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsInN1YiI6IjcwZTQ0YWU1LTY0YjgtNDdlMC1iYjU0LWE1ZWVkY2RjZDM3YyIsInR5cCI6IkJlYXJlciIsImF6cCI6InNoaW5ueV90cSIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFmOWNjZDNhLTI1MDktNGUzOC04MTBiLThjNjE4YWQzNmFjYiIsImFjciI6IjEiLCJzY29wZSI6ImF0dHJpYnV0ZXMtZ3JhbnQtdHEgcHJvZmlsZSB1c2VybmFtZSIsImdyYW50cyI6eyJmZWF0dXJlcyI6WyJmdXRyIiwibG10X2lkeCJdLCJleHBpcnlfZGF0ZSI6IjAiLCJhY2NvdW50cyI6WyI3MGU0NGFlNS02NGI4LTQ3ZTAtYmI1NC1hNWVlZGNkY2QzN2MiLCIxMDM5ODgiLCIqIl19LCJzZXRuYW1lIjp0cnVlLCJuYW1lIjoieWFucWlvbmcgTWEiLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJlbGl6YWJldGhtYSIsImlkIjoiNzBlNDRhZTUtNjRiOC00N2UwLWJiNTQtYTVlZWRjZGNkMzdjIiwiZ2l2ZW5fbmFtZSI6InlhbnFpb25nIiwiZmFtaWx5X25hbWUiOiJNYSIsInVzZXJuYW1lIjoiZWxpemFiZXRobWEifQ.en9vKhjS4FX1DG2r3sfA3I0a8NQsOrZl_dPqBSydw3SiEzwoN21T2FUfUz7BzJ1WXDIMauYWSvaLr0IVRSafC715B4gmQ_24iy7S2T7OD7MECsdnQq2jzynCEsIEe4jhfBtn5vOZeVV2q2woBmYFcpYbIQjr4F60o0I5vddd7lo1kFUfLi8AkPYRRUDZ0qG8dAYKIYvewq40OS_QbrHU4JJDkFIyFMqlCkhed2b0zZanaDILuvEc190WkFs8IuKeQklZ_ZcBDUVHDD3kgKk7yErxySnWIvc0PY9oSg0rEsXG_eAS0ksnBfYtnN_CFbOwM4S2xkpuZxlFzE-hEudezQ","expires_in":31536000,"refresh_expires_in":7776000,"refresh_token":"eyJhbGciOiJIUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJmZDNjMjQwYS00ODcyLTRiYTAtODNlZC04OGRjNWU4ZDE2ODAifQ.eyJqdGkiOiIxNzMyYmU1ZS02ZmY2LTQ0NGQtOGIzMC0xNzFlODhmNTQyYjUiLCJleHAiOjE2MDU2NjQ3NDAsIm5iZiI6MCwiaWF0IjoxNTk3ODg4NzQwLCJpc3MiOiJodHRwczovL2F1dGguc2hpbm55dGVjaC5jb20vYXV0aC9yZWFsbXMvc2hpbm55dGVjaCIsImF1ZCI6Imh0dHBzOi8vYXV0aC5zaGlubnl0ZWNoLmNvbS9hdXRoL3JlYWxtcy9zaGlubnl0ZWNoIiwic3ViIjoiNzBlNDRhZTUtNjRiOC00N2UwLWJiNTQtYTVlZWRjZGNkMzdjIiwidHlwIjoiUmVmcmVzaCIsImF6cCI6InNoaW5ueV90cSIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImFmOWNjZDNhLTI1MDktNGUzOC04MTBiLThjNjE4YWQzNmFjYiIsInNjb3BlIjoiYXR0cmlidXRlcy1ncmFudC10cSBwcm9maWxlIHVzZXJuYW1lIn0.Zuq-TsXC0D_rtk07JR1Dhd_iYNLxd5xg1s4jSrEZLBw","token_type":"bearer","not-before-policy":0,"session_state":"af9ccd3a-2509-4e38-810b-8c618ad36acb","scope":"attributes-grant-tq profile username"}'
        return web.json_response(text=s)

    async def task_serve(self):
        try:
            app = web.Application()
            app.add_routes([web.get('/t/md/symbols/{tail:.*}', self.handle)])
            app.add_routes([web.post('/auth/realms/shinnytech/protocol/openid-connect/token', self.auth_handle)])
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '127.0.0.1', self.port)
            await site.start()
            self.semaphore.release()
            await self.stop_signal
        finally:
            await runner.shutdown()
            await runner.cleanup()

    def _run(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.task_serve())


class MockServer():
    def __init__(self, td_url_character="opentd", md_url_character="openmd", md_port=5100, td_port=5200):
        self.loop = asyncio.new_event_loop()
        self.connections = {}
        self.server_md = None
        self.server_td = None
        self.md_port = md_port
        self.td_port = td_port
        self.md_url_character = md_url_character
        self.td_url_character = td_url_character
        self._expecting = {}
        self.stop_signal = self.loop.create_future()
        self.semaphore = threading.Semaphore(value=0)

    def close(self):
        assert not self._expecting
        self.loop.call_soon_threadsafe(lambda: self.stop_signal.set_result(0))
        self.thread.join()
        self.script_file.close()

    async def _handler_md(self, connection, path):
        await self.on_connected("md", connection)
        try:
            while True:
                s = await self.connections["md"].recv()
                pack = json.loads(s)
                await self.on_received("md", pack)
        except websockets.exceptions.ConnectionClosedOK as e:
            assert e.code == 1000

    async def _handler_td(self, connection, path):
        await self.on_connected("td", connection)
        try:
            while True:
                s = await self.connections["td"].recv()
                pack = json.loads(s)
                if pack["aid"] == "peek_message":
                    continue
                await self.on_received("td", pack)
        except websockets.exceptions.ConnectionClosedOK as e:
            assert e.code == 1000

    def run(self, script_file_name):
        self.script_file_name = script_file_name
        self.thread = threading.Thread(target=self._run)
        self.thread.start()
        self.semaphore.acquire()

    async def _server(self):
        async with websockets.serve(self._handler_md, "127.0.0.1", self.md_port) as self.server_md:
            async with websockets.serve(self._handler_td, "127.0.0.1", self.td_port) as self.server_td:
                self.semaphore.release()
                await self.stop_signal

    def _run(self):
        if str.endswith(self.script_file_name, "lzma"):
            self.script_file = lzma.open(self.script_file_name, "rt", encoding="utf-8")
        else:  # 用于本地script还未压缩成lzma文件时运行测试用例
            self.script_file = open(self.script_file_name, "rt", encoding="utf-8")
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._server())

    async def _process_script(self):
        # 每次处理日志文件中的一行, 直至需要输入为止
        self._expecting = {}
        for line in self.script_file:
            # 2019-09-09 16:22:40,652 - DEBUG - websocket message sent to wss://openmd.shinnytech.com/t/md/front/mobile: {"aid": "subscribe_quote",
            item = {}
            if "websocket message sent" in line and "peek_message" not in line:  # 在api角度的sent
                item["type"] = "sent"
            elif "websocket message received" in line:  # 在api角度的received
                item["type"] = "received"
            else:
                continue
            if self.md_url_character in line:
                item["source"] = "md"
            elif self.td_url_character in line:
                item["source"] = "td"
            else:
                raise Exception()
            content_start_pos = line.find("{")
            content = line[content_start_pos:]
            item["content"] = json.loads(content)
            if item["type"] == "sent":
                self._expecting = item
                break
            elif item["type"] == "received":
                msg = json.dumps(item["content"])
                assert self.connections[item["source"]]
                await self.connections[item["source"]].send(msg)

    async def on_connected(self, source, connection):
        self.connections[source] = connection
        # self._process_script()
        # assert self._expecting["source"] == source
        # assert self._expecting["action"] == "connected"

    async def on_received(self, source, pack):
        if not self._expecting:
            await self._process_script()
        if pack["aid"] != "peek_message":
            assert self._expecting["source"] == source
            if self._expecting["content"]["aid"] == "req_login" and pack["aid"] == "req_login":
                # 登录请求单独判断这几个字段，不同操作系统带的穿管信息的包内容不同
                assert self._expecting["content"]["bid"] == pack["bid"]
                assert self._expecting["content"]["user_name"] == pack["user_name"]
                assert self._expecting["content"]["password"] == pack["password"]
            else:
                assert self._expecting["content"] == pack
            await self._process_script()
