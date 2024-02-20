## ADC Integration notes

- installed [ADS1x15-ADC library](https://github.com/chandrawi/ADS1x15-ADC) - DO NOT INSTALL through `pip` as it has a bug. Rather clone the project and follow next set of notes.
- added `dtparam=i2c_arm=on` on `/boot/config.txt`
- created `/etc/modules-load.d/raspberrypi.conf` with:

```txt
i2c-dev
i2c-bcm2708
```

- install it directly to use modification in PR:
(modification removes lines 68-70 from `ADS1x15/ADS1x15.py`)

```sh
# Activate the breksta environment as usual
pip3 install setuptools wheel  # this should go into breksta
git clone git@github.com:chandrawi/ADS1x15-ADC.git
cd ADS1x15-ADC/
# make modification, either using the available branch or manually
python3 setup.py bdist_wheel
pip3 install dist/ADS1x15_ADC-1.2.1-py3-none-any.whl
# pip3.12 install dist/ADS1x15_ADC-1.2.2-py3-none-any.whl  # recompiling may update the version
```

```sh
python3
>> import ADS1x15  # Worked!
>> ads = ADS1x15.ADS1115(1)  # OH NO!
PermissionError: Permission denied: '/dev/i2c-1'
```

[This](https://raspberrypi.stackexchange.com/questions/51375/how-to-allow-i2c-access-for-non-root-users) suggests the user has to be added to the i2c group
YES YES!

```sh
$ sudo usermod -a -G i2c matt  # where matt is the <username>
```

and:

```sh
# requires installation of i2cdetect
sudo i2cdetect -F 1
Functionalities implemented by /dev/i2c-1:
I2C             YES
SMBus ...       YES
...             YES
```
