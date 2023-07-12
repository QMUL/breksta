# breksta

## Introduction

Breksta is a data acquisition project for photomultiplier tubes. It uses a Raspberry Pi via an ADC and leverages technologies such as Qt (Pyside6), pandas, plotly/dash, and SQLAlchemy.

## Pre-requisites

- Python 3.8 or above
- Qt installed
- Linux OS (preferred)

## Installation and Setup

### First time setup:

- Create a virtual environment: `python3 -m venv env`
- Activate the virtual environment: `source env/bin/activate`
- Install the required packages: `pip3 install -r requirements.txt`

### Running the application

Each time you open a new terminal, you should:

- Add the current directory to the PYTHONPATH: `export PYTHONPATH="$PWD:$PYTHONPATH"`
- Activate the virtual environment: `source env/bin/activate`
- Start the application: `python3 -m app.breksta`

#### Usage

**Exporting experiments**: To export a specific experiment record, select it from the table and click on the "Export" button. You'll be prompted to choose a location where the exported data will be saved. The output file will be named in the format: `<experiment-name>-<datetime:YYYYMMDD_HHMM>.csv`. After the export operation is complete, the "Exported" status of the experiment will change to `True`.

**Deleting experiments**: You can delete a specific experiment record by selecting it and clicking on the "Delete" button. Please note, this operation is irreversible. If you attempt to delete an experiment that hasn't been exported, you'll be asked to confirm your decision twice.

**Database backup**: As a safety measure, the system will create a backup of the database whenever an experiment is deleted. The first time you delete an experiment, you'll be prompted to choose a location for the backup database. This backup file will be named `backup.db` and will automatically be used to restore data if an issue is detected during the deletion of an experiment. This provides an opportunity to manually revert an erroneous deletion once.

## Contributing

Please send a pull request with any suggested changes or improvements.

### Linting

This project uses `flake8` and `pylint` to maintain code quality and ensure adherence to Python best practices.

- `flake8`: It checks for style issues as well as some types of bugs, such as module level imports not at the top of the file, line length, unused imports etc. To install, `(env) :$ pip3 install flake8`.
- `pylint`: It is a Python static code analysis tool which checks for programming errors, helps enforcing a coding standard, sniffs for code smells and offers simple refactoring suggestions. To install, `(env) :$ pip3 install pylint`.

Before committing changes, it's recommended to run these tools to check for any potential issues. They can be run from the command line as follows:

- To run `flake8`, navigate to the project directory and run `flake8 app/*` (or substitute `*` with a file).
- To run `pylint`, navigate to the project directory and run `pylint app/*` (or substitute `*` with a file).

Both have been customized via configuration files (`.flake8` and `.pylintrc`). These configuration files are used to enable or disable certain rules, exclude files or directories, and other. Additionally, both can be added to VS Code by installing the extension `Python` and then changing the settings to enable them.

Remember that these tools are not infallible and some issues they report may be false positives or not applicable in your specific situation. They should be used as guides, not absolute authorities. Always use your best judgement when addressing the issues they report.

### Testing

This project uses `pytest` for running the test suite, which contains unit tests that ensure each individual part of the code performs as expected.

To run the tests, navigate to the project directory and run `pytest` from the command line:

```bash
(env) :$ pytest
```

This will automatically discover and run all tests in the tests directory. Test files are named in the format test_*.py and test methods within those files are named in the format test_*(). This naming convention is required for pytest to automatically discover tests.

When writing tests, you should aim to cover all lines of code and all branches (i.e., all paths through conditional statements). You can check the coverage of your tests by using a tool like `coverage.py`.

To run the tests with coverage, use:

```bash
(env) :$ coverage run -m pytest
```

And then to report the coverage:

```bash
(env) :$ coverage report -m
```

You should aim for as high test coverage as possible, but remember that 100% coverage doesn't guarantee that your code is free of bugs. It only guarantees that all lines of code were executed during testing. You should also aim to test a variety of scenarios and edge cases to ensure your code behaves as expected in a range of situations.

## License

This project is licensed under the MIT License. (placeholder)

## Contact

If you have any questions or suggestions, please contact us at [email] or open an issue on this project. (placeholder)

## Debugging

This warrants its own section - for now dump information here (in case).

Information here should be niche exceptions, etc, that are slightly out of scope of the code.

### `export_data_single`

Exception points to "Export failed due to <>" and still unintelligible?

```python
from sqlalchemy.exc import SQLAlchemyError
from pandas.errors import EmptyDataError
from pathvalidate import ValidationError
except (SQLAlchemyError, OSError, EmptyDataError, ValidationError) as e:
```

### `on_export_button_clicked`

`OSError` will catch `pmt.db` issues. For the db itself:

```python
from sqlalchemy.exc import SQLAlchemyError
except (sqlalchemy.exc.SQLAlchemyError, OSError) as e:
```

### `mark_exported`

If there are any issues with the session or committing changes to the database.

```python
from sqlalchemy.exc import SQLAlchemyError
except sqlalchemy.exc.SQLAlchemyError as e:
```
