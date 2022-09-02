import logging
from threading import Thread
from typing import Callable

from PIL import Image
from pystray import Icon, Menu, MenuItem

import globals as g
import process
from util import check_dark_mode, resource_path

logger = logging.getLogger("discord_fm").getChild(__name__)


class SystemTrayIcon:
    rpc_state = True

    def __init__(self, exit_func: Callable):
        self._exit_func = exit_func
        self.ti = self.create_tray_icon()

    def create_tray_icon(self):
        logger.debug("Creating tray icon")
        image_path = resource_path(
            "resources", "white" if check_dark_mode() else "black", "icon.png"
        )
        icon = Image.open(image_path)

        menu = Menu(
            MenuItem(
                "Enable Rich Presence",
                lambda ic, it: self.toggle_rpc(it),
                checked=lambda i: self.rpc_state,
                visible=lambda i: g.current != g.Status.STARTUP
                and g.current != g.Status.UPDATING
                and g.current != g.Status.WAITING_FOR_DISCORD,
            ),
            MenuItem(
                "Open Settings",
                lambda: process.open_settings(),
                visible=lambda i: g.current != g.Status.STARTUP
                and g.current != g.Status.UPDATING,
            ),
            MenuItem(
                "Starting...",
                None,
                enabled=False,
                visible=lambda i: g.current == g.Status.STARTUP,
            ),
            MenuItem(
                "Downloading update...",
                None,
                enabled=False,
                visible=lambda i: g.current == g.Status.UPDATING,
            ),
            MenuItem(
                "Discord not open",
                None,
                enabled=False,
                visible=lambda i: g.current == g.Status.WAITING_FOR_DISCORD,
            ),
            Menu.SEPARATOR,
            MenuItem("Exit", lambda: self._exit_func()),
        )

        icon = Icon("Discord.fm", icon=icon, title="Discord.fm", menu=menu)
        return icon

    def toggle_rpc(self, item):
        self.rpc_state = not item.checked

        if self.rpc_state:
            g.discord_rp.connect()
            g.current = g.Status.ENABLED
        else:
            g.discord_rp.disconnect()
            g.current = g.Status.DISABLED

        logger.info(f"Changed state to {self.rpc_state}")
