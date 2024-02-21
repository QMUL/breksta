"""This module houses the more general functionality."""
from pathlib import Path

import appdirs


def get_db_path(db_filename: str = "pmt.db", subdirectory: str = "") -> Path:
    """
    Gets the path to the specified database file within the application-specific data directory.

    Args:
        db_filename (str): The name of the database file. Defaults to 'pmt.db'.
        subdirectory (str): An optional subdirectory within the application data directory.

    Returns:
        Path: The path object for the database file.
    """
    # Determine the appropriate user-specific application data directory
    app_dir = Path(appdirs.user_data_dir("Breksta"))
    db_path = app_dir / subdirectory / db_filename
    # Ensure the target directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return db_path
