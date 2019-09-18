from functools import partial
from multiprocessing import Pool

from snapper import app
from snapper.worker import copy_template, finish_task, host_worker


class Scheduler:
    def __init__(self):
        self.pool = Pool(app["workers"])

    async def capture_snaps(self, task):
        copy_template(task)

        host_worker_call = partial(host_worker, task=task)
        finish_task_call = partial(finish_task, task=task)
        self.pool.map_async(host_worker_call, range(len(task.urls)), callback=finish_task_call)


scheduler = Scheduler()
