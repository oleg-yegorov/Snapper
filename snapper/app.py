from aiohttp import web

from snapper.api_views import setup_routes
from snapper.scheduler import Scheduler


async def create_app(config):
    app = web.Application()
    app.update(vars(config))
    setup_routes(app)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app


async def on_startup(app):
    Scheduler(app['workers'])


async def on_shutdown(app):
    Scheduler.get_instance().close()
