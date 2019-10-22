import asyncio
import os
from pathlib import Path
from uuid import uuid4

from snapper.scheduler import Scheduler


class Task:
    scheduler = None

    def __init__(self, urls, timeout, user_agent, output, chrome_binary, workers, output_paths_format):
        self.urls = urls
        self.id = str(uuid4())
        self.status = "running"
        self.result = {}

        self.output_path = Path.cwd() / output / self.id
        self.timeout = timeout
        self.user_agent = user_agent
        self.chrome_binary = chrome_binary
        self.left = len(urls)

        if not Task.scheduler:
            Task.scheduler = Scheduler(workers, output_paths_format, user_agent, chrome_binary, timeout)

    def run(self):
        if not Path(self.output_path).exists():
            os.makedirs(self.output_path)

        asyncio.create_task(Task.scheduler.capture_snaps(self))

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "result": self.result
        }
