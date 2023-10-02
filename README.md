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

### Contributing

For contributions, please open a Pull Request detailing the changes made, issues fixed, or features added.

### Code Quality

- **Linting**: We use `flake8`, `pylint`, and `mypy` to maintain code quality.
  - Run them regularly to pick up issues early.
    ```bash
    flake8 app/*
    pylint app/*
    mypy app/
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
