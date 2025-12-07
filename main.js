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
    const bridgePath = path.join(__dirname, 'youtubeDownloader', 'electron_bridge.py');
    const python = spawn('python3', [bridgePath, 'get-info', url]);

    let dataString = '';
    let errorString = '';

    python.stdout.on('data', (data) => {
      dataString += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorString += data.toString();
    });

    python.on('close', (code) => {
      try {
        const info = JSON.parse(dataString.trim());
        if (info.success) {
          resolve(info);
        } else {
          reject(new Error(info.error || 'Failed to get video info'));
        }
      } catch (err) {
        reject(new Error(errorString || 'Failed to parse video info'));
      }
    });
  });
});

// Start download
ipcMain.handle('start-download', async (event, downloadOptions) => {
  return new Promise((resolve, reject) => {
    const bridgePath = path.join(__dirname, 'youtubeDownloader', 'electron_bridge.py');
    const downloadId = Date.now().toString();

    // Convert download options to match bridge expectations
    const bridgeOptions = {
      url: downloadOptions.url,
      outputFolder: downloadOptions.outputFolder || path.join(require('os').homedir(), 'Downloads', 'YouTube'),
      format: downloadOptions.format || 'mp4',
      quality: downloadOptions.quality || 'best',
      audioOnly: downloadOptions.downloadType === 'audio',
      audioTrack: downloadOptions.audioTrack || 'auto',
      embedThumbnail: downloadOptions.embedThumbnail || false,
      embedMetadata: downloadOptions.embedMetadata !== false
    };

    const python = spawn('python3', [bridgePath, 'download', JSON.stringify(bridgeOptions)]);

    let outputBuffer = '';

    python.stdout.on('data', (data) => {
      outputBuffer += data.toString();

      // Process line by line for JSON messages
      const lines = outputBuffer.split('\n');
      outputBuffer = lines.pop(); // Keep incomplete line in buffer

      lines.forEach(line => {
        if (!line.trim()) return;

        try {
          const message = JSON.parse(line);

          if (message.type === 'progress') {
            mainWindow.webContents.send('download-progress', {
              id: downloadId,
              progress: message.progress,
              speed: message.speed,
              eta: message.eta
            });
          } else if (message.type === 'complete') {
            mainWindow.webContents.send('download-complete', {
              id: downloadId,
              filename: message.filename
            });
          } else if (message.type === 'error') {
            mainWindow.webContents.send('download-error', {
              id: downloadId,
              error: message.error
            });
          }
        } catch (err) {
          // Not JSON, could be regular output
          console.log(line);
        }
      });
    });

    python.stderr.on('data', (data) => {
      const errorMsg = data.toString();
      console.error('Python stderr:', errorMsg);
    });

    python.on('close', (code) => {
      if (code !== 0) {
        mainWindow.webContents.send('download-error', {
          id: downloadId,
          error: 'Download process exited with error'
        });
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
