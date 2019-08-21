import sys
import os
import webbrowser
import os.path
import yaml
import json
import shutil
from jinja2 import Environment, PackageLoader
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from argparse import ArgumentParser
from multiprocessing import Process, Queue
from os import chdir
from shutil import copyfile
from requests import get
from uuid import uuid4
from selenium.common.exceptions import TimeoutException
from flask import Flask, request, Response

# disable warnings
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer
try:
    import SimpleHTTPServer
except ImportError:
    import http.server as SimpleHTTPServer

env = Environment(autoescape=True,
                  loader=PackageLoader('snapper', 'templates'))
with open('config.yaml') as file:
    config = yaml.safe_load(file)
OUTPUT_FILENAME = "snapper_output"
app = Flask(__name__)
server = None
TASKS = {}
numWorkers = None
timeout = None
verbose = None
port = None
user_agent = None

class Task(object):

    def __init__(self, urls):
        self.urls = urls
        self.id = str(uuid4())
        self.status = "running"
        self.result = {}
        self.delete_path = None

    def run(self):
        numWorkers = len(self.urls)
        for url in self.urls:
            print(url)
        capture_snaps(self.urls, os.getcwd(), timeout, True, port, verbose,
                  numWorkers, user_agent, self.id, self)
        self.status = "ready"

    def to_json(self):
        return json.dumps({
            "id": self.id,
            "status": self.status,
            "result": self.result
        })


@app.route('/api/v1/submit', methods=['POST'])
def api_root():
    if "urls" not in request.json:
        return Response(
            json.dumps({"error": "'urls' not specified"}),
            status=400, mimetype='application/json'
        )

    new_task = Task(urls=request.json.get("urls"))
    TASKS[new_task.id] = new_task

    new_task.run()

    return Response(
        new_task.to_json(),
        status=200,
        mimetype='application/json'
    )
@app.route('/api/v1/shutdown', methods=['POST'])
def shutdown():
    outpath = os.path.join(os.getcwd(), OUTPUT_FILENAME)
    shutil.rmtree(outpath)
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    return "Server shutting down... \n"
    #server.terminate()
    #server.join()



@app.route('/api/v1/tasks/<task_id>', methods=['GET', 'DELETE'])
def api_article(task_id):
    task = TASKS.get(task_id)
    if task is None:
        return Response(
            json.dumps({"error": "no such task"}),
            status=404, mimetype='application/json'
        )
    if request.method == "GET":
        return Response(
            task.to_json(),
            status=200,
            mimetype='application/json'
        )
    elif request.method == "DELETE":
        shutil.rmtree(TASKS[task_id].delete_path)
        del TASKS[task_id]
        
        return Response(
            "",
            status=204,
            mimetype='application/json'
        )


def save_image(uri, file_name, driver):
    try:
        driver.get(uri)
        driver.save_screenshot(file_name)
        return True
    except TimeoutException:
        return False


def host_reachable(host, timeout):
    try:
        get(host, timeout=timeout, verify=False)
        return True
    # not sure which exception
    except TimeoutException:
        return False


def host_worker(hostQueue, fileQueue, timeout, user_agent, verbose, outpath):
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = user_agent
    dcap["accept_untrusted_certs"] = True
    # or add to your PATH
    driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true'],
                                 desired_capabilities=dcap)
    # optional
    driver.set_window_size(1024, 768)
    driver.set_page_load_timeout(timeout)
    while(not hostQueue.empty()):
        host = hostQueue.get()
        if not host.startswith("http://") and not host.startswith("https://"):
            host1 = "http://" + host
            host2 = "https://" + host
            filename1 = os.path.join(outpath, "images", str(uuid4()) + ".png")
            filename2 = os.path.join(outpath, "images", str(uuid4()) + ".png")
            if verbose:
                print("Fetching %s" % host1)
            if host_reachable(host1, timeout) and save_image(host1, filename1,
                                                             driver):
                fileQueue.put({host1: filename1})
            else:
                if verbose:
                    print("%s is unreachable or timed out" % host1)
            if verbose:
                print("Fetching %s" % host2)
            if host_reachable(host2, timeout) and save_image(host2, filename2,
                                                             driver):
                fileQueue.put({host2: filename2})
            else:
                if verbose:
                    print("%s is unreachable or timed out" % host2)
        else:
            filename = os.path.join(outpath, "images", str(uuid4()) + ".png")
            if verbose:
                print("Fetching %s" % host)
            if host_reachable(host, timeout) and save_image(host, filename,
                                                            driver):
                fileQueue.put({host: filename})
            else:
                if verbose:
                    print("%s is unreachable or timed out" % host)


def capture_snaps(hosts, outpath, timeout, serve, port,
                  verbose, numWorkers, user_agent, task_id, task):
    ip = config["IP"]
    outpath = os.path.join(outpath, OUTPUT_FILENAME, task_id)
    task.delete_path = outpath
    print(task.delete_path)
    cssOutputPath = os.path.join(outpath, "css")
    jsOutputPath = os.path.join(outpath, "js")
    imagesOutputPath = os.path.join(outpath, "images")
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    if not os.path.exists(imagesOutputPath):
        os.makedirs(imagesOutputPath)
    if not os.path.exists(cssOutputPath):
        os.makedirs(cssOutputPath)
    if not os.path.exists(jsOutputPath):
        os.makedirs(jsOutputPath)
    cssTemplatePath = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                   "templates", "css")
    jsTemplatePath = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                  "templates", "js")
    copyfile(os.path.join(cssTemplatePath, "materialize.min.css"),
             os.path.join(cssOutputPath, "materialize.min.css"))
    copyfile(os.path.join(jsTemplatePath, "jquery.min.js"),
             os.path.join(jsOutputPath, "jquery.min.js"))
    copyfile(os.path.join(jsTemplatePath, "materialize.min.js"),
             os.path.join(jsOutputPath, "materialize.min.js"))
    hostQueue = Queue()
    fileQueue = Queue()

    workers = []
    for host in hosts:
        hostQueue.put(host)
    for i in range(numWorkers):
        p = Process(target=host_worker, args=(hostQueue, fileQueue, timeout,
                    user_agent, verbose, outpath))
        workers.append(p)
        p.start()
    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        for worker in workers:
            worker.terminate()
            worker.join()
        sys.exit()
    setsOfSix = []
    count = 0
    hosts = {}
    while(not fileQueue.empty()):
        if count == 6:
            try:
                setsOfSix.append(hosts.iteritems())
            except AttributeError:
                setsOfSix.append(hosts.items())
            hosts = {}
            count = 0
        temp = fileQueue.get()
        hosts.update(temp)
    try:
        setsOfSix.append(hosts.iteritems())
    except AttributeError:
        setsOfSix.append(hosts.items())
    template = env.get_template('index.html')
    with open(os.path.join(outpath, "index.html"), "w") as outputFile:
        outputFile.write(template.render(setsOfSix=setsOfSix))
    task.result = outpath
    return True


# --------------------------MAIN------------------------- #
#def main():
if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument("-u", '--user-agent', action='store',
                      dest="user_agent", type=str,
                      default=config["USER_AGENT"],
                      help='The user agent used for requests')
    parser.add_argument("-c", '--concurrency', action='store',
                      dest="numWorkers", type=int, default=1,
                      help='Number of cuncurrent processes')
    parser.add_argument("-t", '--timeout', action='store',
                      dest="timeout", type=int, default=10,
                      help='Number of seconds to try to resolve')
    parser.add_argument("-p", '--port', action='store',
                      dest="port", type=int, default=config["PORT"],
                      help='Port to run server on')
    parser.add_argument("-v", action='store_true', dest="verbose",
                      help='Display console output for fetching each host')
    args = parser.parse_args()

    numWorkers = args.numWorkers
    timeout = args.timeout
    verbose = args.verbose
    port = args.port
    user_agent = args.user_agent

    #server = Process(target=app.run(port=port))
    #server.start()
    app.run(port=port)

