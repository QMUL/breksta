# breksta
Data Acquisition for photomultiplier tubes to a Raspberry Pi via an ADC.

Uses (at the moment) Qt, (Pyside6) pandas, plotly/dash and SQLAlchemy.

Assuming Qt is installed:

* pip3 install -r requirements.txt
* python3 breksta.py

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