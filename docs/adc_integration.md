# ADC Integration

This document outlines how to enable I2C on a Raspberry Pi, install the modified ADS1x15 library from source, and troubleshoot common permission issues.

## 1. Enable I2C on Raspberry Pi

1. Edit `/boot/config.txt` and ensure the following line is present (or un-commented):
   ```txt
   dtparam=i2c_arm=on
   ```
2. Create (or edit) `/etc/modules-load.d/raspberrypi.conf` to automatically load the required modules:
   ```txt
   i2c-dev
   i2c-bcm2708
   ```

After rebooting, I2C should be enabled. You can test via:
```bash
sudo i2cdetect -F 1
```
If you see a list of I2C functionalities (`YES` for I2C, SMBus, etc.), the interface is active.

## 2. Install the Modified ADS1x15 Library

> **Important**: Do **not** install `ADS1x15-ADC` directly from `pip`, as there is a known bug. Instead, clone the repository and build it manually.

1. **Activate** your Breksta virtual environment:
   ```bash
   source .venv/bin/activate
   ```
2. **Install build tools** (inside the Breksta environment):
   ```bash
   pip3 install setuptools wheel
   ```
3. **Clone the repository** (using either HTTPS or SSH):
   ```bash
   git clone git@github.com:chandrawi/ADS1x15-ADC.git
   cd ADS1x15-ADC/
   ```
4. **Apply the patch or branch** that removes lines 68–70 from `ADS1x15/ADS1x15.py`. If there is an open PR that does this automatically, switch to that branch; otherwise, remove those lines manually.
5. **Build and install** the wheel:
   ```bash
   python3 setup.py bdist_wheel
   pip3 install dist/ADS1x15_ADC-1.2.1-py3-none-any.whl
   ```
   *(Adjust version numbers as necessary if the build output changes.)*

Confirm installation by starting a Python session:
```py
python3
>>> import ADS1x15
>>> ads = ADS1x15.ADS1115(1)
# If you see a permission error, see Section 3 below.
```

## 3. Fixing Permission Errors

If you encounter:
```py
PermissionError: [Errno 13] Permission denied: '/dev/i2c-1'
```
it means the current user is not in the `i2c` group. To fix this:

```bash
sudo usermod -a -G i2c <your-username>
```

Log out and back in (or reboot) for the group change to take effect.

---
