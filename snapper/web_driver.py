import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


class WebDriver(webdriver.Chrome):
    def __init__(self, user_agent, chrome_binary, timeout):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = True
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--user-agent={}'.format(user_agent))

        # arguments to run in docker container
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        super().__init__(chrome_options=chrome_options, executable_path=chrome_binary)
        self.set_window_size(1024, 768)
        self.set_page_load_timeout(timeout)

    def save_image(self, uri: str, file_name: str):
        try:
            self.get(uri)
            self.save_screenshot(file_name)
            return True
        except TimeoutException:
            return False

    @staticmethod
    def host_reachable(host, timeout):
        try:
            requests.get(host, timeout=timeout, verify=False)
            return True
        except requests.exceptions.RequestException:
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        self.quit()
