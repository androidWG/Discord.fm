function updateBadge(value) {
    document.getElementById("cooldown-time-badge").innerHTML = value + "s";
}

window.addEventListener("load", setInitialValues, false);

function setInitialValues() {
    eel.get_settings()().then((settings) => {
        document.getElementById("username").value = settings["username"];
        document.getElementById("cooldown").value = settings["cooldown"];
        updateBadge(settings["cooldown"]);
        document.getElementById("tray-icon").checked = settings["tray_icon"];
        document.getElementById("auto-update").checked =
            settings["auto_update"];
    });
}

window.addEventListener("load", setInitialValues, false);
setInterval(updateRunning, 500);
