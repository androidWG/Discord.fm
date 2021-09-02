const { app, BrowserWindow } = require("electron");
let mainWindow;

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 400,
        height: 400,
        resizable: false,
        webPreferences: {
            nodeIntegration: true,
        },
    });
    mainWindow.loadURL("http://localhost:8000/settings.html");
    mainWindow.setMenu(null);
    mainWindow.on("closed", function () {
        mainWindow = null;
    });
}

app.whenReady().then(() => {
    createWindow();

    app.on("activate", function () {
        // On macOS it's common to re-create a window in the app when the
        // dock icon is clicked and there are no other windows open.
        if (BrowserWindow.getAllWindows().length === 0) createWindow();
    });
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on("window-all-closed", function () {
    if (process.platform !== "darwin") app.quit();
});
