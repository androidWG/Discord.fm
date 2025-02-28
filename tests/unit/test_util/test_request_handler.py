import unittest
from unittest.mock import MagicMock, patch

import requests.exceptions

import util.request_handler

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


@patch("util.request_handler.wait_for_internet")
class TestRequestHandler(unittest.TestCase):
    manager = MagicMock()

    def test_successful_request(self, *mocks):
        rh = util.request_handler.RequestHandler(self.manager, "test")
        result = rh.attempt_request(mock_method)
        self.assertEqual(result, test_phrase)

    @patch("logging.Logger.warning")
    def test_limited_tries(self, mock_error: MagicMock, mock_wait: MagicMock):
        limit = 5
        rh = util.request_handler.RequestHandler(
            self.manager, "test2", limit_tries=limit
        )
        rh.attempt_request(timeout_method)

        mock_wait.assert_called()
        mock_error.assert_any_call(
            f"Hit or exceeded maximum tries (over {limit} tries)"
        )

    def test_exception_request(self, *mocks):
        rh = util.request_handler.RequestHandler(self.manager, "test3")
        with self.assertRaises(OSError):
            result = rh.attempt_request(bad_method)
            print(result)


if __name__ == "__main__":
    unittest.main()
