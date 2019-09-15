import os
from pathlib import Path
from uuid import uuid4
import threading

from snapper.scheduler import scheduler


class Task:

    def __init__(self, urls, timeout, user_agent, output, phantomjs_binary):
        self.urls = urls
        self.id = str(uuid4())
        self.status = "running"
        self.result = {}

        self.output_path = Path.cwd() / output / self.id
        self.timeout = timeout
        self.user_agent = user_agent
        self.phantomjs_binary = phantomjs_binary
        self.left = len(urls)

    def run(self):
        for url in self.urls:
            print(url)

        if not Path(self.output_path).exists():
            os.makedirs(self.output_path)

        task = self

        scheduler.capture_snaps(
            urls=self.urls,
            outpath=self.output_path,
            timeout=self.timeout,
            user_agent=self.user_agent,
            phantomjs_binary=self.phantomjs_binary,
            task = task
        )

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "result": self.result
        }
