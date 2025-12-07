const { ipcRenderer } = require('electron');
const path = require('path');

// State
let downloads = [];
let settings = {
  outputFolder: path.join(require('os').homedir(), 'Downloads', 'YouTube'),
  downloadType: 'video',
  quality: 'best',
  format: 'mp4',
  audioTrack: 'auto',
  embedThumbnail: false,
  embedMetadata: false
};

// DOM Elements
const addUrlBtn = document.getElementById('addUrlBtn');
const selectFolderBtn = document.getElementById('selectFolderBtn');
const outputFolderInput = document.getElementById('outputFolder');
const outputFolderPath = document.getElementById('outputFolderPath');
const downloadTypeSelect = document.getElementById('downloadType');
const qualitySelect = document.getElementById('quality');
const formatSelect = document.getElementById('format');
const audioTrackSelect = document.getElementById('audioTrack');
const embedThumbnailCheck = document.getElementById('embedThumbnail');
const embedMetadataCheck = document.getElementById('embedMetadata');
const advancedToggle = document.getElementById('advancedToggle');
const advancedToggleIcon = document.getElementById('advancedToggleIcon');
const advancedSettings = document.getElementById('advancedSettings');
const downloadList = document.getElementById('downloadList');
const activeDownloadsSpan = document.getElementById('activeDownloads');
const completedDownloadsSpan = document.getElementById('completedDownloads');

// Initialize
init();

function init() {
  // Set initial output folder
  outputFolderInput.value = settings.outputFolder;
  outputFolderPath.textContent = settings.outputFolder;

  // Event Listeners
  addUrlBtn.addEventListener('click', () => {
    ipcRenderer.send('open-add-url');
  });

  selectFolderBtn.addEventListener('click', async () => {
    const folder = await ipcRenderer.invoke('select-output-folder');
    if (folder) {
      settings.outputFolder = folder;
      outputFolderInput.value = folder;
      outputFolderPath.textContent = folder;
    }
  });

  downloadTypeSelect.addEventListener('change', (e) => {
    settings.downloadType = e.target.value;
    updateFormatOptions();
  });

  qualitySelect.addEventListener('change', (e) => {
    settings.quality = e.target.value;
  });

  formatSelect.addEventListener('change', (e) => {
    settings.format = e.target.value;
  });

  audioTrackSelect.addEventListener('change', (e) => {
    settings.audioTrack = e.target.value;
  });

  embedThumbnailCheck.addEventListener('change', (e) => {
    settings.embedThumbnail = e.target.checked;
  });

  embedMetadataCheck.addEventListener('change', (e) => {
    settings.embedMetadata = e.target.checked;
  });

  advancedToggle.addEventListener('click', () => {
    const isHidden = advancedSettings.style.display === 'none';
    advancedSettings.style.display = isHidden ? 'block' : 'none';
    advancedToggleIcon.textContent = isHidden ? '▼' : '▶';
  });

  // IPC Listeners
  ipcRenderer.on('url-added', (event, urlData) => {
    addDownload(urlData);
  });

  ipcRenderer.on('download-progress', (event, progressData) => {
    updateDownloadProgress(progressData);
  });

  ipcRenderer.on('download-complete', (event, data) => {
    markDownloadComplete(data.id);
  });

  ipcRenderer.on('download-error', (event, data) => {
    markDownloadError(data.id, data.error);
  });
}

function updateFormatOptions() {
  if (settings.downloadType === 'audio') {
    formatSelect.innerHTML = `
      <option value="mp3">MP3</option>
      <option value="m4a">M4A</option>
      <option value="opus">OPUS</option>
      <option value="aac">AAC</option>
    `;
    settings.format = 'mp3';

    // Update quality options for audio
    qualitySelect.innerHTML = `
      <option value="320">320 kbps</option>
      <option value="256">256 kbps</option>
      <option value="192">192 kbps</option>
      <option value="128">128 kbps</option>
    `;
    settings.quality = '192';
  } else {
    formatSelect.innerHTML = `
      <option value="mp4">MP4</option>
      <option value="webm">WebM</option>
      <option value="mkv">MKV</option>
    `;
    settings.format = 'mp4';

    // Update quality options for video
    qualitySelect.innerHTML = `
      <option value="best">Best Available</option>
      <option value="2160p">4K (2160p)</option>
      <option value="1440p">2K (1440p)</option>
      <option value="1080p">1080p (Full HD)</option>
      <option value="720p">720p (HD)</option>
      <option value="480p">480p (SD)</option>
    `;
    settings.quality = 'best';
  }
}

function addDownload(urlData) {
  const download = {
    id: Date.now().toString(),
    url: urlData.url,
    videoInfo: urlData.videoInfo || {},
    status: 'queued', // queued, downloading, completed, error
    progress: 0,
    speed: '',
    eta: '',
    error: null,
    settings: { ...settings }
  };

  downloads.push(download);

  // Update audio track options if available
  if (urlData.videoInfo && urlData.videoInfo.audioTracks) {
    updateAudioTrackOptions(urlData.videoInfo.audioTracks);
  }

  renderDownloads();
  startDownload(download);
}

function updateAudioTrackOptions(audioTracks) {
  if (audioTracks && audioTracks.length > 1) {
    audioTrackSelect.innerHTML = audioTracks
      .map(track => `<option value="${track.id}">${track.language}</option>`)
      .join('');
  }
}

function renderDownloads() {
  if (downloads.length === 0) {
    downloadList.innerHTML = `
      <div class="empty-state">
        <div class="empty-icon">📥</div>
        <p>No downloads yet</p>
        <small>Click "Add URL" to start downloading</small>
      </div>
    `;
    return;
  }

  downloadList.innerHTML = downloads.map(download => {
    const title = download.videoInfo?.title || 'Loading...';
    // Fallback to SVG placeholder if no thumbnail
    const placeholderSvg = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="160" height="90" viewBox="0 0 160 90"%3E%3Crect fill="%23e0e0e0" width="160" height="90"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="12" fill="%23999"%3EThumbnail%3C/text%3E%3C/svg%3E';
    const thumbnail = download.videoInfo?.thumbnail || placeholderSvg;

    return `
      <div class="download-item" data-id="${download.id}">
        <div class="download-thumbnail">
          <img src="${thumbnail}" alt="Thumbnail" onerror="this.src='${placeholderSvg}'">
          <div class="download-status-badge ${download.status}">
            ${getStatusIcon(download.status)}
          </div>
        </div>
        <div class="download-info">
          <div class="download-title">${title}</div>
          <div class="download-meta">
            ${settings.downloadType === 'audio' ? '🎵 Audio' : '🎬 Video'} •
            ${settings.quality} •
            ${settings.format.toUpperCase()}
          </div>
          <div class="download-progress-container">
            <div class="download-progress-bar">
              <div class="download-progress-fill" style="width: ${download.progress}%"></div>
            </div>
            <div class="download-progress-text">
              ${getProgressText(download)}
            </div>
          </div>
        </div>
        <div class="download-actions">
          ${getActionButtons(download)}
        </div>
      </div>
    `;
  }).join('');

  updateStats();
}

function getStatusIcon(status) {
  const icons = {
    queued: '⏳',
    downloading: '⬇️',
    completed: '✅',
    error: '❌'
  };
  return icons[status] || '❓';
}

function getProgressText(download) {
  if (download.status === 'completed') {
    return 'Download complete';
  }
  if (download.status === 'error') {
    return `Error: ${download.error || 'Unknown error'}`;
  }
  if (download.status === 'downloading') {
    return `${download.progress}% • ${download.speed} • ${download.eta}`;
  }
  return 'Queued...';
}

function getActionButtons(download) {
  if (download.status === 'completed') {
    return `
      <button class="btn-icon" onclick="openDownloadFolder('${download.id}')" title="Open folder">
        📁
      </button>
      <button class="btn-icon" onclick="removeDownload('${download.id}')" title="Remove">
        🗑️
      </button>
    `;
  }
  if (download.status === 'error') {
    return `
      <button class="btn-icon" onclick="retryDownload('${download.id}')" title="Retry">
        🔄
      </button>
      <button class="btn-icon" onclick="removeDownload('${download.id}')" title="Remove">
        🗑️
      </button>
    `;
  }
  return `
    <button class="btn-icon" onclick="cancelDownload('${download.id}')" title="Cancel">
      ⏹️
    </button>
  `;
}

function updateStats() {
  const active = downloads.filter(d => d.status === 'downloading' || d.status === 'queued').length;
  const completed = downloads.filter(d => d.status === 'completed').length;

  activeDownloadsSpan.textContent = `${active} active`;
  completedDownloadsSpan.textContent = `${completed} completed`;
}

async function startDownload(download) {
  const downloadObj = downloads.find(d => d.id === download.id);
  if (!downloadObj) return;

  downloadObj.status = 'downloading';
  renderDownloads();

  try {
    // Call the Python backend to start the real download
    const downloadOptions = {
      url: downloadObj.url,
      outputFolder: settings.outputFolder,
      format: downloadObj.settings.format,
      quality: downloadObj.settings.quality,
      downloadType: downloadObj.settings.downloadType,
      audioTrack: downloadObj.settings.audioTrack,
      embedThumbnail: downloadObj.settings.embedThumbnail,
      embedMetadata: downloadObj.settings.embedMetadata
    };

    await ipcRenderer.invoke('start-download', downloadOptions);
  } catch (error) {
    markDownloadError(download.id, error.message);
  }
}

function updateDownloadProgress(progressData) {
  const download = downloads.find(d => d.id === progressData.id);
  if (!download) return;

  download.progress = progressData.progress || 0;
  download.speed = progressData.speed || '';
  download.eta = progressData.eta || '';

  renderDownloads();
}

function markDownloadComplete(downloadId) {
  const download = downloads.find(d => d.id === downloadId);
  if (!download) return;

  download.status = 'completed';
  download.progress = 100;
  renderDownloads();
}

function markDownloadError(downloadId, error) {
  const download = downloads.find(d => d.id === downloadId);
  if (!download) return;

  download.status = 'error';
  download.error = error;
  renderDownloads();
}

// Global functions for button actions
window.openDownloadFolder = (downloadId) => {
  const { shell } = require('electron');
  shell.openPath(settings.outputFolder);
};

window.removeDownload = (downloadId) => {
  downloads = downloads.filter(d => d.id !== downloadId);
  renderDownloads();
};

window.retryDownload = (downloadId) => {
  const download = downloads.find(d => d.id === downloadId);
  if (download) {
    download.status = 'queued';
    download.progress = 0;
    download.error = null;
    startDownload(download);
  }
};

window.cancelDownload = (downloadId) => {
  const download = downloads.find(d => d.id === downloadId);
  if (download) {
    download.status = 'error';
    download.error = 'Cancelled by user';
    renderDownloads();
  }
};
