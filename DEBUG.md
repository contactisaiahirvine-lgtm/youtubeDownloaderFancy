# Debugging Guide for YouTube Downloader Fancy

This guide will help you debug issues with the YouTube Downloader application.

## Quick Start Debugging

### 1. Run in Development Mode

Always run in dev mode to see console output:

```bash
npm run dev
```

This will:
- Open DevTools automatically
- Show all console logs
- Display Python errors
- Show network issues

### 2. Check Console Logs

All components now have detailed logging with prefixes:

- `[Main Process]` - Electron main process logs
- `[Main]` - Main window renderer logs
- `[Add URL]` - Add URL modal logs
- `[Python]` - Python bridge script logs

## Common Issues and Solutions

### Issue 1: "Add URL" Button Not Responding

**Symptoms:**
- Clicking "Add URL" does nothing
- No modal window appears

**Debug Steps:**
1. Open DevTools (automatically opens in dev mode)
2. Check for JavaScript errors in Console
3. Look for logs starting with `[Main Process] open-add-url`

**Common Causes:**
- JavaScript error in main.js
- Modal window failed to create

**Solution:**
```bash
# Check if there are any syntax errors
node -c main.js
```

---

### Issue 2: Video Info Not Loading

**Symptoms:**
- "Get Info" button shows loading forever
- Error message appears
- Thumbnail doesn't load

**Debug Steps:**

1. **Check Python is installed:**
   ```bash
   python3 --version
   # Should show Python 3.7+
   ```

2. **Test Python bridge directly:**
   ```bash
   python3 youtubeDownloader/electron_bridge.py get-info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
   ```

   Expected output (JSON):
   ```json
   {"success": true, "title": "...", "thumbnail": "...", ...}
   ```

3. **Check Python dependencies:**
   ```bash
   pip3 list | grep yt-dlp
   # Should show yt-dlp version
   ```

4. **Check DevTools Console:**
   - Look for `[Add URL] Fetching video info for:`
   - Look for `[Main Process] Getting video info for:`
   - Check for error messages

**Common Causes:**
- Python not installed or not in PATH
- yt-dlp not installed (`pip3 install yt-dlp`)
- Network issues/firewall blocking YouTube
- Invalid YouTube URL

**Solution:**
```bash
# Reinstall Python dependencies
cd youtubeDownloader
pip3 install -r requirements.txt --upgrade
```

---

### Issue 3: Thumbnails Not Showing

**Symptoms:**
- Gray placeholder instead of thumbnail
- "Failed to load thumbnail" in console

**Debug Steps:**

1. **Check Console for errors:**
   - Look for `Failed to load thumbnail:` messages
   - Check if thumbnail URL is present

2. **Test thumbnail URL directly:**
   - Copy thumbnail URL from console
   - Paste into browser
   - See if it loads

3. **Check webSecurity setting:**
   - In `main.js`, verify `webSecurity: false` is set for both windows

**Common Causes:**
- CORS/security restrictions
- Invalid thumbnail URL
- Network issues

**Solution:**
- Thumbnails have automatic fallback to gray placeholder
- Check if `info.thumbnail` is populated in console logs

---

### Issue 4: Downloads Not Starting

**Symptoms:**
- Progress bar stuck at 0%
- Status shows "queued" forever
- Error appears immediately

**Debug Steps:**

1. **Check Console Logs:**
   ```
   [Main] startDownload called for: [ID]
   [Main] Invoking start-download with options: {...}
   [Main Process] Starting download with options: {...}
   [Main Process] Python download process spawned with PID: ...
   ```

2. **Check Python Bridge:**
   ```bash
   # Test download command manually (replace with your options)
   python3 youtubeDownloader/electron_bridge.py download '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","outputFolder":"/tmp","format":"mp4","quality":"best","audioOnly":false}'
   ```

3. **Check FFmpeg:**
   ```bash
   ffmpeg -version
   # Should display FFmpeg version
   ```

4. **Check output folder permissions:**
   ```bash
   # Make sure you can write to the output folder
   ls -la ~/Downloads/YouTube
   ```

**Common Causes:**
- FFmpeg not installed
- No write permission to output folder
- Python process crashes
- Network issues

**Solutions:**
```bash
# Install FFmpeg (Ubuntu/Debian)
sudo apt install ffmpeg

# Install FFmpeg (macOS)
brew install ffmpeg

# Create output directory
mkdir -p ~/Downloads/YouTube
chmod 755 ~/Downloads/YouTube
```

---

### Issue 5: Progress Not Updating

**Symptoms:**
- Progress bar doesn't move
- No speed/ETA shown

**Debug Steps:**

1. **Check Console for progress messages:**
   ```
   [Main] Download progress: {id: "...", progress: 45, speed: "2.1 MB/s", eta: "30s"}
   ```

2. **Check Python output:**
   - Look for `[Main Process] Python stdout:` messages
   - Should see JSON progress updates

3. **Check IPC communication:**
   - Verify `download-progress` events are being sent
   - Check renderer is receiving them

**Common Causes:**
- Python not sending progress updates
- JSON parsing errors
- IPC communication failure

---

### Issue 6: Scroll Not Working in Add URL Modal

**Symptoms:**
- Can't see "Add to Downloads" button after getting info
- Content cut off at bottom

**Debug Steps:**

1. **Check window height:**
   - Modal should be 600px height
   - Should be resizable

2. **Check CSS:**
   - `.modal-body` should have `overflow-y: auto`
   - Body should be flexbox

**Solution:**
- Window is now resizable - drag to make it taller
- Or scroll within the modal body section

---

## Advanced Debugging

### Enable Verbose Python Logging

Edit `youtubeDownloader/electron_bridge.py` and change:

```python
ydl_opts = {
    'quiet': True,          # Change to False
    'no_warnings': True,    # Change to False
    ...
}
```

### Check Python Process Status

```bash
# While download is running, check processes
ps aux | grep electron_bridge.py

# Check if Python can access the internet
curl -I https://www.youtube.com
```

### Inspect JSON Communication

All communication between Electron and Python is via JSON. Check logs for:

```
[Main Process] Python stdout: {"type":"progress","progress":50,...}
```

### Check File Permissions

```bash
# Check if electron_bridge.py is executable
ls -la youtubeDownloader/electron_bridge.py

# Should show -rwxr-xr-x or similar
```

---

## Logging Reference

### Console Log Prefixes

| Prefix | Location | Purpose |
|--------|----------|---------|
| `[Main Process]` | main.js | Electron main process |
| `[Main]` | renderer.js | Main window renderer |
| `[Add URL]` | add-url-renderer.js | Add URL modal |

### What Each Log Means

**Getting Video Info:**
```
[Add URL] Fetching video info for: [URL]
[Main Process] Getting video info for: [URL]
[Main Process] Bridge path: [PATH]
[Main Process] Python process spawned with PID: [PID]
[Main Process] Python stdout: [OUTPUT]
[Main Process] Video info retrieved successfully: [TITLE]
[Add URL] Received video info: [INFO OBJECT]
```

**Starting Download:**
```
[Main] URL added: {url: "...", videoInfo: {...}}
[Main] Adding download: [URL DATA]
[Main] Created download object: [DOWNLOAD]
[Main] Starting download for ID: [ID]
[Main] Invoking start-download with options: [OPTIONS]
[Main Process] Starting download with options: [OPTIONS]
[Main Process] Bridge options: [BRIDGE OPTIONS]
[Main Process] Python download process spawned with PID: [PID]
```

**During Download:**
```
[Main Process] Python stdout: {"type":"progress","progress":45,...}
[Main] Download progress: {id: "...", progress: 45, ...}
```

**On Completion:**
```
[Main Process] Python stdout: {"type":"complete","filename":"..."}
[Main] Download complete: {id: "...", filename: "..."}
```

**On Error:**
```
[Main Process] Python stderr: [ERROR MESSAGE]
[Main] Download error: {id: "...", error: "..."}
```

---

## Network Issues

### Proxy/Firewall

If you're behind a proxy or firewall:

1. **Set proxy for yt-dlp:**
   ```bash
   export HTTP_PROXY=http://proxy:port
   export HTTPS_PROXY=http://proxy:port
   ```

2. **Test connection:**
   ```bash
   curl -I https://www.youtube.com
   ```

### VPN Issues

Some VPNs may block YouTube access:
- Try disabling VPN temporarily
- Check VPN settings for YouTube access

---

## Getting Help

When reporting issues, please include:

1. **Console logs from DevTools**
   - Open DevTools (npm run dev)
   - Copy all console output
   - Include errors in red

2. **Python test output**
   ```bash
   python3 youtubeDownloader/electron_bridge.py get-info "[YOUR URL]"
   ```

3. **System info**
   ```bash
   node --version
   python3 --version
   ffmpeg -version
   npm --version
   ```

4. **Operating System**
   - Windows version / macOS version / Linux distro

5. **Exact steps to reproduce**
   - What you clicked
   - What URL you used
   - What settings you chose

---

## Quick Fixes Checklist

- [ ] Python 3.7+ installed: `python3 --version`
- [ ] yt-dlp installed: `pip3 list | grep yt-dlp`
- [ ] FFmpeg installed: `ffmpeg -version`
- [ ] Node.js installed: `node --version`
- [ ] Dependencies installed: `npm install`
- [ ] Running in dev mode: `npm run dev`
- [ ] Internet connection working
- [ ] Output folder exists and is writable
- [ ] DevTools open to see errors

---

## Still Having Issues?

If you've tried everything above:

1. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules
   npm install
   ```

2. Reinstall Python dependencies:
   ```bash
   pip3 install -r youtubeDownloader/requirements.txt --upgrade
   ```

3. Try with a different YouTube URL

4. Check GitHub issues for similar problems

5. Create a new issue with all debugging info above
