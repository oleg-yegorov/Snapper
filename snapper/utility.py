import logging

import numpy
import requests
from urllib.parse import urlsplit, quote, unquote, urlunsplit
from PIL import Image, UnidentifiedImageError


def host_reachable(host, timeout):
    try:
        response = requests.get(host, timeout=timeout, verify=False)
        return True if response.content else False
    except requests.exceptions.RequestException:
        return False


def image_transparent(file_name: str):
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


def fix_url(url):
    parsed = urlsplit(url)

    # divide the netloc further
    userpass, at, hostport = parsed.netloc.rpartition('@')
    user, colon1, pass_ = userpass.partition(':')
    host, colon2, port = hostport.partition(':')

    # encode each component
    scheme = parsed.scheme
    user = quote(user)
    colon1 = colon1
    pass_ = quote(pass_)
    at = at
    host = host.encode('idna').decode('utf-8')
    colon2 = colon2
    port = port
    path = '/'.join(  # could be encoded slashes!
        quote(unquote(pce), '')
        for pce in parsed.path.split('/')
    )
    query = quote(unquote(parsed.query), '=&?/')
    fragment = quote(unquote(parsed.fragment))

    # put it back together
    netloc = ''.join((user, colon1, pass_, at, host, colon2, port))
    return urlunsplit((scheme, netloc, path, query, fragment))
