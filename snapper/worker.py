import logging
import os
import requests
import shutil
import sys

from pathlib import Path

from uuid import uuid4

from multiprocessing import Process, Queue

from jinja2 import Environment, PackageLoader
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

env = Environment(autoescape=True,
                  loader=PackageLoader('snapper', 'templates'))


def save_image(uri: str, file_name: str, driver):
    try:
        driver.get(uri)
        driver.save_screenshot(file_name)
        return True
    except TimeoutException:
        return False


def host_reachable(host, timeout):
    try:
        requests.get(host, timeout=timeout, verify=False)
        return True
    # not sure which exception
    except TimeoutException:
        return False


def host_worker(host_queue, file_queue, timeout,
                user_agent, outpath, phantomjs_binary, task):
    print("SNAKE")
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent
    dcap["phantomjs.binary.path"] = phantomjs_binary
    dcap["accept_untrusted_certs"] = True
    # or add to your PATH
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'],
                                 desired_capabilities=dcap)
    # optional
    driver.set_window_size(1024, 768)
    driver.set_page_load_timeout(timeout)
    while True:
    #while not host_queue.empty():
        host = host_queue.get()
        if not host.startswith("http://") and not host.startswith("https://"):
            host_http = "http://" + host
            host_https = "https://" + host
            filename_http = Path(outpath) / "images" / (
                    str(uuid4()) + "_http.png")
            filename_https = Path(outpath) / "images" / (
                    str(uuid4()) + "_https.png")
            logging.debug("Fetching %s", host_http)
            if host_reachable(host_http, timeout) and \
                    save_image(host_http, str(filename_http), driver):
                file_queue.put({host_http: str(filename_http)})
            else:
                logging.debug("%s is unreachable or timed out", host_http)
            logging.debug("Fetching %s", host_https)
            if host_reachable(host_https, timeout) and \
                    save_image(host_https, str(filename_https), driver):
                file_queue.put({host_https: str(filename_https)})
            else:
                logging.debug("%s is unreachable or timed out", host_https)
        else:
            filename = Path(outpath) / "images" / (str(uuid4()) + ".png")
            logging.debug("Fetching %s", host)
            if host_reachable(host, timeout) and save_image(host, filename,
                                                            driver):
                file_queue.put({host: str(filename)})
            else:
                logging.debug("%s is unreachable or timed out", host)

    task.left = task.left-1
    if(task.left == 0):
        finish_task(task, file_queue, outpath)

    def finish_task(task, file_queue, outpath):
        sets_of_six = []
        count = 0
        urls = {}
        while not file_queue.empty():
            if count == 6:
                sets_of_six.append(urls.items())
                urls = {}
                count = 0
            temp = file_queue.get()
            urls.update(temp)

        try:
            sets_of_six.append(urls.items())
        except AttributeError:
            sets_of_six.append(urls.items())
        template = env.get_template('index.html')
        with open(Path(outpath) / "index.html", "w") as output_file:
            output_file.write(template.render(sets_of_six=sets_of_six))
        task.status = "ready"
        task.result.update({"all": str(outpath)})


