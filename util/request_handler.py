import logging
import queue
import threading
import time
import pylast
from typing import Callable
from requests import get, exceptions


def wait_for_internet():
    """Sends a request to google.com repeatedly to check if there's request_handler connectivity. Returns True if it was
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


class RequestHandler:
    _interrupt_request = False
    _current_thread = 0

    def __init__(self, message: str, inactive_func: Callable = None):
        self.result = None
        self.bucket = queue.Queue()

        self.message = message
        self.inactive_func = inactive_func

    def attempt_request(self, request_func: Callable, timeout: float = 60, *args, **kwargs):
        """Tries to run ``request_func`` and catches common exception errors from methods that use
        ``requests.get``. Returns None if the request ultimately fails.

        :param args: Parameters to send to the function
        :param request_func: The function that we will try
        :type request_func: Callable
        :param timeout: How many seconds before we determine the function is taking too long
        :type timeout: float
        :return: request_func result or None if it fails
        """
        timeout_timer = threading.Timer(timeout, self._interrupt)
        timeout_timer.start()
        inactive_timer = None

        if self.inactive_func is not None:
            inactive_timer = threading.Timer(30, self.inactive_func)
            inactive_timer.start()

        while True:
            self.result = None
            self.bucket = queue.Queue()

            thread = threading.Thread(target=self._wrapper, args=(request_func, args, kwargs))
            thread.start()
            self._current_thread = thread.ident

            while thread.is_alive():
                if self._interrupt_request:
                    logging.warning(f"Request for {self.message} timed out")
                    continue

            if not self.bucket.empty():
                e = self.bucket.get(block=False)
                if isinstance(e, (exceptions.ConnectionError, pylast.NetworkError)):
                    logging.warning(f"A connection error occurred while getting {self.message}. Exception Message:\n{e}")
                elif isinstance(e, exceptions.Timeout):
                    logging.warning(f"Timed out while requesting {self.message}")
                elif isinstance(e, exceptions.ChunkedEncodingError):
                    logging.warning(f"Connection error while downloading {self.message}")
                elif isinstance(e, pylast.MalformedResponseError):
                    logging.info(f"Received a Last.fm internal server error while getting {self.message}", exc_info=e)
                elif isinstance(e, exceptions.RequestException):
                    logging.error(f"Unexpected generic exception while getting {self.message}", exc_info=e)
                else:
                    raise e

                wait_for_internet()
                continue

            timeout_timer.cancel()
            if inactive_timer is not None:
                inactive_timer.cancel()
            return self.result

    def _interrupt(self):
        self._interrupt_request = True

    def _wrapper(self, func, args, kwargs):
        thread_id = threading.get_ident()
        logging.debug(f"Thread ID: {thread_id}")
        exc = None
        try:
            result = func(*args, **kwargs)
            logging.debug(f"Finished running function \"{func.__name__}\"")
        except Exception as e:
            exc = e
        finally:
            if self._current_thread != thread_id:
                logging.debug(f"current_thread is mismatched with this thread ({self._current_thread} "
                              f"vs. {thread_id})")
                return

        if exc is not None:
            self.bucket.put(exc)
            logging.debug(f"Caught exception: \n{exc}")
            return

        logging.debug(f"Thread result: {result}")
        self.result = result
