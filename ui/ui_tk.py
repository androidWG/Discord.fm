from tkinter import *
from tkinter import ttk as tk
from settings import local_settings, get_version, get_debug

LABEL_PAD = (0, 0, 8, 0)
VERT_PAD = 2

window = Tk()
root = tk.Frame(window, padding=(12, 8))

username_layout = tk.Frame(root)
username_label = tk.Label(username_layout, text="Last.fm Username", padding=LABEL_PAD)
username_input = tk.Entry(username_layout)
username_label.pack(side=LEFT)
username_input.pack(side=LEFT, fill=X)
username_layout.grid(column=0, sticky=(W, E))

username_status = tk.Label(root, text="Checking...", padding=(80, 0, 0, 0))
username_status.grid(column=0, sticky=W)

# region Cooldown Slider
cooldown_value = local_settings.get("cooldown")
cooldown_layout = tk.Frame(root)
cooldown_label = tk.Label(cooldown_layout, text="Cooldown", padding=LABEL_PAD)
cooldown_timelabel = tk.Label(cooldown_layout, text=str(cooldown_value) + "s", padding=LABEL_PAD)
cooldown_slider = tk.Scale(cooldown_layout, from_=2, to=30, orient=HORIZONTAL, length=200)
# cooldown_slider.sliderReleased.connect(
#     lambda: save_setting("cooldown", cooldown_slider.value()))
# cooldown_slider.valueChanged.connect(
#     lambda: cooldown_label.setText(f"{cooldown_slider.value()}s"))
cooldown_label.pack(side=LEFT)
cooldown_slider.pack(side=LEFT, fill=X)
cooldown_timelabel.pack(side=LEFT)
cooldown_layout.grid(column=0, sticky=(W, E), pady=VERT_PAD)
# endregion

# region Buttons
auto_update_check = tk.Checkbutton(root, text="Automatically download and install updates")
pre_releases_check = tk.Checkbutton(root, text="Include pre-release versions")
# auto_update_check.stateChanged.connect(
#     lambda: save_setting("auto_update", auto_update_check.isChecked()))
# pre_releases_check.stateChanged.connect(
#     lambda: save_setting("pre_releases", pre_releases_check.isChecked()))
auto_update_check.grid(column=0, sticky=W, pady=VERT_PAD)
pre_releases_check.grid(column=0, sticky=W, pady=VERT_PAD)

buttons_layout = tk.Frame(root)
logs_button = tk.Button(buttons_layout, text="Open logs folder")
# logs_button.clicked.connect(util.process.open_logs_folder)
service_button = tk.Button(buttons_layout, text="Start service")
# service_button.clicked.connect(
#     lambda: call_start_stop())
logs_button.grid(column=0, row=0, sticky=(W, E), padx=4)
service_button.grid(column=1, row=0, sticky=(W, E), padx=4)
buttons_layout.columnconfigure(0, weight=1)
buttons_layout.columnconfigure(1, weight=1)
buttons_layout.grid(column=0, sticky=(W, E), pady=VERT_PAD)
# endregion

root.pack()

# region Status Bar
status_bar = tk.Frame(window)
status_label = tk.Label(status_bar, text="Waiting...", relief=SUNKEN)
version_label = tk.Label(status_bar, text="v" + get_version() + " (debug)" if get_debug() else "", relief=SUNKEN, padding=(8, 0, 0, 0))
status_label.grid(column=0, row=0, sticky=(W, E))
version_label.grid(column=1, row=0)
status_bar.columnconfigure(0, weight=5)
status_bar.pack(fill=X)
# endregion

window.resizable(False, False)
window.mainloop()
