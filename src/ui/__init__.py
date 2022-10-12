from threading import get_ident, Thread, Timer
from tkinter import *
from tkinter import messagebox, ttk

import process
import util.install
import version
import wrappers.last_fm_user
from ui.repeat_timer import RepeatTimer
from util import resource_path

SMALL_PAD = (4, 0, 4, 0)
LABEL_PAD = (0, 0, 8, 0)
VERT_PAD = 2


# noinspection PyUnusedLocal
class SettingsWindow(Tk):
    _stopping = False
    _starting = False
    _last_username = ""

    # noinspection PyTypeChecker
    def __init__(self, manager):
        super().__init__()

        self.m = manager

        self.resizable(False, False)
        self.wm_title("Discord.fm Settings")
        icon = Image("photo", file=resource_path("resources", "settings.png"))
        self.iconphoto(True, icon)

        self.root = ttk.Frame(self, padding=(12, 8))

        # region Set up variables
        self.username = StringVar(value=self.m.settings.get("username"))
        self.username.trace_add(
            "write",
            lambda x, y, z: self.m.settings.define("username", self.username.get()),
        )

        self.cooldown = IntVar(value=self.m.settings.get("cooldown"))
        self.cld_timelbl_text = StringVar(value=str(self.cooldown.get()) + "s")
        self.cooldown.trace_add(
            "write",
            lambda x, y, z: self.cld_timelbl_text.set(str(self.cooldown.get()) + "s"),
        )

        self.usr_status_text = StringVar(value="Checking...")
        self.service_btn_text = StringVar(value="Start service")
        self.logs_btn_text = StringVar(value="Open logs folder")

        self.start_with_system = BooleanVar(
            value=self.m.settings.get("start_with_system")
        )
        self.start_with_system.set(util.install.get_start_with_system())
        self.start_with_system.trace_add(
            "write",
            self._set_start_with_system,
        )

        self.auto_update = BooleanVar(value=self.m.settings.get("auto_update"))
        self.auto_update.trace_add(
            "write",
            lambda: self.m.settings.define("auto_update", self.auto_update.get()),
        )

        self.pre_releases = BooleanVar(value=self.m.settings.get("pre_releases"))
        self.pre_releases.trace_add(
            "write",
            lambda: self.m.settings.define("pre_releases", self.pre_releases.get()),
        )
        # endregion

        # region Username
        self.debounce = Timer(0.5, self._check_username)

        usr_layout = ttk.Frame(self.root)
        self.usr_lbl = ttk.Label(usr_layout, text="Last.fm Username", padding=LABEL_PAD)
        self.usr_input = ttk.Entry(usr_layout, textvariable=self.username)
        self.usr_input.bind("<KeyPress>", self.call_debounce)
        self.usr_lbl.grid(column=0, row=0)
        self.usr_input.grid(column=1, row=0, sticky=(W, E))
        usr_layout.columnconfigure(1, weight=10)
        usr_layout.grid(column=0, sticky=(W, E))

        self.usr_status = ttk.Label(
            self.root, textvariable=self.usr_status_text, padding=(128, 0, 0, 0)
        )
        self.usr_status.grid(column=0, sticky=W)
        # endregion

        # region Cooldown Slider
        cld_layout = ttk.Frame(self.root)
        cld_lbl = ttk.Label(cld_layout, text="Cooldown", padding=LABEL_PAD)
        self.cld_timelbl = ttk.Label(
            cld_layout, padding=(8, 0, 0, 0), textvariable=self.cld_timelbl_text
        )
        self.cld_scale = ttk.Scale(
            cld_layout,
            from_=2,
            to=30,
            orient=HORIZONTAL,
            length=200,
            variable=self.cooldown,
        )

        self.cld_scale.bind(
            "<ButtonRelease>",
            lambda x: self.m.settings.define("cooldown", self.cooldown.get()),
        )

        cld_lbl.pack(side=LEFT)
        self.cld_scale.pack(side=LEFT, fill=X)
        self.cld_timelbl.pack(side=LEFT)
        cld_layout.grid(column=0, sticky=(W, E), pady=VERT_PAD)
        # endregion

        # region Check Buttons
        start_check = ttk.Checkbutton(
            self.root, text="Start with system", variable=self.start_with_system
        )
        upd_check = ttk.Checkbutton(
            self.root,
            text="Automatically download and install updates",
            variable=self.auto_update,
        )
        beta_check = ttk.Checkbutton(
            self.root, text="Include pre-release versions", variable=self.pre_releases
        )
        start_check.grid(column=0, sticky=W, pady=VERT_PAD)
        upd_check.grid(column=0, sticky=W, pady=VERT_PAD)
        beta_check.grid(column=0, sticky=W, pady=VERT_PAD)
        # endregion

        # region Buttons
        logs_btn = ttk.Button(
            self.root,
            textvariable=self.logs_btn_text,
            command=lambda: process.open_in_explorer(self.m.settings.logs_path),
        )
        logs_btn.grid(column=0, sticky=(W, E))
        # endregion

        self.root.pack()

        # region Status Bar
        self.bar = ttk.Frame(self)
        ver_lbl = ttk.Label(
            self.bar,
            text="v" + version.get_version() + " (debug)" if self.m.get_debug() else "",
            padding=SMALL_PAD,
        )
        ver_lbl.grid(column=1, row=0)

        self.bar.columnconfigure(0, weight=5)
        self.bar.pack(fill=X)
        # endregion

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        Thread(target=self._check_username, daemon=True).start()

    def on_close(self):
        if self._last_username != self.username.get():
            self.usr_status_text.set("Checking...")
            valid_username = self._check_username(ignore_debounce=True)
            if not valid_username:
                messagebox.showwarning(
                    "Warning",
                    "The username you set is not valid. Please change it to a "
                    "valid username.",
                )
                return

        self.debounce.cancel()

        self.m.settings.define("username", self.username.get())
        self.destroy()

    def _set_start_with_system(self, v1, v2, v3):
        checked = self.start_with_system.get()
        self.m.settings.define("start_with_system", checked)
        result = util.install.set_start_with_system(
            checked, util.install.get_exe_path()
        )
        self.start_with_system.set(result)

    def call_debounce(self, value=""):
        self.debounce.cancel()
        self.debounce = Timer(0.5, self._check_username)
        self.debounce.start()

    def _check_username(self, value="", ignore_debounce=False):
        print("Running _check_username")
        if self.debounce.ident is None:
            print("debounce is none")
        elif self.debounce.ident != get_ident() and not ignore_debounce:
            print(f"ident is different ({self.debounce.ident} vs. {get_ident()})")
            return

        username = self.username.get()
        try:
            self.usr_status_text.set("Checking...")
            user = wrappers.last_fm_user.LastFMUser(self.m)
            user_valid = user.check_username()
        except ValueError:
            user_valid = False

        if user_valid:
            self.usr_status_text.set("Username is valid")
            self._last_username = username
            return True
        else:
            self.usr_status_text.set("Invalid username")
            return False
