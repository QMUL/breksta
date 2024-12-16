[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

<img src="./assets/breksta.png" style="align:center; width:256px" />

## Introduction

***Breksta*** is a specialized data acquisition system focusing on photomultiplier tubes. The application operates on a Raspberry Pi interfacing via an ADC. It integrates multiple technologies, including Qt (via `PySide6`), `pandas` for data manipulation, `Plotly`/`Dash` for visualization, and `SQLAlchemy` for database operations.

- [Introduction](#introduction)
- [Pre-requisites](#pre-requisites)
- [Installation](#installation)
- [Development](#development)
- [License](#license)
- [Contact](#contact)
- [Appendix](#appendix)

## Pre-requisites

- Linux-based OS
- Python `3.10` minimum, tested on `3.11`, `3.12`
- Qt C++ libraries, pre-requisite for `PySide6`
- `uv` - How to [install](#installing-uv) and [use](#using-uv) `uv`.

## Installation

### Setup

1. **Create a Virtual Environment**:

```bash
uv venv
```

2. **Activate the Virtual Environment**:

```bash
source .venv/bin/activate
```

3. **Install Required Packages**:

```bash
uv pip install -r pyproject.toml
```

### Running the Application

To run the application:

1. Add the current directory to `PYTHONPATH`:

```bash
export PYTHONPATH="$PWD:$PYTHONPATH"
```

2. Activate the virtual environment

3. Start the application:

```bash
python -m app.breksta
```

## Development

### Setting up Development Environment

1. **Activate the Virtual Environment**
2. **Install Development Packages**:

```bash
uv pip install -r requirements-dev.txt
```

### Selecting mock device for development

To bypass ADC selection and use the Sine Wave generator, before starting the app use:

```sh
export USE_MOCK_DEVICE=1
```

### Contributing

For contributions, please open a Pull Request detailing the changes made, issues fixed, or features added.

### Code Quality

#### **Linting**

We use `flake8`, `pylint`, and `mypy` to maintain code quality. Additionally, we've introduced `ruff` to the mix, which covers both linting and formatting. Built in Rust, `ruff` encompasses most of `flake8` and `pylint` functionality (and a bunch of others) but is still under development. The config file includes a lot of up-to-date rules.

```bash
# To check all Python files
flake8 **/*.py
pylint **/*.py
mypy **/*.py
ruff check [optional: file]  # to list linting warnings and errors
ruff check --fix [optional: file]  # to fix them automatically
```

#### **Formatting**

`ruff` handles formatting in a similar way that `black` does; it can be very opinionated but also customizable.

```bash
ruff format --help  # to see all available options
ruff format --diff [file]  # will print the proposed changes
ruff format [file]  # regular formatting operation
```

#### **Testing and Coverage**

`pytest` is used for running tests, and `coverage` generates a coverage report using `pytest`.

```bash
pytest  # will run the whole suite of tests
coverage run -m pytest  # to generate a coverage report
coverage report -m  # to see the report
```

#### **pre-commit checks**

`pre-commit` is a tool that installs hooks on git's functionality. When that functionality is called to run, the hooks are ran first. This enables testing, linting, and formatting to automatically run consistently every time that git functionality is called.

To install (or uninstall) the hooks, activate the environment and run:

```sh
$ pre-commit install  # uninstall
pre-commit installed at .git/hooks/pre-commit
pre-commit installed at .git/hooks/pre-push
```

To temporarily skip over a hook; if you're fixing the issue in a later commit, for example a failed test, use:

```sh
SKIP pytest-check git commit -m "Commit message.."
```

## License

The project operates under an [Apache v2.0](./LICENSE) license.

## Contact

For questions or suggestions, please contact us at [email](m.alexandrakis@qmul.ac.uk) or open an issue.

## Appendix

### ADC Integration

The notes can be found [here](./docs/adc_integration.md).

### Installing `uv`

From your terminal, execute: `$ curl -LsSf https://astral.sh/uv/install.sh | sh`

Note: It's recommended to review scripts from the internet before executing them. You can view the script at `https://astral.sh/uv/install.sh` before running the above command.

Then restart terminal. To update it, simply invoke `uv self update`.

### Using `uv`

```bash
# Create a virtual environment
uv venv
source .venv/bin/activate  # to activate

# Install dependencies
uv pip install -r pyproject.toml  # runtime
uv pip install -r requirements-dev.txt  # development
```
