import subprocess
import sys
import time

import wrappers.last_fm_user
from threading import Thread, Timer, get_ident
from tkinter import *
from tkinter import ttk, messagebox
from repeat_timer import RepeatTimer
from util import process
from settings import local_settings, get_version, get_debug

SMALL_PAD = (4, 0, 4, 0)
LABEL_PAD = (0, 0, 8, 0)
VERT_PAD = 2


class SettingsWindow(Tk):
    stopping = False
    starting = False

    # noinspection PyTypeChecker
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.wm_title("Discord.fm Settings")

        self.root = ttk.Frame(self, padding=(12, 8))

        # region Set up variables
        self.username = StringVar(value=local_settings.get("username"))

        self.cooldown = IntVar(value=local_settings.get("cooldown"))
        self.cld_timelbl_text = StringVar(value=str(self.cooldown.get()) + "s")
        self.cooldown.trace_add("write", lambda x, y, z: self.cld_timelbl_text.set(str(self.cooldown.get()) + "s"))

        self.usr_status_text = StringVar(value="Checking...")
        self.service_btn_text = StringVar(value="Start service")
        self.logs_btn_text = StringVar(value="Open logs folder")
        self.status_lbl_text = StringVar(value="Waiting...")

        self.auto_update = BooleanVar(value=local_settings.get("auto_update"))
        self.auto_update.trace_add("write", lambda: local_settings.define("auto_update", self.auto_update.get()))

        self.pre_releases = BooleanVar(value=local_settings.get("pre_releases"))
        self.pre_releases.trace_add("write", lambda: local_settings.define("pre_releases", self.pre_releases.get()))
        # endregion

        # region Username
        self.debounce = Timer(0.5, self._check_username)

        usr_layout = ttk.Frame(self.root)
        self.usr_lbl = ttk.Label(usr_layout, text="Last.fm Username", padding=LABEL_PAD)
        self.usr_input = ttk.Entry(usr_layout, textvariable=self.username)
        self.usr_input.bind("<KeyPress>", self.call_debounce)
        self.usr_lbl.pack(side=LEFT)
        self.usr_input.pack(side=LEFT, fill=X)
        usr_layout.grid(column=0, sticky=(W, E))

        self.usr_status = ttk.Label(self.root, textvariable=self.usr_status_text, padding=(128, 0, 0, 0))
        self.usr_status.grid(column=0, sticky=W)
        # endregion

        # region Cooldown Slider
        cld_layout = ttk.Frame(self.root)
        cld_lbl = ttk.Label(cld_layout, text="Cooldown", padding=LABEL_PAD)
        self.cld_timelbl = ttk.Label(cld_layout, padding=LABEL_PAD, textvariable=self.cld_timelbl_text)
        self.cld_scale = ttk.Scale(cld_layout, from_=2, to=30, orient=HORIZONTAL, length=200, variable=self.cooldown)

        self.cld_scale.bind("<ButtonRelease>", lambda x: local_settings.define("cooldown", self.cooldown.get()))

        cld_lbl.pack(side=LEFT)
        self.cld_scale.pack(side=LEFT, fill=X)
        self.cld_timelbl.pack(side=LEFT)
        cld_layout.grid(column=0, sticky=(W, E), pady=VERT_PAD)
        # endregion

        # region Buttons
        upd_check = ttk.Checkbutton(self.root, text="Automatically download and install updates",
                                    variable=self.auto_update)
        beta_check = ttk.Checkbutton(self.root, text="Include pre-release versions", variable=self.pre_releases)
        upd_check.grid(column=0, sticky=W, pady=VERT_PAD)
        beta_check.grid(column=0, sticky=W, pady=VERT_PAD)

        btn_layout = ttk.Frame(self.root)
        self.logs_btn = ttk.Button(btn_layout, textvariable=self.logs_btn_text, command=process.open_logs_folder)
        self.service_btn = ttk.Button(btn_layout, textvariable=self.service_btn_text, command=self.call_start_stop)
        self.logs_btn.grid(column=0, row=0, sticky=(W, E), padx=4)
        self.service_btn.grid(column=1, row=0, sticky=(W, E), padx=4)
        btn_layout.columnconfigure(0, weight=1)
        btn_layout.columnconfigure(1, weight=1)
        btn_layout.grid(column=0, sticky=(W, E), pady=VERT_PAD)
        # endregion

        self.root.pack()

        # region Status Bar
        self.bar = ttk.Frame(self)
        self.status_lbl = ttk.Label(self.bar, textvariable=self.status_lbl_text, relief=SUNKEN, padding=SMALL_PAD)
        ver_lbl = ttk.Label(self.bar, text="v" + get_version() + " (debug)" if get_debug() else "", relief=SUNKEN,
                            padding=SMALL_PAD)
        self.status_lbl.grid(column=0, row=0, sticky=(W, E))
        ver_lbl.grid(column=1, row=0)

        self.bar.columnconfigure(0, weight=5)
        self.bar.pack(fill=X)
        # endregion

        self.timer = RepeatTimer(1, self._set_running_status)
        self.timer.start()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        Thread(target=self._check_username).start()

    def on_close(self):
        valid_username = self._check_username(ignore_debounce=True)
        if not valid_username:
            messagebox.showwarning("Warning", "The username you set is not valid. Please change it to a "
                                              "valid username.")
        else:
            self.timer.cancel()
            self.debounce.cancel()

            local_settings.define("username", self.username.get())
            self.destroy()

    def call_start_stop(self):
        def _update():
            nonlocal self
            if self.starting or self.stopping:
                self._set_running_status()

        if process.check_process_running("discord_fm"):
            self.stopping = True
            self.service_btn.text = "Stopping..."

            Thread(target=process.kill_process, args=["discord_fm"]).start()
        else:
            self.starting = True
            self.service_btn.text = "Starting..."

            main_proc = process.ExecutableInfo("Discord.fm",
                                               "discord_fm.exe",
                                               "Discord.fm.app",
                                               "discord_fm")
            Thread(target=subprocess.Popen, args=main_proc.path).start()

        self.service_btn.state("disabled")
        Timer(12, _update)

    def call_debounce(self, value=""):
        self.debounce.cancel()
        self.debounce = Timer(0.5, self._check_username)
        self.usr_status_text.set("Checking...")
        self.debounce.start()

    def _set_running_status(self):
        if not getattr(sys, "frozen", False):
            self.status_lbl_text.set("Cannot check if service is running")
            self.service_btn_text.set("Start service")
            return

        is_running = process.check_process_running("discord_fm")
        if is_running and not self.stopping:
            self.service_btn.state("disabled")
            self.status_lbl_text.set("Running")
            self.service_btn_text.set("Stop service")
            self.starting = False
        elif not is_running and not self.starting:
            self.service_btn.state("enable")
            self.status_lbl_text.set("Stopped")
            self.service_btn_text.set("Start service")
            self.stopping = False

    def _check_username(self, value="", ignore_debounce=False):
        print("Running _check_username")
        if self.debounce.ident is None:
            print("debounce is none")
            pass
        elif self.debounce.ident != get_ident() and not ignore_debounce:
            print(f"ident is different ({self.debounce.ident} vs. {get_ident()})")
            return

        try:
            user = wrappers.last_fm_user.LastFMUser(self.username.get())
            user_valid = user.check_username()
        except ValueError:
            user_valid = False

        if user_valid:
            self.usr_status_text.set("Username is valid")
            return True
        elif not user_valid:
            self.usr_status_text.set("Invalid username")
            return False
        else:
            self.usr_status_text.set("No internet connection")
            return True
