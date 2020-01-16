import asyncio
import logging
from uuid import uuid4

from snapper.scheduler import Scheduler
from snapper.utility import host_reachable
from snapper.web_driver_chrome import WebDriverChrome


class TaskRedirect:
    def __init__(self, urls, timeout, user_agent, chromedriver_binary):
        self.urls = urls
        self.id = str(uuid4())
        self.status = "running"
        self.result = {}

        self.timeout = timeout
        self.user_agent = user_agent
        self.chromedriver_binary = chromedriver_binary
        self.left = len(urls)

    def run(self):
        asyncio.create_task(Scheduler.get_instance().process_urls(self))

    def to_dict(self):
        return {
            "id": self.id,
            "status": self.status,
            "result": self.result,
        }

    def process_url(self, url_id):
        with WebDriverChrome(self.user_agent, self.chromedriver_binary, self.timeout) as web_driver:
            host = self.urls[url_id]
            if not host.startswith("https://") and not host.startswith("http://"):
                host = "http://" + host

            logging.debug("Fetching %s", host)
            if not host_reachable(host, self.timeout):
                redirect_chain = ["url is unreachable or timed out"]
                logging.debug("%s is unreachable or timed out", host)
            else:
                redirect_chain = web_driver.get_redirect_chain(host)

            return self.urls[url_id], redirect_chain

    def finish_task(self, urls_to_redirects):
        self.result.update({
            url: redirect_chain
            for url, redirect_chain in urls_to_redirects
        })

        self.status = "ready"
