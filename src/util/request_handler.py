import logging
import queue
import threading
import time
from typing import Any, Callable

import pylast
from requests import exceptions, get

import globals as g

logger = logging.getLogger("discord_fm").getChild(__name__)


def wait_for_internet():
    """Sends a request to Google repeatedly until it is able to connect."""
    counter = 0
    while True:
        try:
            get("https://gstatic.com/generate_204")
            logger.info("Connected to the internet again")
            return
        except (exceptions.ConnectionError, exceptions.Timeout):
            counter += 1
            time.sleep(2)


class RequestHandler:
    _inactive_timer = None
    _timeout_timer = None
    _interrupt_request = False
    _current_thread = 0
    _result = None
    _bucket = queue.Queue()
    _tries = 0

    def __init__(
        self, message: str, inactive_func: Callable = None, limit_tries: int = 0
    ):
        self.message = message
        self.inactive_func = inactive_func
        self._limit = limit_tries

    def attempt_request(
        self, request_func: Callable, timeout: float = 60, *args, **kwargs
    ) -> Any:
        """Tries to run ``request_func`` and catches common exception errors from methods that use
        ``requests.get``.

        :param args: Parameters to send to the function
        :param kwargs: Keyword parameters to send to the function
        :param request_func: The function that will be tried
        :type request_func: Callable
        :param timeout: Max time in seconds that the function can take
        :type timeout: float
        :return: request_func result
        """

        self._timeout_timer = threading.Timer(timeout, self._interrupt)
        self._timeout_timer.start()
        self._inactive_timer = None

        if self.inactive_func is not None:
            self._inactive_timer = threading.Timer(30, self.inactive_func)
            self._inactive_timer.start()

        self._result = None
        self._bucket = queue.Queue()

        while True:
            if g.current == g.Status.KILL:
                self._cancel_timers()
                g.manager.close()

            if 0 < self._limit <= self._tries:
                logger.warning(
                    f"Hit or exceeded maximum tries (over {self._limit} tries)"
                )
                self._cancel_timers()
                return None

            thread = threading.Thread(
                target=self._wrapper, args=(request_func, args, kwargs)
            )
            thread.start()
            self._current_thread = thread.ident

            while thread.is_alive():
                if g.current == g.Status.KILL:
                    self._cancel_timers()
                    g.manager.close()

                if self._interrupt_request:
                    logger.info(f"Request for {self.message} timed out")
                    self._tries += 1
                    continue

            if not self._bucket.empty():
                e = self._bucket.get(block=False)
                if isinstance(e, (exceptions.ConnectionError, pylast.NetworkError)):
                    logger.warning(
                        f"A connection error occurred while getting {self.message}",
                        exc_info=e,
                    )
                elif isinstance(e, exceptions.Timeout):
                    logger.warning(f"Timed out while requesting {self.message}")
                elif isinstance(e, exceptions.ChunkedEncodingError):
                    logger.warning(f"Connection error while downloading {self.message}")
                elif isinstance(e, pylast.MalformedResponseError):
                    logger.warning(
                        f"Received a Last.fm internal server error while getting {self.message}",
                        exc_info=e,
                    )
                elif isinstance(e, exceptions.RequestException):
                    logger.error(
                        f"Unexpected generic exception while getting {self.message}",
                        exc_info=e,
                    )
                elif isinstance(e, pylast.WSError) and e.get_id() == 8:
                    logger.warning(
                        f"Error with WSError when getting {self.message}", exc_info=e
                    )
                else:
                    self._cancel_timers()
                    raise e

                wait_for_internet()
                self._tries += 1
                continue

            self._cancel_timers()
            return self._result

    def _cancel_timers(self):
        self._timeout_timer.cancel()
        if self._inactive_timer is not None:
            self._inactive_timer.cancel()

    def _interrupt(self):
        self._interrupt_request = True

    def _wrapper(self, func, args, kwargs):
        thread_id = threading.get_ident()
        logger.debug(f"Thread ID: {thread_id}")
        exc = None
        try:
            result = func(*args, **kwargs)
            logger.debug(f'Finished running function "{func.__name__}"')
        except Exception as e:
            exc = e

        if self._current_thread != thread_id:
            logger.debug(
                f"current_thread is mismatched with this thread ({self._current_thread} "
                f"vs. {thread_id})"
            )
            return

        if exc is not None:
            self._bucket.put(exc)
            logger.debug(f"Caught exception: \n{exc}")
            return

        # noinspection PyUnboundLocalVariable
        logger.debug(f"Thread result: {result}")
        self._result = result
        return
