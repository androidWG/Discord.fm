import logging
import os
import platform
import tkinter

import pystray
from PIL import Image

import util
from util.scrobble_status import ScrobbleStatus
from util.status import Status

logger = logging.getLogger("discord_fm").getChild(__name__)


class SystemTrayIcon:
    def __init__(self, manager):
        self.m = manager

        self._exit_func = manager.close
        if platform.system() == "Darwin":
            # TkInter can only create a new NSApplication instance when it is initialized. pystray uses the shared
            # one or creates one. To avoid NSApplication macOSVersion error when the settings UI is opened,
            # create a dummy hidden Tk instance so pystray can use it's NSApplication.
            class DummyWindow(tkinter.Tk):
                def __init__(self):
                    super().__init__()
                    self.withdraw()

            dummy = DummyWindow()
            dummy.destroy()
        self.ti = self.create_tray_icon()

        if platform.system() == "Linux":
            # Make sure appindicator is used on Linux. For some reason, pystray will always default to X11
            os.environ["PYSTRAY_BACKEND"] = "appindicator"

    def _get_current_scrobbling(self) -> tuple[str | None, str | None]:
        try:
            track = self.m.loop.get_last_track()
            return track.name, track.artist
        except AttributeError:
            return None, None

    def _create_menu(self) -> pystray.Menu:
        return pystray.Menu(
            pystray.MenuItem(
                "Starting...",
                None,
                enabled=False,
                visible=lambda i: self.m.status == Status.STARTUP,
            ),
            pystray.MenuItem(
                "Downloading update...",
                None,
                enabled=False,
                visible=lambda i: self.m.status == Status.UPDATING,
            ),
            pystray.MenuItem(
                "Discord not open",
                None,
                enabled=False,
                visible=lambda i: self.m.status == Status.WAITING_FOR_DISCORD,
            ),
            pystray.MenuItem(
                "Not scrobbling anything",
                None,
                enabled=False,
                visible=lambda i: self.m.scrobble_status
                == ScrobbleStatus.NOT_SCROBBLING,
            ),
            pystray.MenuItem(
                f"Scrobbling {self._get_current_scrobbling()[0]} by {self._get_current_scrobbling()[1]}",
                None,
                enabled=False,
                visible=lambda i: self.m.scrobble_status == ScrobbleStatus.SCROBBLING
                and self.m.status == Status.ENABLED,
            ),
            pystray.MenuItem(
                "Checking current scrobbling...",
                None,
                enabled=False,
                visible=lambda i: self.m.scrobble_status == ScrobbleStatus.FIRST_CHECK
                and self.m.status != Status.WAITING_FOR_DISCORD,
            ),
            pystray.MenuItem(
                "Enable Rich Presence",
                lambda ic, it: self.m.toggle_rpc(not it.checked),
                checked=lambda i: self.m.rpc_state,
                visible=lambda i: self.m.status != Status.STARTUP
                and self.m.status != Status.UPDATING
                and self.m.status != Status.WAITING_FOR_DISCORD,
            ),
            pystray.MenuItem(
                "Open Settings",
                self.m.open_settings,
                visible=lambda i: self.m.status != Status.STARTUP
                and self.m.status != Status.UPDATING,
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", lambda: self._exit_func()),
        )

    def update_tray_icon(self):
        self.ti.menu = self._create_menu()

    def create_tray_icon(self):
        logger.debug("Creating tray icon")
        image_path = util.resource_path(
            "resources", "white" if util.check_dark_mode() else "black", "icon.png"
        )
        icon = Image.open(image_path)

        menu = self._create_menu()

        icon = pystray.Icon("Discord.fm", icon=icon, title="Discord.fm", menu=menu)
        return icon
