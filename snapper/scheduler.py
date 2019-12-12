from multiprocessing import Pool


class Scheduler:
    def __init__(self, workers):
        self.pool = Pool(workers)

    async def capture_snaps(self, task):
        self.pool.map_async(task.process_url, range(len(task.urls)), callback=task.finish_task)
