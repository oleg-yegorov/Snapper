import os
from pathlib import Path
from uuid import uuid4

from snapper.worker import capture_snaps


class Task(object):

    def __init__(self, urls, timeout, user_agent, output, phantomjs_binary):
        self.urls = urls
        self.id = str(uuid4())
        self.status = "running"
        self.result = {}

        self.output_path = Path.cwd() / output / self.id
        self.timeout = timeout
        self.user_agent = user_agent
        self.phantomjs_binary = phantomjs_binary

    def run(self, num_workers):
        for url in self.urls:
            print(url)

        if not Path(self.output_path).exists():
            os.makedirs(self.output_path)

        capture_snaps(
            urls=self.urls,
            outpath=self.output_path,
            timeout=self.timeout,
            num_workers=num_workers,
            user_agent=self.user_agent,
            result=self.result,
            phantomjs_binary=self.phantomjs_binary
        )
        self.status = "ready"

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "result": self.result
        }
