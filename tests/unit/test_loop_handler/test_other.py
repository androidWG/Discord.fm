from unittest import mock
from unittest.mock import MagicMock, patch


@patch("loop_handler.scheduler")
class TestLoopHandler:
    manager = MagicMock()

    def test_handle_update(self, *mocks):
        from loop_handler import LoopHandler

        handler = LoopHandler(self.manager)

        handler.handle_update()

        handler.sc.enter.assert_has_calls(
            [
                mock.call(handler.cooldown, 1, handler._lastfm_update, (handler.sc,)),
                mock.call(
                    handler.misc_cooldown, 2, handler._misc_update, (handler.sc,)
                ),
            ]
        )
        handler.sc.run.assert_called_once()

    def test_force_update(self, *mocks):
        from loop_handler import LoopHandler

        handler = LoopHandler(self.manager)
        handler.sc.queue = [mock.sentinel.event1, mock.sentinel.event2]

        handler.force_update()

        handler.sc.cancel.assert_has_calls(
            [mock.call(mock.sentinel.event1), mock.call(mock.sentinel.event2)]
        )
        handler.sc.enter.assert_has_calls(
            [
                mock.call(0, 1, handler._lastfm_update, (handler.sc,)),
                mock.call(0, 2, handler._misc_update, (handler.sc,)),
            ]
        )

    def test_get_last_track(self, *mocks):
        from loop_handler import LoopHandler

        handler = LoopHandler(self.manager)
        handler._last_track = mock.sentinel.track

        assert handler.get_last_track() == mock.sentinel.track
