import requests
from selenium import webdriver
from selenium.common.exceptions import TimeoutException


class WebDriver(webdriver.Firefox):
    def __init__(self, user_agent, firefox_binary, timeout):
        firefox_profile = webdriver.FirefoxProfile()
        firefox_profile.set_preference("general.useragent.override", user_agent)

        firefox_options = webdriver.FirefoxOptions()
        firefox_options.headless = True
        firefox_options.accept_insecure_certs = True

        # arguments to run in docker container
        firefox_options.add_argument("--no-sandbox")
        firefox_options.add_argument("--disable-dev-shm-usage")

        super().__init__(firefox_binary=firefox_binary, firefox_options=firefox_options,
                         firefox_profile=firefox_profile)
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
