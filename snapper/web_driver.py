import logging

import numpy
import requests
from PIL import Image, UnidentifiedImageError
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

        super().__init__(service_args=['--ignore-ssl-errors=true', '--ssl-protocol=any', '--web-security=false'],
                         desired_capabilities=dcap)
        self.set_window_size(1024, 768)
        self.set_page_load_timeout(timeout)

    @staticmethod
    def image_is_transparent(file_name: str):
        try:
            image = Image.open(file_name)
            image_array = numpy.asarray(image)
            if len(image_array.shape) == 3 and image_array.shape[2] == 4:  # image has A channel?
                alpha_channel = image_array[..., 3]
                return not alpha_channel.any()
            else:
                logging.error("image does not have an A channel: %s", file_name)
                return False
        except (UnidentifiedImageError, IOError) as e:
            logging.error(e)
            return False

    def save_image(self, uri: str, file_name: str):
        uri = requests.utils.requote_uri(uri)
        try:
            self.get(uri)
            self.save_screenshot(file_name)
            return not WebDriver.image_is_transparent(file_name)
        except (WebDriverException, ProtocolError):
            return False

    @staticmethod
    def host_reachable(host, timeout):
        try:
            response = requests.get(host, timeout=timeout, verify=False)
            return True if response.content else False
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
