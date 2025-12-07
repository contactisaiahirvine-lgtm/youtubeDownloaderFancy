const { ipcRenderer } = require('electron');

let currentVideoInfo = null;

// DOM Elements
const urlInput = document.getElementById('urlInput');
const getInfoBtn = document.getElementById('getInfoBtn');
const cancelBtn = document.getElementById('cancelBtn');
const addBtn = document.getElementById('addBtn');
const previewSection = document.getElementById('previewSection');
const loadingIndicator = document.getElementById('loadingIndicator');
const previewContent = document.getElementById('previewContent');
const previewTitle = document.getElementById('previewTitle');
const previewThumbnail = document.getElementById('previewThumbnail');
const audioTracksInfo = document.getElementById('audioTracksInfo');
const errorMessage = document.getElementById('errorMessage');

// Event Listeners
getInfoBtn.addEventListener('click', async () => {
  const url = urlInput.value.trim();

  if (!url) {
    showError('Please enter a YouTube URL');
    return;
  }

  // Basic URL validation
  if (!url.includes('youtube.com') && !url.includes('youtu.be')) {
    showError('Please enter a valid YouTube URL');
    return;
  }

  await fetchVideoInfo(url);
});

cancelBtn.addEventListener('click', () => {
  ipcRenderer.send('close-add-url');
});

addBtn.addEventListener('click', () => {
  const url = urlInput.value.trim();

  if (!url) {
    showError('Please enter a URL');
    return;
  }

  // Send URL data to main window
  ipcRenderer.send('add-url-submit', {
    url: url,
    videoInfo: currentVideoInfo
  });
});

// Auto-enable add button when URL is entered
urlInput.addEventListener('input', () => {
  const url = urlInput.value.trim();
  addBtn.disabled = !url;
  hideError();
});

// Allow Enter key to get info
urlInput.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && e.ctrlKey) {
    getInfoBtn.click();
  }
});

async function fetchVideoInfo(url) {
  try {
    hideError();
    showLoading();

    // Call the Python backend via IPC to get real video info
    const info = await ipcRenderer.invoke('get-video-info', url);

    if (!info.success) {
      throw new Error(info.error || 'Failed to get video info');
    }

    currentVideoInfo = info;
    displayVideoInfo(info);

  } catch (error) {
    hideLoading();
    showError('Failed to fetch video info: ' + error.message);
  }
}

function showLoading() {
  previewSection.classList.add('show');
  loadingIndicator.style.display = 'block';
  previewContent.style.display = 'none';
}

function hideLoading() {
  loadingIndicator.style.display = 'none';
}

function displayVideoInfo(info) {
  hideLoading();

  previewTitle.textContent = info.title;
  previewThumbnail.src = info.thumbnail;

  // Display audio tracks if available
  if (info.audioTracks && info.audioTracks.length > 1) {
    const tracksList = info.audioTracks
      .map(track => `<div>🎵 ${track.language}</div>`)
      .join('');
    audioTracksInfo.innerHTML = `
      <div style="margin-top: 12px;">
        <strong>Available Audio Tracks:</strong>
        <div style="margin-top: 8px; font-size: 13px;">
          ${tracksList}
        </div>
      </div>
    `;
  } else {
    audioTracksInfo.innerHTML = '';
  }

  previewContent.style.display = 'block';
}

function showError(message) {
  errorMessage.textContent = message;
  errorMessage.classList.add('show');
}

function hideError() {
  errorMessage.classList.remove('show');
}

// Focus the textarea on load
urlInput.focus();
