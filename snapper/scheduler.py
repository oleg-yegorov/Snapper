import logging
from multiprocessing.pool import Pool


class Scheduler(Pool):
    _instance = None

    def __init__(self, workers):
        super().__init__(workers)
        Scheduler._instance = self

    def close(self):
        super().close()
        self.join()

    @staticmethod
    def get_instance():
        if not Scheduler._instance:
            logging.error("Storage is not initialized")

        return Scheduler._instance

    async def process_urls(self, task):
        self.map_async(task.process_url, range(len(task.urls)), callback=task.finish_task)
