import unittest
from unittest.mock import patch

import loop_handler
import wrappers
from app_manager import AppManager
from util.status import Status


@patch("wrappers.system_tray_icon.Image")
@patch("util.resource_path")
@patch("settings.Settings")
class TestAppManager(unittest.TestCase):
    @patch("util.is_frozen")
    @patch("process.check_process_running")
    @patch("util.arg_exists")
    @patch("app_manager.AppManager.open_settings")
    def test_perform_checks(
        self,
        mock_open_settings,
        mock_arg_exists,
        mock_check_process_running,
        mock_is_frozen,
        *mocks
    ):
        manager = AppManager()
        manager.status = Status.STARTUP

        mock_is_frozen.return_value = False
        mock_check_process_running.return_value = False
        mock_arg_exists.return_value = False

        with patch.object(manager.settings, "get", return_value=False):
            manager._perform_checks()

        mock_is_frozen.assert_called_once()
        mock_check_process_running.assert_called_once_with("discord_fm", "discord.fm")
        mock_open_settings.assert_not_called()

    @patch("atexit.register")
    @patch("app_manager.AppManager._perform_checks")
    @patch("app_manager.Thread.start")
    @patch("app_manager.system_tray_icon.SystemTrayIcon")
    @patch("loop_handler.LoopHandler")
    @patch("app_manager.AppManager.close")
    def test_start(
        self,
        mock_close,
        mock_loop,
        mock_tray,
        mock_thread_start,
        mock__perform_checks,
        mock_register,
        *mocks
    ):
        manager = AppManager()

        # Test kill status
        manager.status = Status.KILL

        manager.start()

        mock_close.assert_called_once()
        mock_thread_start.assert_not_called()

        mock_thread_start.reset_mock()
        mock_register.reset_mock()
        mock__perform_checks.reset_mock()

        # Test not kill
        manager.status = Status.ENABLED

        manager.start()

        manager.tray_icon.ti.update_menu.assert_called_once()
        manager.tray_icon.ti.run.assert_called_once()

        mock_thread_start.assert_called_once()
        mock_register.assert_called_once_with(manager.close)
        mock__perform_checks.assert_called_once()

    @patch("process.check_process_running")
    @patch("util.arg_exists")
    @patch("util.updates.get_newest_release")
    @patch("util.updates.download_asset")
    @patch("util.install.get_install")
    @patch("version.get_version")
    @patch("app_manager.AppManager.close")
    @patch("app_manager.system_tray_icon.SystemTrayIcon")
    def test_perform_checks_auto_update(
        self,
        mock_tray_icon,
        mock_close,
        mock_get_version,
        mock_get_install,
        mock_download_asset,
        mock_get_newest_release,
        mock_arg_exists,
        mock_check_process_running,
        *mocks
    ):
        manager = AppManager()
        manager.status = Status.STARTUP

        mock_get_version.return_value = 1.0
        mock_get_newest_release.return_value = (2.0, "latest_asset")
        mock_arg_exists.return_value = False
        mock_check_process_running.return_value = False

        with patch.object(manager.settings, "get", return_value=True):
            manager._perform_checks()

        mock_get_newest_release.assert_called_once_with(manager)
        mock_get_version.assert_called_once_with(True)
        mock_check_process_running.assert_called_once_with("discord_fm", "discord.fm")
        manager.tray_icon.ti.update_menu.assert_called_once()
        mock_download_asset.assert_called_once_with(manager, "latest_asset")
        mock_get_install.return_value.install.assert_called_once()
        mock_close.assert_called_once()

    @patch("wrappers.discord_rp.DiscordRP")
    @patch("app_manager.AppManager.close")
    @patch("loop_handler.LoopHandler")
    def test_reload(self, mock_loop, mock_close, mock_discord_rp, *mocks):
        manager = AppManager()
        manager.status = Status.DISABLED

        manager.reload()

        mock_discord_rp.return_value.exit_rp.assert_called_once()
        manager.loop.reload_lastfm.assert_called_once()
        self.assertEqual(manager.status, Status.ENABLED)

    @patch("wrappers.discord_rp.DiscordRP")
    @patch("app_manager.system_tray_icon.SystemTrayIcon")
    @patch("sys.exit")
    def test_close(self, mock_exit, mock_tray, mock_discord_rp, *mocks):
        manager = AppManager()
        manager.status = Status.KILL

        manager.close()

        mock_exit.assert_called_once()
        mock_discord_rp.return_value.exit_rp.assert_called_once()
        mock_tray.return_value.ti.stop.assert_called_once()

    @patch("wrappers.discord_rp.DiscordRP")
    @patch("loop_handler.LoopHandler")
    def test_toggle_rpc(self, mock_discord_rp, *mocks):
        manager = AppManager()
        manager.status = Status.ENABLED

        manager.toggle_rpc(True)

        self.assertEqual(manager.rpc_state, True)
        self.assertEqual(manager.status, Status.ENABLED)
        manager.loop.force_update.assert_called_once()

        manager.toggle_rpc(False)

        self.assertEqual(manager.rpc_state, False)
        self.assertEqual(manager.status, Status.DISABLED)
        manager.discord_rp.disconnect.assert_called_once()
        self.assertEqual(manager.discord_rp.last_track, None)

    @patch("process.check_process_running")
    @patch("time.sleep")
    @patch("util.basic_notification")
    @patch("platform.system")
    @patch("wrappers.discord_rp.DiscordRP")
    def test_attempt_to_connect_rp(
        self,
        mock_discord_rp,
        mock_platform,
        mock_basic_notification,
        mock_sleep,
        mock_check_process_running,
        *mocks
    ):
        manager = AppManager()

        # Test running
        mock_check_process_running.return_value = True
        manager.discord_rp.connected = False

        manager.attempt_to_connect_rp()

        mock_check_process_running.assert_called_once_with("Discord", "DiscordCanary")
        manager.discord_rp.connect.assert_called_once()
        mock_basic_notification.assert_not_called()
        mock_sleep.assert_not_called()

        mock_check_process_running.reset_mock()
        mock_discord_rp.connect.reset_mock()

        # Test not running
        mock_check_process_running.return_value = False

        manager.attempt_to_connect_rp()

        mock_check_process_running.assert_called_once_with("Discord", "DiscordCanary")
        mock_discord_rp.connect.assert_not_called()
        mock_basic_notification.assert_not_called()
        mock_sleep.assert_called_once_with(10)

        mock_check_process_running.reset_mock()
        mock_discord_rp.connect.reset_mock()
        mock_sleep.reset_mock()

        # Test already connected
        manager.discord_rp.connected = True

        manager.attempt_to_connect_rp()

        mock_check_process_running.assert_not_called()
        mock_discord_rp.connect.assert_not_called()
        mock_sleep.assert_not_called()

    @patch("wrappers.discord_rp.DiscordRP")
    def test_disconnect_rp(self, mock_discord_rp, *mocks):
        manager = AppManager()

        manager.disconnect_rp()

        mock_discord_rp.return_value.disconnect.assert_called_once()
        self.assertEqual(manager.discord_rp.last_track, None)

    @patch("ui.SettingsWindow")
    @patch("platform.system")
    @patch("ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID")
    def test_open_settings(
        self, mock_set_app_id, mock_system, mock_settings_window, *mocks
    ):
        manager = AppManager()

        mock_system.return_value = "Windows"

        manager.open_settings()

        mock_set_app_id.assert_called_once()
        mock_settings_window.assert_called_once()
