import json

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import DesiredCapabilities

from snapper.utility import fix_url


class WebDriverChrome(webdriver.Chrome):
    def __init__(self, user_agent, chrome_binary, timeout):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--user-agent={}'.format(user_agent))

        # arguments to run in docker container
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        dCaps = DesiredCapabilities.CHROME
        dCaps['goog:loggingPrefs'] = {'performance': 'INFO'}

        super().__init__(chrome_options=chrome_options, executable_path=chrome_binary, desired_capabilities=dCaps)
        self.set_window_size(1024, 768)
        self.set_page_load_timeout(timeout)

    def get_redirect_chain(self, uri: str):
        try:
            self.get(uri)

            uri = fix_url(uri)
            redirect_chain = [uri]

            logs = self.get_log('performance')
            for log in logs:
                try:
                    log_entry = json.loads(log['message'])
                    if log_entry['message']['method'] == 'Page.frameScheduledNavigation' and \
                            log_entry['webview'] == log_entry['message']['params']['frameId']:
                        redirect_chain.append(log_entry['message']['params']['url'])
                    if log_entry['message']['params']['redirectResponse']['url'] == redirect_chain[-1] or \
                            log_entry['message']['params']['redirectResponse']['url'][:-1] == redirect_chain[-1]:    # trailing slash may be found
                        redirect_chain.append(log_entry['message']['params']['request']['url'])
                except KeyError as e:
                    pass
            return redirect_chain
        except TimeoutException:
            return []
        except Exception as e:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.quit()