"""Encapsulates all UI-related helper functionality."""

from pathlib import Path

from PySide6.QtWidgets import QFileDialog

from app.utils import get_db_path

default_db_path: Path = get_db_path()


def choose_directory(
    default_path: Path = default_db_path, dialog_title: str = "Select Folder to export and backup"
) -> Path | None:
    """
    Opens a dialog for the user to choose an export folder for the experiment data.
    Utilizes pathlib for path manipulation, setting the default directory to the user's home directory,
    but allows specifying a different default directory and dialog title.

    Args:
        default_path (Path): The default directory path when the dialog opens. Defaults to the user's home directory.
        dialog_title (str): The title of the dialog window. Defaults to "Select Folder".

    Returns:
        Path or None: The chosen directory path as a Path object, or None if the user cancels the dialog.
    """
    chosen_path = QFileDialog.getExistingDirectory(None, dialog_title, str(default_path))

    # Upon cancelling, QFileDialog will return an empty string
    if not chosen_path:
        return None

    return Path(chosen_path)
