## Troubleshooting & Advanced Setup

This section collects common issues and advanced usage tips, particularly on Arch-based or Raspberry Pi OS setups.

### 1. Environment Setup and Upgrading

Upgrading or Locking Packages:

Use `--upgrade` if new versions of the dependencies are needed.

```bash
pip install --upgrade setuptools wheel  # used to install the ADS1X15 library
```

To lock the dependencies, use `pip freeze > requirements-working.txt` to mark the versions of all dependencies. Using `requirements-working.txt` to reinstall packages will pull and install the exact same versions.

### 2. QtWebEngine & GPU Flags

If PySide6’s QtWebEngine components cause crashes or blank screens on certain platforms, you may need to disable GPU acceleration:

```bash
export QTWEBENGINE_CHROMIUM_FLAGS="--disable-gpu"
python3 -m app.breksta
```

Make sure `qt6-webengine` (and sometimes `qt6-webview`) is installed on Arch-based systems:
```bash
sudo pacman -S qt6-webengine qt6-webview
```

### 3. libtiff Conflicts

On some Arch-based systems, you might encounter version conflicts between `libtiff.so.5` and `libtiff.so.6`. If you see errors related to `libtiff` when running `app.breksta`, consider:

- Installing or updating `libtiff`:
    ```bash
    sudo pacman -S libtiff
    ```
- (Advanced users) Manually linking or renaming libraries if your system libraries are inconsistent. Example:
    ```bash
    sudo ln -sf /usr/lib/libtiff.so.6.0.2 /usr/lib/libtiff.so.5
    ```

Use this approach **only** if you know exactly why the link is missing or incorrect—mixing library versions can cause instability.

### 4. I2C Permission Errors

If you encounter:
```python
PermissionError: [Errno 13] Permission denied: '/dev/i2c-1'
```
You need to add your user to the `i2c` group:
```bash
sudo usermod -a -G i2c <your-username>
```
Then log out and back in (or reboot) for the change to take effect.

### 5. Run Commands and Testing

- **Starting the App**:
  ```bash
  python3 -m app.breksta
  ```
- **Mock Device** (if no ADC hardware):
  ```bash
  export USE_MOCK_DEVICE=1
  python3 -m app.breksta
  ```

### 6. Database & Logs

- **Local Database**: The app writes to `pmt.db` by default. You can explore it via:
  ```bash
  sqlite3 pmt.db
  ```
- **Realtime Logs**:
  ```bash
  tail -f file.log
  ```
  or
  ```bash
  watch tail -f file.log
  ```

### 7. Other Common Commands

- **Upgrade system** (Arch-based):
  ```bash
  sudo pacman -Syu --noconfirm
  ```
- **Check Python version**:
  ```bash
  python3 --version
  ```

Finally, feel free to open an Issue if you run into a problem not covered here!
