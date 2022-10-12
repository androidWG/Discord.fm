import logging

from PIL import Image
from pystray import Icon, Menu, MenuItem

import util
from util.status import Status

logger = logging.getLogger("discord_fm").getChild(__name__)


class SystemTrayIcon:
    rpc_state = True

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
                lambda ic, it: self.toggle_rpc(it),
                checked=lambda i: self.rpc_state,
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

    def toggle_rpc(self, item):
        self.rpc_state = not item.checked

        if self.rpc_state:
            self.m.discord_rp.connect()
            self.m.status = Status.ENABLED
        else:
            self.m.discord_rp.disconnect()
            self.m.status = Status.DISABLED

        logger.info(f"Changed state to {self.rpc_state}")
