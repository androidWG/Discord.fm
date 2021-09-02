import tkinter as tk

window = tk.Tk()
window.resizable(0, 0)
window.title("Discord.fm")

frame_user = tk.Frame(master=window)

entry_user = tk.Entry(master=frame_user, width=12)
lbl_user = tk.Label(master=frame_user, text="Last.fm Username")
entry_user.grid(row=0, column=1, sticky="w")
lbl_user.grid(row=0, column=0, sticky="e")

frame_cooldown = tk.Frame(master=window)

entry_cooldown = tk.Entry(master=frame_cooldown, width=8)
lbl_cooldown = tk.Label(master=frame_cooldown, text="Cooldown")
entry_cooldown.grid(row=0, column=1, sticky="w")
lbl_cooldown.grid(row=0, column=0, sticky="e")

check_tray = tk.Checkbutton(text="Tray Icon")
check_update = tk.Checkbutton(text="Auto Update")

frame_buttons = tk.Frame(master=window)

btn_open_logs = tk.Button(master=frame_buttons, text="Open Logs Folder")
btn_restart = tk.Button(master=frame_buttons, text="Restart Service")
btn_open_logs.grid(row=0, column=0, sticky="w")
btn_restart.grid(row=0, column=1, sticky="e")

frame_user.grid(row=0, column=0, padx=10)
frame_cooldown.grid(row=1, column=0, padx=10)
check_tray.grid(row=2, column=0, padx=10)
check_update.grid(row=3, column=0, padx=10)
frame_buttons.grid(row=4, column=0, padx=10)

window.mainloop()
