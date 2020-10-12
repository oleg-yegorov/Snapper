import asyncio
from uuid import uuid4


class Task:
    def __init__(self, urls, task_timeout_sec):
        self.urls = urls
        self.id = str(uuid4())
        self.status = "running"
        self.result = {}
        self.task_timeout_sec = task_timeout_sec

    def run(self):
        process_urls_task = asyncio.create_task(self.process_urls())
        asyncio.create_task(self.delete_task(process_urls_task))

    def to_dict(self):
        pass

    async def process_urls(self):
        pass

    async def delete_task(self, process_urls_task):
        sleep_task = asyncio.sleep(self.task_timeout_sec)
        await asyncio.wait([sleep_task, process_urls_task], return_when=asyncio.ALL_COMPLETED)

        self.status = "deleted"
        self.result = {}

        await self.cleanup()

    async def cleanup(self):
        pass
