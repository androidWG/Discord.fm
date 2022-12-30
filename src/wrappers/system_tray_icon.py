import logging

from PIL import Image
from pystray import Icon, Menu, MenuItem

import util
from util.status import Status

logger = logging.getLogger("discord_fm").getChild(__name__)


class SystemTrayIcon:
    def __init__(self, manager):
        self.m = manager

        self._exit_func = manager.close
        self.ti = self.create_tray_icon()

    def create_tray_icon(self):
        logger.debug("Creating tray icon")
        image_path = util.resource_path(
            "resources", "white" if util.check_dark_mode() else "black", "icon.png"
        )
        icon = Image.open(image_path)

        menu = Menu(
            MenuItem(
                "Enable Rich Presence",
                lambda ic, it: self.m.toggle_rpc(not it.checked),
                checked=lambda i: self.m.rpc_state,
                visible=lambda i: self.m.status != Status.STARTUP
                and self.m.status != Status.UPDATING
                and self.m.status != Status.WAITING_FOR_DISCORD,
            ),
            MenuItem(
                "Open Settings",
                self.m.open_settings,
                visible=lambda i: self.m.status != Status.STARTUP
                and self.m.status != Status.UPDATING,
            ),
            MenuItem(
                "Starting...",
                None,
                enabled=False,
                visible=lambda i: self.m.status == Status.STARTUP,
            ),
            MenuItem(
                "Downloading update...",
                None,
                enabled=False,
                visible=lambda i: self.m.status == Status.UPDATING,
            ),
            MenuItem(
                "Discord not open",
                None,
                enabled=False,
                visible=lambda i: self.m.status == Status.WAITING_FOR_DISCORD,
            ),
            Menu.SEPARATOR,
            MenuItem("Exit", lambda: self._exit_func()),
        )

        icon = Icon("Discord.fm", icon=icon, title="Discord.fm", menu=menu)
        return icon
