import logging
import platform
import time
import util
import util.process
import util.updates
import util.log_setup
import globals as g
import wrappers.discord_rp
from PIL import Image
from typing import Callable
from threading import Thread
from pystray import MenuItem, Menu, Icon
from pypresence import InvalidPipe, DiscordNotFound, DiscordError

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
        image_path = util.resource_path(
            "resources/white/icon.png" if util.check_dark_mode() else "resources/black/icon.png")
        icon = Image.open(image_path)

        menu = Menu(MenuItem("Enable Rich Presence", self.toggle_rpc,
                             enabled=lambda i: g.current != g.Status.WAITING_FOR_DISCORD,
                             checked=lambda i: self.rpc_state,
                             visible=lambda i: g.current != g.Status.STARTUP and g.current != g.Status.UPDATING),
                    MenuItem("Open Settings", util.process.open_settings,
                             visible=lambda i: g.current != g.Status.STARTUP and g.current != g.Status.UPDATING),
                    MenuItem("Starting...", None,
                             enabled=False,
                             visible=lambda i: g.current == g.Status.STARTUP),
                    MenuItem("Downloading update...", None,
                             enabled=False,
                             visible=lambda i: g.current == g.Status.UPDATING),
                    Menu.SEPARATOR,
                    MenuItem("Exit", self._exit_func))

        icon = Icon("Discord.fm", icon=icon, title="Discord.fm", menu=menu)
        return icon

    def toggle_rpc(self, icon, item):
        self.rpc_state = not item.checked

        if self.rpc_state:
            self.discord_rp.connect()
            g.current = g.Status.ENABLED
        else:
            self.discord_rp.disconnect()
            g.current = g.Status.DISABLED

        logger.info(f"Changed rpc_state to {self.rpc_state}")

    def wait_for_discord(self):
        g.current = g.Status.WAITING_FOR_DISCORD

        notification_called = False
        self.ti.update_menu()

        while True:
            if util.process.check_process_running("Discord", "DiscordCanary"):
                try:
                    self.discord_rp = wrappers.discord_rp.DiscordRP()
                    self.discord_rp.connect()
                except (FileNotFoundError, InvalidPipe, DiscordNotFound, DiscordError):
                    continue
                except PermissionError as e:
                    if not notification_called and platform.system() == "Windows":
                        logger.critical("Another user has Discord open, notifying user", exc_info=e)

                        title = "Another user has Discord open"
                        message = "Discord.fm will not update your Rich Presence or theirs. Please close the other " \
                                  "instance before scrobbling with this user. "

                        util.basic_notification(title, message)

                        notification_called = True
                    continue

                break
            else:
                time.sleep(10)

        g.current = g.Status.ENABLED
        self.ti.update_menu()
