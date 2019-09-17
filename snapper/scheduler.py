from functools import partial
from multiprocessing import Pool
from pathlib import Path

import yaml

from snapper.worker import copy_template, finish_task, host_worker


class Scheduler:
    def __init__(self):
        with open(Path(__file__).parent / "config.yaml") as file:
            config = yaml.safe_load(file)

        workers = config["workers"]
        self.pool = Pool(workers)

    def capture_snaps(self, task):
        copy_template(task)

        host_worker_call = partial(host_worker, task=task)
        filenames = self.pool.map(host_worker_call, range(len(task.urls)))

        finish_task(task, filenames, task.output_path)


scheduler = Scheduler()
