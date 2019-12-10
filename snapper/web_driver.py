import requests
import logging
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib3.exceptions import ProtocolError, MaxRetryError


class WebDriver(webdriver.PhantomJS):
    def __init__(self, user_agent, phantomjs_binary, timeout):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = user_agent
        dcap["phantomjs.binary.path"] = phantomjs_binary
        dcap["accept_untrusted_certs"] = True

        super().__init__(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any'],
                         desired_capabilities=dcap)
        self.set_window_size(1024, 768)
        self.set_page_load_timeout(timeout)

    def save_image(self, uri: str, file_name: str):
        uri = requests.utils.requote_uri(uri)
        try:
            self.get(uri)
            self.save_screenshot(file_name)
            return True
        except (WebDriverException, ProtocolError):
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
        try:
            self.close()
        except MaxRetryError:
            logging.error("urllib3.exceptions.MaxRetryError while closing webdriver")

        self.quit()
