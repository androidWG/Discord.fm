from tkinter import *
from tkinter import ttk
from settings import local_settings, get_version, get_debug

SMALL_PAD = (4, 0, 4, 0)
LABEL_PAD = (0, 0, 8, 0)
VERT_PAD = 2


class SettingsWindow(Tk):
    def __init__(self):
        super().__init__()
        self.resizable(False, False)
        self.wm_title("Discord.fm Settings")

        self.root = ttk.Frame(self, padding=(12, 8))

        usr_layout = ttk.Frame(self.root)
        self.usr_lbl = ttk.Label(usr_layout, text="Last.fm Username", padding=LABEL_PAD)
        self.usr_input = ttk.Entry(usr_layout)
        self.usr_lbl.pack(side=LEFT)
        self.usr_input.pack(side=LEFT, fill=X)
        usr_layout.grid(column=0, sticky=(W, E))

        self.usr_status = ttk.Label(self.root, text="Checking...", padding=(128, 0, 0, 0))
        self.usr_status.grid(column=0, sticky=W)

        # region Cooldown Slider
        cooldown = local_settings.get("cooldown")
        cld_layout = ttk.Frame(self.root)
        cld_lbl = ttk.Label(cld_layout, text="Cooldown", padding=LABEL_PAD)
        self.cld_timelbl = ttk.Label(cld_layout, text=str(cooldown) + "s", padding=LABEL_PAD)
        self.cld_scale = ttk.Scale(cld_layout, from_=2, to=30, orient=HORIZONTAL, length=200, value=cooldown)
        # cld_scale.sliderReleased.connect(
        #     lambda: save_setting("cooldown", cld_scale.value()))
        # cld_scale.valueChanged.connect(
        #     lambda: cld_lbl.setText(f"{cld_scale.value()}s"))
        cld_lbl.pack(side=LEFT)
        self.cld_scale.pack(side=LEFT, fill=X)
        self.cld_timelbl.pack(side=LEFT)
        cld_layout.grid(column=0, sticky=(W, E), pady=VERT_PAD)
        # endregion

        # region Buttons
        upd_check = ttk.Checkbutton(self.root, text="Automatically download and install updates")
        beta_check = ttk.Checkbutton(self.root, text="Include pre-release versions")
        # upd_check.stateChanged.connect(
        #     lambda: save_setting("auto_update", upd_check.isChecked()))
        # beta_check.stateChanged.connect(
        #     lambda: save_setting("pre_releases", beta_check.isChecked()))
        upd_check.grid(column=0, sticky=W, pady=VERT_PAD)
        beta_check.grid(column=0, sticky=W, pady=VERT_PAD)

        btn_layout = ttk.Frame(self.root)
        self.logs_btn = ttk.Button(btn_layout, text="Open logs folder")
        # self.logs_btn.clicked.connect(util.process.open_logs_folder)
        self.service_btn = ttk.Button(btn_layout, text="Start service")
        # self.service_btn.clicked.connect(
        #     lambda: call_start_stop())
        self.logs_btn.grid(column=0, row=0, sticky=(W, E), padx=4)
        self.service_btn.grid(column=1, row=0, sticky=(W, E), padx=4)
        btn_layout.columnconfigure(0, weight=1)
        btn_layout.columnconfigure(1, weight=1)
        btn_layout.grid(column=0, sticky=(W, E), pady=VERT_PAD)
        # endregion

        self.root.pack()

        # region Status Bar
        self.bar = ttk.Frame(self)
        self.status_lbl = ttk.Label(self.bar, text="Waiting...", relief=SUNKEN, padding=SMALL_PAD)
        ver_lbl = ttk.Label(self.bar, text="v" + get_version() + " (debug)" if get_debug() else "", relief=SUNKEN,
                            padding=SMALL_PAD)
        self.status_lbl.grid(column=0, row=0, sticky=(W, E))
        ver_lbl.grid(column=1, row=0)

        self.bar.columnconfigure(0, weight=5)
        self.bar.pack(fill=X)
        # endregion
