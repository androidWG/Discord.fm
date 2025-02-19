from unittest import mock
from unittest.mock import MagicMock, patch

from loop_handler import LoopHandler
from util.status import Status


@patch("wrappers.last_fm_user.LastFMUser")
@patch("loop_handler.system_tray_icon.SystemTrayIcon")
@patch("loop_handler.track_info.TrackInfo")
@patch("loop_handler.Image")
@patch("loop_handler.scheduler")
class TestLastfmUpdate:
    manager = MagicMock()

    def test_disabled_status(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.DISABLED

        with mock.patch.object(handler.sc, "enter") as mock_enter:
            handler._lastfm_update(mock.sentinel.scheduler_ref)

        mock_enter.assert_called_once_with(
            handler.cooldown, 1, handler._lastfm_update, (mock.sentinel.scheduler_ref,)
        )

    def test_waiting_for_discord_status(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.WAITING_FOR_DISCORD

        with mock.patch.object(handler.sc, "enter") as mock_enter:
            handler._lastfm_update(mock.sentinel.scheduler_ref)

        mock_enter.assert_called_once_with(
            handler.cooldown, 1, handler._lastfm_update, (mock.sentinel.scheduler_ref,)
        )

    def test_kill_status(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.KILL

        handler._lastfm_update(mock.sentinel.scheduler_ref)

        # Assert that no further actions are taken

    def test_track_not_none(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.ENABLED

        mock_user = mock.Mock()
        mock_user.now_playing.return_value = "Track Name"
        handler.user = mock_user

        with (
            mock.patch.object(
                handler.m.discord_rp, "update_status"
            ) as mock_update_status,
            mock.patch.object(handler.m.discord_rp, "clear_presence") as mock_clear,
            mock.patch.object(handler.sc, "enter") as mock_enter,
        ):
            handler._lastfm_update(mock.sentinel.scheduler_ref)

        mock_update_status.assert_called_once_with("Track Name")
        mock_clear.assert_not_called()
        mock_enter.assert_called_once_with(
            handler.cooldown, 1, handler._lastfm_update, (mock.sentinel.scheduler_ref,)
        )

    def test_track_none(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.ENABLED

        mock_user = mock.Mock()
        mock_user.now_playing.return_value = None
        handler.user = mock_user

        with (
            mock.patch.object(handler.m, "attempt_to_connect_rp") as mock_connect_rp,
            mock.patch.object(
                handler.m.discord_rp, "update_status"
            ) as mock_update_status,
            mock.patch.object(handler.m.discord_rp, "clear_presence") as mock_clear,
            mock.patch.object(handler.sc, "enter") as mock_enter,
        ):
            handler._lastfm_update(mock.sentinel.scheduler_ref)

        mock_connect_rp.assert_not_called()
        mock_update_status.assert_not_called()
        mock_clear.assert_called_once()
        mock_enter.assert_called_once_with(
            handler.cooldown, 1, handler._lastfm_update, (mock.sentinel.scheduler_ref,)
        )
