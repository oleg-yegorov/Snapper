import logging

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from urllib3.exceptions import ProtocolError, MaxRetryError
from snapper.utility import image_transparent


class WebDriverPhantomjs(webdriver.PhantomJS):
    def __init__(self, user_agent, phantomjs_binary, timeout):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = user_agent
        dcap["phantomjs.binary.path"] = phantomjs_binary
        dcap["accept_untrusted_certs"] = True

        super().__init__(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any', '--web-security=false'],
                         desired_capabilities=dcap)
        self.set_window_size(1024, 768)
        self.set_page_load_timeout(timeout)

    def save_image(self, uri: str, file_name: str):
        uri = requests.utils.requote_uri(uri)
        try:
            self.get(uri)
            self.save_screenshot(file_name)
            return not image_transparent(file_name)
        except (WebDriverException, ProtocolError, MaxRetryError):
            return False
        except Exception as e:
            return False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self.close()
        except MaxRetryError:
            logging.error("urllib3.exceptions.MaxRetryError while closing webdriver")
        except Exception as e:
            logging.error("Error while closing webdriver")

        try:
            self.quit()
        except Exception as e:
            logging.error("Error while closing webdriver")
