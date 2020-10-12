import base64
import datetime
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from uuid import uuid4

from jinja2 import Environment, PackageLoader

from snapper.s3 import S3
from snapper.scheduler import Scheduler
from snapper.task import Task
from snapper.utility import host_reachable
from snapper.web_driver_phantomjs import WebDriverPhantomjs

env = Environment(autoescape=True,
                  loader=PackageLoader('snapper', 'templates'))


class TaskSnapper(Task):
    def __init__(self, urls, timeout, user_agent, output,
                 phantomjs_binary, output_paths_format, task_timeout_sec):
        super().__init__(urls, task_timeout_sec)

        self.output_path = Path.cwd() / output / self.id
        self.timeout = timeout
        self.user_agent = user_agent
        self.phantomjs_binary = phantomjs_binary
        self.output_paths_format = output_paths_format

        self.copy_template()

    def copy_template(self):
        shutil.copytree(Path(__file__).parent / "templates", self.output_path)
        os.makedirs(self.output_path / "images")

    def fill_template(self):
        # absolute path to relative path
        result_with_rel_paths = [
            (_, os.path.relpath(filename, self.output_path))
            for _, filename in self.result.items()
            if filename
        ]

        sets_of_six = list(zip(*[iter(result_with_rel_paths)]*6))
        sets_of_six.append(result_with_rel_paths[len(sets_of_six)*6:])

        template = env.get_template('index.html')
        index_file_path = Path(self.output_path) / "index.html"
        with open(index_file_path, "w") as index_file:
            index_file.write(template.render(sets_of_six=sets_of_six))

        self.result.update({"all": str(index_file_path)})

    async def process_urls(self):
        await Scheduler.get_instance().process_urls(self)

    def to_dict(self):
        result = {
            url: self.output_paths_format.format(filename)
            for url, filename in self.result.items()
        }

        return {
            "id": self.id,
            "status": self.status,
            "result": result,
        }

    def process_url(self, url_id):
        with WebDriverPhantomjs(self.user_agent, self.phantomjs_binary, self.timeout) as web_driver:
            filename = Path(self.output_path) / "images" / (str(uuid4()) + ".png")

            host = self.urls[url_id]
            if not host.startswith("https://") and not host.startswith("http://"):
                host = "http://" + host

            logging.debug("Fetching %s", host)
            if not host_reachable(host, self.timeout) or \
                    not web_driver.save_image(host, str(filename)):
                logging.debug("%s is unreachable or timed out", host)

                try:
                    error_page_path = Path(__file__).parent / "error_pages" / "unreachable_or_timed_out.png"
                    shutil.copyfile(error_page_path, filename)
                except IOError as e:
                    logging.error("error while coping %s to %s: %s", error_page_path, filename, str(e))
                    return self.urls[url_id], None

            return self.urls[url_id], str(filename)

    def create_meta_file(self):
        meta_data = {
            os.path.basename(path): {
                "url": url,
                "created": os.path.getmtime(path)
            }
            for url, path in self.result.items()
        }

        with open(Path(self.output_path) / "images" / "meta.txt", "w") as meta_file:
            json.dump(meta_data, meta_file)

    def to_s3_format(self, output_dir):
        for url, path in self.result.items():
            url_dir = base64.b64encode(url.encode('UTF-8')).decode('UTF-8')
            os.mkdir(output_dir / url_dir)

            screenshot_dir = Path(datetime.datetime.fromtimestamp(os.path.getmtime(path)).replace(microsecond=0).isoformat())
            os.mkdir(output_dir / url_dir / screenshot_dir)
            os.symlink(path, output_dir / url_dir / screenshot_dir / 'screenshot.png')

            with open(output_dir / url_dir / screenshot_dir / 'task_id.txt', 'w') as task_id_file:
                    task_id_file.write(self.id)

    async def upload_to_s3(self):
        if not S3.get_instance():
            return

        async with S3.get_instance().get_async_client() as s3_client:
            with Path(tempfile.mkdtemp()) as task_dir:
                self.to_s3_format(task_dir)

                url_dirs = next(os.walk(task_dir))[1]
                for url_dir in url_dirs:
                    await S3.get_instance().upload_dir(s3_client, task_dir / url_dir, url_dir)

                shutil.rmtree(task_dir)

    async def finish_task(self, urls_to_filenames):
        # list of list -> dict
        self.result.update({
            url: filename
            for url, filename in urls_to_filenames
            if filename
        })

        self.create_meta_file()
        self.fill_template()

        self.status = "ready"

        await self.upload_to_s3()

    async def cleanup(self):
        shutil.rmtree(self.output_path)
