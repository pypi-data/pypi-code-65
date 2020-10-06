#!/usr/bin/env python3

from http import HTTPStatus
from logging import getLogger
from signal import SIGTERM, signal
from socket import (
    AF_INET,
    IPPROTO_TCP,
    SHUT_RDWR,
    SO_KEEPALIVE,
    SOCK_STREAM,
    SOL_SOCKET,
    TCP_KEEPCNT,
    TCP_KEEPIDLE,
    TCP_KEEPINTVL,
    getaddrinfo,
    socket,
)
from threading import Timer, Thread, Event
from time import sleep, time
from wsgiref import simple_server

from ph_wsgiref.simple_server import WSGIRequestHandler
from psutil import cpu_times, Process

from .resource_balancer import ResourceBalancer
from .gating import wait_for_idle_cpus

LOGGER = getLogger("pothead.worker")


class Handler(WSGIRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, socket, address, server, cb_request_received):
        self.cb_request_received = cb_request_received
        super().__init__(socket, address, server)

    def handle_one_request(self):
        try:
            super().handle_one_request()
        finally:
            self.close_connection = True

    def parse_request(self):
        success = super().parse_request()

        # This socket shall no longer be fast-closed on SIGTERM
        socket = self.request
        self.server.sockets_waiting_for_request.remove(socket)

        if success and self.cb_request_received:
            self.cb_request_received(self.get_environ())

        return success

    def log_message(self, format, *args):
        LOGGER.info(format, *args)

    def log_request(self, code="-", size="-"):
        if isinstance(code, HTTPStatus):
            code = code.value
        LOGGER.info('"%s" %s %s', self.requestline, str(code), str(size))

    def log_error(self, format, *args):
        LOGGER.error(format, *args)


class Server:
    ssl_context = None
    multithread = False
    multiprocess = False
    server_address = "localhost"
    passthrough_errors = False
    shutdown_signal = False
    running = True

    def __init__(self, addr, app):
        (host, port) = addr
        # Set up base environment
        env = self.base_environ = {}
        env["SERVER_NAME"] = host
        env["GATEWAY_INTERFACE"] = "HTTP/1.1"
        env["SERVER_PORT"] = port
        env["REMOTE_HOST"] = ""
        env["CONTENT_LENGTH"] = ""
        env["SCRIPT_NAME"] = ""

        self.balancer = LoadBalancer(host, port)
        self.app = app
        self.sockets_waiting_for_request = set()

    def worker(self):
        while self.running:
            self._fetch_and_run_one_job()

    def _fetch_and_run_one_job(self, cb_request_received=None):
        with socket(AF_INET, SOCK_STREAM) as s, self.balancer.acquire_addr() as addr:
            self.sockets_waiting_for_request.add(s)
            try:
                s.connect(addr)

                s.setsockopt(SOL_SOCKET, SO_KEEPALIVE, 1)
                s.setsockopt(IPPROTO_TCP, TCP_KEEPIDLE, 1)
                s.setsockopt(IPPROTO_TCP, TCP_KEEPINTVL, 2)
                s.setsockopt(IPPROTO_TCP, TCP_KEEPCNT, 3)
            except Exception as e:
                LOGGER.error("Connect To Broker: %s", e)
                sleep(2)
                return

            try:
                Handler(s, addr, self, cb_request_received)
            except:
                LOGGER.exception("In WSGI request handling")
                sleep(1)
                return

    def get_app(self):
        return self.app

    def shutdown(self):
        LOGGER.info("shutting down workers...")
        self.running = False
        for s in list(self.sockets_waiting_for_request):
            s.shutdown(SHUT_RDWR)
            s.close()

    def poll_loop(self):
        """Uses app.wait_for_slot() spawn new workers dynamically. This is useful, for example to wait for
        enough CPU, memory, or disk space, to start next job.

        `wait_for_slot` is expected to block until it's time to poll for a new job. It is given a function
        `halt` which it should polle intermittently to check if this worker is undergoing `shutdown()`.

        It may return an object, if so `obj.request_received(environ)` will be called when a request is
        received and `obj.done()` when either the request is received, or if polling failed in which case
        `request_received()` was never called.

        See pothead.gating for some ready-made `wait_for_slot` implementations"""

        while self.running:
            callbacks = self.app.wait_for_slot(lambda: not self.running)
            if not self.running:
                break

            event = Event()
            t = Thread(target=self._run_one_poll, args=(event, callbacks))
            t.start()
            event.wait()

    def _run_one_poll(self, event, callbacks):
        def request_received(environ):
            event.set()
            next = getattr(callbacks, 'request_received', None)
            if next:
                next(environ)

        try:
            self._fetch_and_run_one_job(request_received)
        finally:
            event.set()
            if hasattr(callbacks, "done"):
                callbacks.done()


def install_term_handler(f):
    previous = []

    def on_term(_signal, _stack):
        f()
        for p in previous:
            p()

    p = signal(SIGTERM, on_term)
    if p:
        previous.append(p)


class LoadBalancer:
    REFRESH_INTERVAL = 5

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self._balancer = ResourceBalancer()
        self.refresh()

    def acquire_addr(self):
        return self._balancer.acquire()

    def refresh(self):
        try:
            results = getaddrinfo(self.host, self.port, type=SOCK_STREAM)
            hosts = (sockaddr for _f, _t, _p, _c, sockaddr in results)
            self._balancer.provision(hosts)
        except:
            LOGGER.exception(
                "Failed to refresh endpoints for %s:%d", self.host, self.port
            )
        t = Timer(self.REFRESH_INTERVAL, self.refresh)
        t.setDaemon(True)
        t.start()


demo_app = simple_server.demo_app
demo_app.wait_for_slot = wait_for_idle_cpus(3)


if __name__ == "__main__":
    from argparse import ArgumentParser
    from importlib import import_module
    from logging import INFO, basicConfig
    from os import environ
    from sys import path
    from threading import Thread

    path.insert(0, ".")

    def address(str):
        (host, port) = str.rsplit(":", 1)
        return (host, int(port))

    def func(str):
        (module, symbol) = str.rsplit(":", 1)
        module = import_module(module)
        return getattr(module, symbol)

    DEFAULT_WORKERS = int(environ.get("POTHEAD_WORKERS", 1))

    parser = ArgumentParser(description="Run WSGI app in sequential `worker` mode")
    parser.add_argument(
        "--connect",
        default="localhost:4040",
        type=address,
        help="Load Balancer Hub to connect to [host:port]",
    )
    job_control_group = parser.add_mutually_exclusive_group()
    job_control_group.add_argument(
        "--workers",
        default=DEFAULT_WORKERS,
        type=int,
        help="Number of worker Processes",
    )
    job_control_group.add_argument(
        "--poll-jobs",
        action="store_true",
        help="Use `app.wait_for_slot` to determine when to pull new jobs",
    )

    parser.add_argument(
        "app",
        nargs="?",
        default="pothead.worker:demo_app",
        type=func,
        help="The WSGI request handler to handle requests",
    )
    args = parser.parse_args()
    basicConfig(level=INFO)

    LOGGER.info("Initializing server for app %s", args.app)

    server = Server(args.connect, args.app)

    install_term_handler(server.shutdown)

    if args.poll_jobs:
        LOGGER.info(
            "Starting up job-polling dynamic workers connecting to %s", args.connect
        )
        server.poll_loop()
    else:
        LOGGER.info(
            "Starting up %d workers connecting to %s", args.workers, args.connect
        )
        workers = [Thread(target=server.worker) for _ in range(args.workers)]
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()

    LOGGER.info("shut down")
