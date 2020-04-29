import os

from aiohttp import web

from snapper.api_views import setup_routes
from snapper.s3 import S3
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

    if all([os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'), app['aws_bucket_name']]):
        S3(os.getenv('AWS_ACCESS_KEY_ID'), os.getenv('AWS_SECRET_ACCESS_KEY'), app['aws_bucket_name'])


async def on_shutdown(app):
    pass
