from multiprocessing import Queue, Pool, Manager
import shutil
import os

#from snapper import app
from snapper.worker import host_worker

import yaml
from pathlib import Path


#host_queue = None
#pool = None

class Scheduler:


    def __init__(self):
        with open(Path(__file__).parent / "config.yaml") as file:
            config = yaml.safe_load(file)
        #workers = app.config["workers"]   
        workers = config["workers"]
        #manager = Manager()
        self.host_queue = Queue()
        self.pool = Pool(workers)


    def capture_snaps(self, urls, outpath, timeout,
                      user_agent, phantomjs_binary, task):
        css_output_path = Path(outpath) / "css"
        js_output_path = Path(outpath) / "js"
        images_output_path = Path(outpath) / "images"

        os.makedirs(css_output_path)
        os.makedirs(js_output_path)
        os.makedirs(images_output_path)

        css_template_path = Path(__file__).parent / "templates" / "css"
        js_template_path = Path(__file__).parent / "templates" / "js"
        shutil.copyfile(
            css_template_path / "materialize.min.css",
            css_output_path / "materialize.min.css"
        )
        shutil.copyfile(
            js_template_path / "jquery.min.js",
            js_output_path / "jquery.min.js"
        )
        shutil.copyfile(
            js_template_path / "materialize.min.js",
            js_output_path / "materialize.min.js"
        )

        #manager = Manager()
        file_queue = Queue()

        for host in urls:
            self.host_queue.put(host)

        self.pool.apply_async(host_worker, (self.host_queue, file_queue, timeout,
                user_agent, outpath, phantomjs_binary, task,))

scheduler = Scheduler()