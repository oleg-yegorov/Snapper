from aiohttp import web

from snapper.api_views import setup_routes
from snapper.scheduler import Scheduler
from snapper.s3 import S3


async def create_app(config):
    app = web.Application()
    app.update(vars(config))
    setup_routes(app)

    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    return app


async def on_startup(app):
    Scheduler(app['workers'])

    if all([app['aws_access_key_id'], app['aws_secret_access_key'], app['aws_bucket_name']]):
        S3(app['aws_access_key_id'], app['aws_secret_access_key'], app['aws_bucket_name'])

async def on_shutdown(app):
    Scheduler.get_instance().close()
