const { app, BrowserWindow } = require("electron");
let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 400,
        height: 365,
        resizable: false,
        title: "Discord.fm Settings",
        webPreferences: {
            nodeIntegration: true,
        },
    });
    mainWindow.loadURL("http://localhost:8000/settings.html");
    mainWindow.setMenu(null);
    mainWindow.on("closed", function () {
        mainWindow = null;
    });

    //mainWindow.webContents.openDevTools();
}

app.whenReady().then(() => {
    createWindow();

    app.on("activate", function () {
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

app.on("window-all-closed", function () {
    if (process.platform !== "darwin") app.quit();
});
