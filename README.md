## Introduction

Breksta is a specialized data acquisition system focusing on photomultiplier tubes. The application operates on a Raspberry Pi interfacing via an ADC. It integrates multiple technologies, including Qt (via PySide6), pandas for data manipulation, Plotly/Dash for visualization, and SQLAlchemy for database operations.

## Pre-requisites

- Python 3.8+
- Qt (PySide6)
- Linux-based OS

## Installation

### Setup

1. **Create a Virtual Environment**:
    ```bash
    python3 -m venv env
    ```

2. **Activate the Virtual Environment**:
    ```bash
    source env/bin/activate
    ```

3. **Install Required Packages**:
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the application:

1. Add the current directory to `PYTHONPATH`:
    ```bash
    export PYTHONPATH="$PWD:$PYTHONPATH"
    ```

2. Activate the virtual environment:
    ```bash
    source env/bin/activate
    ```

3. Start the application:
    ```bash
    python -m app.breksta
    ```

## Development

### Setting up Development Environment

1. **Activate the Virtual Environment**:
    ```bash
    source env/bin/activate
    ```

2. **Install Development Packages**:
    ```bash
    pip install -r requirements-dev.txt
    ```

### Selecting devices

To bypass ADC selection and use the Sine Wave generator, before starting the app use:
```sh
export USE_MOCK_DEVICE=1
```

### Contributing

For contributions, please open a Pull Request detailing the changes made, issues fixed, or features added.

### Code Quality

- **Linting**: We use `flake8`, `pylint`, and `mypy` to maintain code quality. Additionally, we've introduced `ruff` to the mix, which covers both linting and formatting. Built in Rust, `ruff` encompasses most of `flake8` and `pylint` functionality (and a bunch of others) but is still under development. The config file includes a lot of up-to-date rules.
  - Run them regularly to pick up issues early.
    ```bash
    flake8 app/*
    pylint app/*
    mypy app/
    ruff check [optional: file]  # to list linting warnings and errors
    ruff check --fix [optional: file]  # to fix them
    ```

- **Formatting**: Ruff handles formatting in a similar way that `black` does; it can be very opinionated but also customizable.
```bash
ruff format --help  # to see all available options
ruff format --diff [file]  # will print the proposed changes
ruff format [file]  # regular formatting operation
```

- **Testing**: `pytest` is used for running tests.
  - Run tests:
    ```bash
    pytest
    ```
  - **Coverage**:
    ```bash
    coverage run -m pytest  # to generate a coverage report
    coverage report -m  # to see the report
    ```

## License

The project is operating under an Open License.

## Contact

For questions or suggestions, please contact us at [email](mailto:example@example.com) or open an issue.


## Integration notes

- installed [ADS1x15-ADC library](https://github.com/chandrawi/ADS1x15-ADC)
- added `dtparam=i2c_arm=on` on `/boot/config.txt`
- created `/etc/modules-load.d/raspberrypi.conf` with:

```txt
i2c-dev
i2c-bcm2708
```

- install it directly to use modification in PR:
(modification removes lines 68-70 from `ADS1x15/ADS1x15.py`)

```txt
pip3 install setuptools wheel
python3 setup.py bdist_wheel
pip3 install dist/ADS1x15_ADC-1.2.1-py3-none-any.whl
```

WORKED:

```sh
python3
>> import ADS1x15
```

OH NO:

```sh
>> ads = ADS1x15.ADS1115(1)
PermissionError: Permission denied: '/dev/i2c-1'
```

[This](https://raspberrypi.stackexchange.com/questions/51375/how-to-allow-i2c-access-for-non-root-users) suggests the user has to be added to the i2c group
YES YES!

```sh
$ sudo usermod -a -G i2c matt  # where matt is the <username>
```

and:

```sh
sudo i2cdetect -F 1
Functionalities implemented by /dev/i2c-1:
I2C             YES
SMBus ...       YES
...             YES
```
