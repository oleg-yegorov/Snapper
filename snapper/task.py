import os
from pathlib import Path
from uuid import uuid4



class Task:

    def __init__(self, urls, timeout, user_agent, output, phantomjs_binary):
        self.urls = []
        for url in urls:
            if url.startswith("https://") or url.startswith("https://"):
                self.urls.append(url)
            else:
                self.urls.append("http://" + url)
                self.urls.append("https://" + url)

        self.id = str(uuid4())
        self.status = "running"
        self.result = {}

        self.output_path = Path.cwd() / output / self.id
        self.timeout = timeout
        self.user_agent = user_agent
        self.phantomjs_binary = phantomjs_binary
        self.left = len(urls)

    def run(self):
        if not Path(self.output_path).exists():
            os.makedirs(self.output_path)

        task = self

        from snapper.scheduler import scheduler
        scheduler.capture_snaps(task)

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "result": self.result
        }
