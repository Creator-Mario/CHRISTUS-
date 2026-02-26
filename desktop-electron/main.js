/**
 * CHRISTUS Desktop App – Electron main process
 *
 * Loads the web app entirely from local bundled files (www/).
 * No internet connection is required during normal operation.
 * The Service Worker is not used in the Electron context because
 * file:// protocol does not support SW; all assets are local anyway.
 */
'use strict';

const { app, BrowserWindow, shell } = require('electron');
const path = require('path');

let mainWindow = null;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 860,
    minWidth: 360,
    minHeight: 600,
    icon: path.join(__dirname, 'www', 'app', 'icons', 'icon-512.png'),
    title: 'Jesus Christus – Retter & Kompass',
    backgroundColor: '#0f1028',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      // Service Workers are not used in the file:// context
      // (all assets are already bundled locally).
    },
  });

  // Load the app from the locally bundled files – fully offline
  mainWindow.loadFile(path.join(__dirname, 'www', 'index.html'));

  // Hide the default menu bar
  mainWindow.setMenuBarVisibility(false);

  // Open external links (e.g. Bible references) in the system browser
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    if (url.startsWith('http://') || url.startsWith('https://')) {
      shell.openExternal(url);
      return { action: 'deny' };
    }
    return { action: 'allow' };
  });

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  // On macOS it is conventional to keep the app running
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (!mainWindow) createWindow();
});
