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
- Start the application - Default (as a module): `python3 -m app.breksta`
- Start the application - alternatively: `python3 app/breksta.py`

## Contributing
Please send a pull request with any suggested changes or improvements. (placeholder)

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
