# Snapper
A security tool for grabbing screenshots of many web hosts. This tool is useful after [DNS enumeration](https://github.com/mschwager/fierce) or after enumerating web hosts via nmap or nessus.

## How to install 


- Pypl package
```bash
pip install -i  https://test.pypi.org/simple/ snapper
```

- Install phantomJS (you need to have [npm installed](https://nodejs.org/en/download/package-manager/))
```bash
npm -g install phantomjs
```

## How to use
### On the server side

To start up the application from pypi:

```
snap
```

You can also launch it directly from [github](https://github.com/revisor48/Snapper), make sure requirenment.txt is satisfied:

```
python cli.py
```
### On the user side
POST command populates the data:
```
curl -XPOST -H 'Content-Type: application/json' -d '{"urls": ["google.com", "gmail.google.com", "ads.google.com"]}' http://127.0.0.1:8000/api/v1/submit
```

This kicks off 3 processes, each of which fetch screenshots of the http and https versions of the hosts in question. 
![output results](http://i.imgur.com/OlvyIBp.png)
Each POST request has an id, which you can use to access the data outputted by it. The output is saved on the server side in the "output" folder and the path to it is returned as json by GET command:
```
curl -XGET http://127.0.0.1:8000/api/v1/tasks/164157d3-472d-4e25-8488-389e206d24bb
```

You can also read from a file, these results where generated from a [fierce](https://github.com/mschwager/fierce) enumeration:
```
snap -f googleExample.txt -c 10
```

You can view the results [here](https://security.love/Snapper/output). Note in addition to the server, the static files are available in your current working directory as "output"


## More options

```bash
snap --help
```

```
Options:
  -h, --help            show this help message and exit
  -f FILE, --file=FILE  Souce from input file
  -l LIST, --list=LIST  Source from commandline list
  -u USER_AGENT, --user-agent=USER_AGENT
                        The user agent used for requests
  -c NUMWORKERS, --concurrency=NUMWORKERS
                        Number of cuncurrent processes
  -t TIMEOUT, --timeout=TIMEOUT
                        Number of seconds to try to resolve
  -p PORT, --port=PORT  Port to run server on
  -v                    Display console output for fetching each host
```
