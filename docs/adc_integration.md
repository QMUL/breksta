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

There is a [known bug][known-bug-issue] in the original `ADS1x15-ADC` library. A [pull request (PR #5)][pr-5] has been opened to fix this issue, but if it is not yet merged or released on PyPI, you can manually apply the patch.

### Option A: If PR #5 Is Merged and Released

If the PR has been merged and a new version published to PyPI, you can install it directly with `pip`:

```bash
# Activate your Breksta virtual environment
source .venv/bin/activate

# Then simply install from PyPI (assuming bug is fixed in a new version)
pip install ADS1x15-ADC --upgrade
```

> **Tip**: Check the [PyPI page](https://pypi.org/project/ADS1x15-ADC/) or the [repository][repo-url] to confirm the bug fix is included.

### Option B: If PR #5 Is Still Unmerged (Manual Patch)

1. **Activate** your Breksta virtual environment:
   ```bash
   source .venv/bin/activate
   ```

2. **Install build tools**:
   ```bash
   pip install --upgrade setuptools wheel
   ```

3. **Clone the library** (using HTTPS or SSH):
   ```bash
   git clone https://github.com/chandrawi/ADS1x15-ADC.git
   cd ADS1x15-ADC/
   ```

4. **Check out the PR branch** (if available) or **apply the fix manually**:
   - **Via Git** (if you can see the PR branch remotely):
     ```bash
     # Example: fetch and checkout the PR branch
     git fetch origin pull/5/head:fix-i2c-bug
     git checkout fix-i2c-bug
     ```
   - **Manually** remove lines 68–70 in `ADS1x15/ADS1x15.py` if you do not see the PR branch.

   ```python
    # I2C object from smbus library
    i2c = SMBus(1)
    ```

5. **Build and install** the wheel:
   ```bash
   python3 setup.py bdist_wheel
   # Adjust the version if it’s named differently
   pip install dist/ADS1x15_ADC-1.2.1-py3-none-any.whl
   ```

[known-bug-issue]: https://github.com/chandrawi/ADS1x15-ADC/issues/4
[pr-5]: https://github.com/chandrawi/ADS1x15-ADC/pull/5
[repo-url]: https://github.com/chandrawi/ADS1x15-ADC

6. **Confirm installation** by starting a Python session:

```python
python3
>>> import ADS1x15
>>> ads = ADS1x15.ADS1115(1)
```

If you see a permission error, see [section 4 in troubleshooting](./troubleshooting.md#4-i2c-permission-errors).
