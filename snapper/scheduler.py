import asyncio
import logging
from concurrent.futures import ProcessPoolExecutor


class Scheduler(ProcessPoolExecutor):
    _instance = None

    def __init__(self, workers):
        super().__init__(max_workers=workers)
        Scheduler._instance = self

    @staticmethod
    def get_instance():
        if not Scheduler._instance:
            logging.error("Storage is not initialized")

        return Scheduler._instance

    async def process_urls(self, task):
        loop = asyncio.get_event_loop()
        futures = [loop.run_in_executor(self, task.process_url, url_id)
                   for url_id in range(len(task.urls))]
        result = await asyncio.gather(*futures)
        await task.finish_task(result)
