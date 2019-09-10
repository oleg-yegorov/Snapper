# Snapper
A security tool for grabbing screenshots of many web hosts. This tool is useful after [DNS enumeration](https://github.com/mschwager/fierce) or after enumerating web hosts via nmap or nessus. Here is the github [link](https://github.com/revisor48/Snapper).

## How to install 


- PyPl package
```bash
pip install snapper
```

- Install phantomJS (you need to have [npm installed](https://nodejs.org/en/download/package-manager/))
```bash
npm -g install phantomjs
```

## How to use
### On the server side

To start up the application:

```
snap
```

, make sure requirenment.txt is satisfied:

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

You can view the results [here](https://security.love/Snapper/output). Note in addition to the server, the static files are available in your current working directory as "output"


## More options

```bash
snap --help
```

```
Options:
  -h, --help            show this help message and exit
  -u USER_AGENT, --user-agent=USER_AGENT
                        The user agent used for requests
  -o OUTPUT_DIR, --output=OUTPUT_DIR	
  						Directory for output
  -l LOGS, --log_level=LOGS 
  						Logging facility level
  -t TIMEOUT, --timeout=TIMEOUT
                        Number of seconds to try to resolve
  -p PORT, --port=PORT  Port to run server on
  -H HOST, --host=HOST  Host to run server on  
  -v                    Display console output for fetching each host
  
```
