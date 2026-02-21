'use strict';

const { app, BrowserWindow, shell, Menu } = require('electron');
const path = require('path');

function createWindow () {
  const win = new BrowserWindow({
    width: 900,
    height: 720,
    minWidth: 360,
    minHeight: 500,
    title: 'Buch des Dienstes zur Evangelisation',
    backgroundColor: '#0d1b2a',
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      // Service Workers not needed; all data is embedded in app.html
    },
  });

  // All Bible data is embedded in app.html (no network needed)
  win.loadFile(path.join(__dirname, 'app.html'));

  win.once('ready-to-show', () => win.show());

  // Open any navigated URLs in the default browser instead
  win.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });

  // Suppress "Failed to register a ServiceWorker" noise on file://
  win.webContents.on('console-message', (_e, _level, msg) => {
    if (msg.includes('ServiceWorker') || msg.includes('manifest')) return;
  });
}

// Minimal application menu (removes default Electron menu clutter)
function buildMenu () {
  const isMac = process.platform === 'darwin';
  const template = [
    ...(isMac ? [{ role: 'appMenu' }] : []),
    { role: 'editMenu' },
    {
      label: 'Ansicht',
      submenu: [
        { role: 'reload' },
        { role: 'togglefullscreen' },
        { role: 'toggleDevTools' },
      ],
    },
    { role: 'windowMenu' },
  ];
  Menu.setApplicationMenu(Menu.buildFromTemplate(template));
}

app.whenReady().then(() => {
  buildMenu();
  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
