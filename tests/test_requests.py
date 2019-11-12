import time
from pathlib import Path

import pytest
import yaml
from aiohttp import web

from snapper.api_views import setup_routes


@pytest.fixture(scope="function")
def snapper_client(loop, aiohttp_client):
    config_filename = str(Path(__file__).parent.parent / 'snapper' / 'config.yaml')
    with open(config_filename, 'r') as config_file:
        config = yaml.safe_load(config_file)

    app = web.Application()
    app.update(config)

    setup_routes(app)
    yield loop.run_until_complete(aiohttp_client(app))


async def wait_for_all_tasks(snapper_client):
    while True:
        time.sleep(0.1)
        response = await snapper_client.get("/api/v1/tasks")

        if all(task['status'] == 'ready' for task in await response.json()):
            break


async def submit(snapper_client, urls):
    response = await snapper_client.post("/api/v1/submit", json={"urls": urls})
    return await response.json()


async def get_task(snapper_client, id):
    response = await snapper_client.get("/api/v1/tasks/" + id)
    return await response.json()


async def _test_url(snapper_client, url):
    response = await submit(snapper_client, [url])
    task_id = response['id']

    await wait_for_all_tasks(snapper_client)
    response = await get_task(snapper_client, task_id)
    return response['result']


async def test_url_with_no_scheme(snapper_client):
    result = await _test_url(snapper_client, "ya.ru")
    assert "ya.ru" in result


async def test_nonexistent_url(snapper_client):
    result = await _test_url(snapper_client, "https://ya1111.ru")
    assert "https://ya1111.ru" in result


async def test_null_body_element(snapper_client):
    result = await _test_url(snapper_client, "https://www.de.abbott/media-center/press-releases/05-10-2018.html")
    assert "https://www.de.abbott/media-center/press-releases/05-10-2018.html" in result
