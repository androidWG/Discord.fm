import logging
import threading
import time
import pylast
import requests
from typing import Callable


def wait_for_internet():
    """Sends a request to google.com forever to check if there's request_handler connectivity. Returns True if it was
    able to connect in under 300 tries and False if it reached that limit.

    :return: Boolean indicating if caller should try again or give up
    :rtype: bool
    """
    counter = 0
    while True:
        try:
            requests.get("https://google.com")
            logging.info("Connected to the internet again")
            return
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            counter += 1
            time.sleep(1.5)


def attempt_request(request_func: Callable, message: str = "request", timeout_func: Callable = None, *args, **kwargs):
    """Tries to run ``request_func`` and catches common exception errors from methods that use
    ``requests.get``. Returns None if the request ultimately fails.

    :param args: Parameters to send to the function
    :param message: Name to be used when logging
    :type message: str
    :param request_func: The function that we will try
    :type request_func: Callable
    :param timeout_func: Function that will be executed after 60 seconds of inactivity (optional)
    :type timeout_func: Callable
    :return: request_func result or None if it fails
    """
    timer = None
    if timeout_func is not None:
        timer = threading.Timer(60, timeout_func)
        timer.start()

    while True:
        try:
            if len(args) == 0:
                result = request_func()
            elif len(args) != 0 and len(kwargs) != 0:
                result = request_func(*args, **kwargs)
            else:
                result = request_func(*args)

            if timer is not None:
                timer.cancel()
            return result
        except (requests.exceptions.ConnectionError, pylast.NetworkError) as e:
            logging.warning(f"A connection error occurred while getting {message}. Exception Message:\n{e.details}")
        except requests.exceptions.Timeout:
            logging.warning(f"Timed out while requesting {message}")
        except requests.exceptions.ChunkedEncodingError:
            logging.warning(f"Connection error while downloading {message}")
        except pylast.MalformedResponseError as e:
            logging.info(f"Received a Last.fm internal server error while getting {message}", exc_info=e)

        wait_for_internet()
