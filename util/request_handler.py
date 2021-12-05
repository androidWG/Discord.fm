import logging
import queue
import sys
import threading
import time
import pylast
from typing import Callable
from requests import get, exceptions

interrupt_request = False
current_thread = 0


def wait_for_internet():
    """Sends a request to google.com forever to check if there's request_handler connectivity. Returns True if it was
    able to connect in under 300 tries and False if it reached that limit.

    :return: Boolean indicating if caller should try again or give up
    :rtype: bool
    """
    counter = 0
    while True:
        try:
            get("https://google.com")
            logging.info("Connected to the internet again")
            return
        except (exceptions.ConnectionError, exceptions.Timeout):
            counter += 1
            time.sleep(2)


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
    global current_thread
    timeout_timer = threading.Timer(20, _interrupt)
    timeout_timer.start()
    inactive_timer = None

    if timeout_func is not None:
        inactive_timer = threading.Timer(30, timeout_func)
        inactive_timer.start()

    while True:
        result = []
        bucket = queue.Queue()

        thread = threading.Thread(target=_wrapper, args=(request_func, result, bucket, args, kwargs))
        thread.start()
        current_thread = thread.ident

        while thread.is_alive():
            if interrupt_request:
                logging.warning(f"Request for {message} timed out")
                continue

        if not bucket.empty():
            e = bucket.get(block=False)
            if isinstance(e, (exceptions.ConnectionError, pylast.NetworkError)):
                logging.warning(f"A connection error occurred while getting {message}. Exception Message:\n{e}")
            elif isinstance(e, exceptions.Timeout):
                logging.warning(f"Timed out while requesting {message}")
            elif isinstance(e, exceptions.ChunkedEncodingError):
                logging.warning(f"Connection error while downloading {message}")
            elif isinstance(e, pylast.MalformedResponseError):
                logging.info(f"Received a Last.fm internal server error while getting {message}", exc_info=e)
            elif isinstance(e, exceptions.RequestException):
                logging.error(f"Unexpected generic exception while getting {message}", exc_info=e)

            wait_for_internet()
            continue

        timeout_timer.cancel()
        if inactive_timer is not None:
            inactive_timer.cancel()
        return result[0]


def _interrupt():
    global interrupt_request
    interrupt_request = True


def _wrapper(func, return_var: list, bucket: queue.Queue, args, kwargs):
    thread_id = threading.get_ident()
    logging.debug(f"Thread ID: {thread_id}")
    exc = None
    try:
        result = func(*args, **kwargs)
        logging.debug(f"Finished running function \"{func.__name__}\"")
    except Exception:
        exc = sys.exc_info()
        logging.debug("EXCEPTION")
    finally:
        if current_thread != thread_id:
            logging.debug(f"current_thread is mismatched with this thread (\"{current_thread}\" vs. \"{thread_id}\")")
            return

    if exc is not None:
        bucket.put(exc)
        logging.debug(f"Caught exception: \n{exc}")
        return

    logging.debug(f"Thread result: {result}")
    return_var.append(result)
