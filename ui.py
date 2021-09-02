import eel.browsers


eel.init("web")
eel.browsers.set_path("electron", "C:\\Users\\samu-\\Repos\\Discord.fm\\node_modules\\electron\\dist\\electron.exe")
eel.start("settings.html", mode="electron")
