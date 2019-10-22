from functools import partial
from multiprocessing import Pool

from snapper.worker import copy_template, finish_task, host_worker, set_global_worker


class Scheduler:
    def __init__(self, workers, output_paths_format, user_agent, chrome_binary, timeout):
        self.pool = Pool(workers, initializer=set_global_worker, initargs=(user_agent, chrome_binary, timeout))
        self._output_paths_format = output_paths_format

    async def capture_snaps(self, task):
        copy_template(task)

        host_worker_call = partial(host_worker, task=task)
        finish_task_call = partial(finish_task, task=task, output_paths_format=self._output_paths_format)
        self.pool.map_async(host_worker_call, range(len(task.urls)), callback=finish_task_call)
