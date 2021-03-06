import logging
import time
import globals as g
import wrappers.discord_rp
from PIL import Image
from struct import error
from platform import system
from typing import Callable
from threading import Thread
from pystray import MenuItem, Menu, Icon
from pypresence import InvalidPipe, DiscordNotFound, DiscordError
from util import process, basic_notification, resource_path, check_dark_mode

logger = logging.getLogger("discord_fm").getChild(__name__)


class SystemTrayIcon:
    rpc_state = True

    def __init__(self, exit_func: Callable):
        self._exit_func = exit_func
        self.ti = self.create_tray_icon()

        self.discord_rp = None
        self.wait_for_discord()

        Thread(target=self.ti.run).start()

    def create_tray_icon(self):
        logger.debug("Creating tray icon")
        image_path = resource_path(
            "resources/white/icon.png" if check_dark_mode() else "resources/black/icon.png")
        icon = Image.open(image_path)

        menu = Menu(MenuItem("Enable Rich Presence", lambda ic, it: self.toggle_rpc(it),
                             enabled=lambda i: g.current != g.Status.WAITING_FOR_DISCORD,
                             checked=lambda i: self.rpc_state,
                             visible=lambda i: g.current != g.Status.STARTUP and g.current != g.Status.UPDATING),
                    MenuItem("Open Settings", lambda: process.open_settings(),
                             visible=lambda i: g.current != g.Status.STARTUP and g.current != g.Status.UPDATING),
                    MenuItem("Starting...", None,
                             enabled=False,
                             visible=lambda i: g.current == g.Status.STARTUP),
                    MenuItem("Downloading update...", None,
                             enabled=False,
                             visible=lambda i: g.current == g.Status.UPDATING),
                    Menu.SEPARATOR,
                    MenuItem("Exit", lambda: self._exit_func()))

        icon = Icon("Discord.fm", icon=icon, title="Discord.fm", menu=menu)
        return icon

    def toggle_rpc(self, item):
        self.rpc_state = not item.checked

        if self.rpc_state:
            self.discord_rp.connect()
            g.current = g.Status.ENABLED
        else:
            self.discord_rp.disconnect()
            g.current = g.Status.DISABLED

        logger.info(f"Changed state to {self.rpc_state}")

    def wait_for_discord(self):
        g.current = g.Status.WAITING_FOR_DISCORD
        logger.info("Attempting to connect to Discord")

        notification_called = False
        self.ti.update_menu()

        while True:
            if process.check_process_running("Discord", "DiscordCanary"):
                try:
                    self.discord_rp = wrappers.discord_rp.DiscordRP()
                    self.discord_rp.connect()
                    logger.info("Successfully connected to Discord")
                except (FileNotFoundError, InvalidPipe, DiscordNotFound, DiscordError, ValueError, error) as e:
                    logger.debug(f"Received {e}")
                    continue
                except PermissionError as e:
                    if not notification_called and system() == "Windows":
                        logger.critical("Another user has Discord open, notifying user", exc_info=e)

                        title = "Another user has Discord open"
                        message = "Discord.fm will not update your Rich Presence or theirs. Please close the other " \
                                  "instance before scrobbling with this user. "

                        basic_notification(title, message)

                        notification_called = True
                    continue

                break
            else:
                time.sleep(10)

        g.current = g.Status.ENABLED
        self.ti.update_menu()
