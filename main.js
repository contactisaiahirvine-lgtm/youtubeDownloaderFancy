const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let mainWindow;
let addUrlWindow;

function createMainWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true
    },
    icon: path.join(__dirname, 'assets/icon.png')
  });

  mainWindow.loadFile('index.html');

  // Open DevTools in development mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function createAddUrlWindow() {
  if (addUrlWindow) {
    addUrlWindow.focus();
    return;
  }

  addUrlWindow = new BrowserWindow({
    width: 600,
    height: 400,
    parent: mainWindow,
    modal: true,
    show: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    },
    resizable: false,
    minimizable: false,
    maximizable: false
  });

  addUrlWindow.loadFile('add-url.html');

  addUrlWindow.once('ready-to-show', () => {
    addUrlWindow.show();
  });

  addUrlWindow.on('closed', () => {
    addUrlWindow = null;
  });
}

app.whenReady().then(() => {
  createMainWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createMainWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// IPC Handlers

// Open Add URL window
ipcMain.on('open-add-url', () => {
  createAddUrlWindow();
});

// Close Add URL window
ipcMain.on('close-add-url', () => {
  if (addUrlWindow) {
    addUrlWindow.close();
  }
});

// Select output folder
ipcMain.handle('select-output-folder', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory', 'createDirectory']
  });

  if (!result.canceled && result.filePaths.length > 0) {
    return result.filePaths[0];
  }
  return null;
});

// Get video info from Python backend
ipcMain.handle('get-video-info', async (event, url) => {
  return new Promise((resolve, reject) => {
    const pythonPath = path.join(__dirname, 'youtubeDownloader', 'youtube_downloader.py');
    const python = spawn('python3', [pythonPath, '--info', url]);

    let dataString = '';
    let errorString = '';

    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorString += data.toString();
    });

    python.on('close', (code) => {
      if (code !== 0) {
        reject(new Error(errorString || 'Failed to get video info'));
      } else {
        try {
          const info = JSON.parse(dataString);
          resolve(info);
        } catch (err) {
          reject(new Error('Failed to parse video info'));
        }
      }
    });
  });
});

// Start download
ipcMain.handle('start-download', async (event, downloadOptions) => {
  return new Promise((resolve, reject) => {
    const pythonPath = path.join(__dirname, 'youtubeDownloader', 'youtube_downloader.py');
    const args = ['--download', JSON.stringify(downloadOptions)];
    const python = spawn('python3', [pythonPath, ...args]);

    const downloadId = Date.now().toString();

    python.stdout.on('data', (data) => {
      const output = data.toString();
      // Parse progress updates and send to renderer
      try {
        const progressData = JSON.parse(output);
        mainWindow.webContents.send('download-progress', {
          id: downloadId,
          ...progressData
        });
      } catch (err) {
        // Not JSON, probably log output
        console.log(output);
      }
    });

    python.stderr.on('data', (data) => {
      console.error(data.toString());
      mainWindow.webContents.send('download-error', {
        id: downloadId,
        error: data.toString()
      });
    });

    python.on('close', (code) => {
      if (code === 0) {
        mainWindow.webContents.send('download-complete', { id: downloadId });
        resolve(downloadId);
      } else {
        reject(new Error('Download failed'));
      }
    });

    // Return download ID immediately
    resolve(downloadId);
  });
});

// Add URL from modal to main window
ipcMain.on('add-url-submit', (event, urlData) => {
  if (mainWindow) {
    mainWindow.webContents.send('url-added', urlData);
  }
  if (addUrlWindow) {
    addUrlWindow.close();
  }
});
