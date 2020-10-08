#!/bin/env python
"""Reference Implementation of v1 C3 Security Beacon Auth Server."""
from aiohttp import web
import aiohttp_cors
import asyncio
import os
import signal

import click

from ..db import init_db, init_db_pool
from .listeners import ListenersView, ListenerView
from .proximity import ProximityView
from .tags import TagsView, TagView
from .zones import ZonesView, ZoneView
from .groups import GroupsView, GroupView
from ..demo_fe.main import app as demo_fe_app


@click.command()
@click.option('--port', '-p', default=5000)
@click.option('--reset-db', is_flag=True, default=False)
@click.option('--demo-fe', is_flag=True, default=True)
def main(port, reset_db, demo_fe) -> None:
    loop = asyncio.get_event_loop()
    if signal is not None and os.name != 'nt':
        loop.add_signal_handler(signal.SIGINT, loop.stop)

    async def init_db_app(app):
        pool = await init_db_pool()
        await init_db(pool, reset_db)
        app['db_pool'] = pool

    app = web.Application()
    app.on_startup.append(init_db_app)
    app.router.add_view('/api/listeners', ListenersView)
    app.router.add_view('/api/listeners/{id:\w+}', ListenerView, name='listener')
    app.router.add_view('/api/zones', ZonesView)
    app.router.add_view('/api/zones/{id:\d+}', ZoneView, name='zone')
    app.router.add_view('/api/tags', TagsView)
    app.router.add_view('/api/tags/{id:\d+}', TagView, name='tag')
    app.router.add_view('/api/proximity', ProximityView)
    app.router.add_view('/api/groups', GroupsView)
    app.router.add_view('/api/groups/{id:\d+}', GroupView, name='group')

    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    for route in list(app.router.routes()):
        cors.add(route)

    if demo_fe:
        app.add_subapp('/demo', demo_fe_app)
    web.run_app(app, port=port)


if __name__ == '__main__':
    main()
