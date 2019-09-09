import os
from pathlib import Path
from uuid import uuid4
import threading

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

        thread = threading.Thread(target=capture_snaps,
          args = (self.urls, self.output_path, self.timeout, num_workers,
                  self.user_agent, self.result, self.phantomjs_binary, self,)) 
        thread.daemon = True
        thread.start()

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "result": self.result
        }
