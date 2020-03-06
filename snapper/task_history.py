import asyncio
import base64
import datetime
import logging
import os
import shutil
import time
from pathlib import Path
from uuid import uuid4

from snapper.s3 import S3


class TaskHistory:
    tasks = {}

    def __init__(self, urls, output, output_paths_format, task_lifetime_sec=86400):
        self.urls = urls
        self.id = str(uuid4())
        self.result = {url: {} for url in urls }
        self.status = "running"
        self.output_path = Path.cwd() / output / self.id
        self.output_paths_format = output_paths_format
        self.task_lifetime_sec = task_lifetime_sec

        os.makedirs(self.output_path)
        TaskHistory.tasks[self.id] = self

    def to_dict(self):
        result = {
            url: {
                self.output_paths_format.format(screenshot): created
                for screenshot, created in screenshots.items()
            }
            for url, screenshots in self.result.items()
        }

        return {
            "id": self.id,
            "status": self.status,
            "result": result
        }

    def run(self):
        asyncio.create_task(self.process_urls())
        asyncio.create_task(self.delete_task())

    async def process_urls(self):
        if not S3.get_instance():
            self.status = 'ready'
            return

        async with S3.get_instance().get_async_client() as s3_client:
            for url in self.urls:
                s3_url_dir = base64.b64encode(url.encode('UTF-8')).decode('UTF-8')

                for object in await S3.get_instance().list_objects(s3_client, s3_url_dir):
                    path = object.split('/')
                    if len(path) != 3 or path[2] != 'screenshot.png':
                        continue
                    try:
                        s3_scr_dir = path[1]
                        s3_scr_timestamp = datetime.datetime.strptime(s3_scr_dir, "%Y-%m-%dT%H:%M:%S")
                        s3_scr_timestamp_posix = int(time.mktime(s3_scr_timestamp.timetuple()))

                        local_scr_filename = str(uuid4()) + '.png'
                        local_scr_path = Path(self.output_path) / local_scr_filename
                        await S3.get_instance().download_object(s3_client, object,
                                                                str(self.output_path / local_scr_filename))

                        self.result[url][str(local_scr_path)] = s3_scr_timestamp_posix
                    except ValueError as e:
                        logging.error('s3 object %s: %s' % (object, str(e)))

            self.status = 'ready'

    async def delete_task(self):
        await asyncio.sleep(self.task_lifetime_sec)

        shutil.rmtree(self.output_path)
        del TaskHistory.tasks[self.id]
