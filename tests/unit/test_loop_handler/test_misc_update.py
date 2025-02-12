from unittest import mock
from unittest.mock import MagicMock, patch

from loop_handler import LoopHandler
from util.status import Status


@patch("wrappers.last_fm_user.LastFMUser")
@patch("loop_handler.SystemTrayIcon")
@patch("loop_handler.TrackInfo")
@patch("loop_handler.Image")
@patch("loop_handler.scheduler")
class TestMiscUpdate:
    manager = MagicMock()

    def test_misc_update_disabled_status(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.DISABLED

        with mock.patch.object(handler.sc, "enter") as mock_enter:
            handler._misc_update(mock.sentinel.misc_scheduler)

        mock_enter.assert_called_once_with(
            handler.misc_cooldown,
            2,
            handler._misc_update,
            (mock.sentinel.misc_scheduler,),
        )

    def test_misc_update_kill_status(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.KILL

        handler._misc_update(mock.sentinel.misc_scheduler)

        # Assert that no further actions are taken

    def test_misc_update_username_changed(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.ENABLED
        handler.m.settings.get.return_value = "OldUsername"
        handler.user.user.name = "NewUsername"

        with (
            mock.patch.object(handler.m, "reload") as mock_reload,
            mock.patch.object(handler.sc, "enter") as mock_enter,
        ):
            handler._misc_update(mock.sentinel.misc_scheduler)

        mock_reload.assert_called_once()
        mock_enter.assert_called_once_with(
            handler.misc_cooldown,
            2,
            handler._misc_update,
            (mock.sentinel.misc_scheduler,),
        )

    def test_misc_update_username_not_changed(self, *mocks):
        handler = LoopHandler(self.manager)
        handler.m.status = Status.ENABLED
        handler.m.settings.get.return_value = "OldUsername"
        handler.user.user.name = "OldUsername"

        with (
            mock.patch.object(handler.m, "reload") as mock_reload,
            mock.patch.object(handler.sc, "enter") as mock_enter,
        ):
            handler._misc_update(mock.sentinel.misc_scheduler)

        mock_reload.assert_not_called()
        mock_enter.assert_called_once_with(
            handler.misc_cooldown,
            2,
            handler._misc_update,
            (mock.sentinel.misc_scheduler,),
        )
