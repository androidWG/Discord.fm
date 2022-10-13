import unittest
from unittest.mock import MagicMock, patch

import requests.exceptions

from util import request_handler

test_phrase = "mock method finished"


def mock_method():
    # Simple slightly time-consuming method to be called
    number = 1
    for x in range(0, 100000):
        for y in range(0, number):
            number += x * y

    return test_phrase


def timeout_method():
    mock_method()
    raise requests.exceptions.Timeout()


def bad_method():
    mock_method()
    raise OSError("Test exception handling")


class TestRequestHandler(unittest.TestCase):
    manager = MagicMock()

    def test_successful_request(self):
        rh = request_handler.RequestHandler(self.manager, "test")
        self.assertEqual(rh.attempt_request(mock_method), test_phrase)

    @patch("util.request_handler.wait_for_internet")
    def test_limited_tries(self, mock_wait: MagicMock, mock_error: MagicMock):
        limit = 5
        rh = request_handler.RequestHandler(self.manager, "test2", limit_tries=limit)
        rh.attempt_request(timeout_method, timeout=5)

        mock_wait.assert_called()
        mock_error.assert_called_once_with(
            f"Hit or exceeded maximum tries (over {limit} tries)"
        )

    def test_exception_request(self):
        rh = request_handler.RequestHandler(self.manager, "test3")
        self.assertRaises(OSError, rh.attempt_request, bad_method)


if __name__ == "__main__":
    unittest.main()
