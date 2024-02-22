"""Tests all ui_utils helper functions."""
import unittest
from pathlib import Path
from unittest import mock

from app.ui_utils import choose_directory, default_db_path


class TestChooseDirectory(unittest.TestCase):
    """Tests choose_directory helper function"""

    def test_opens_dialog_window(self) -> None:
        """opens a dialog window to choose a directory path"""
        # Mock the QFileDialog.getExistingDirectory method
        with mock.patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory") as mock_get_directory:
            # Set the return value of the mock method
            mock_get_directory.return_value = "/path/to/directory"

            # Call the choose_directory function
            result = choose_directory()

            # Assert that the QFileDialog.getExistingDirectory method was called with the correct arguments
            mock_get_directory.assert_called_once_with(None, "Select Folder to export and backup", str(default_db_path))

            # Assert that the result is a Path object with the correct value
            self.assertIsInstance(result, Path)
            self.assertEqual(result, Path("/path/to/directory"))

    def test_returns_none_if_directory_path_is_empty(self) -> None:
        """Returns None if the chosen directory path is empty."""
        # Mock the QFileDialog.getExistingDirectory method
        with mock.patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory") as mock_get_directory:
            # Set the return value of the mock method to an empty string
            mock_get_directory.return_value = ""

            # Call the choose_directory function
            result = choose_directory()

            # Assert that the QFileDialog.getExistingDirectory method was called with the correct arguments
            mock_get_directory.assert_called_once_with(None, "Select Folder to export and backup", str(default_db_path))

            # Assert that the result is None
            self.assertIsNone(result)

    def test_specify_default_directory(self) -> None:
        """Allows specifying a different default directory path and dialog title"""
        default_path = Path("/path/to/default")
        dialog_title = "Select Folder"

        # Mock the QFileDialog.getExistingDirectory method
        with mock.patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory") as mock_get_directory:
            # Set the return value of the mock method
            mock_get_directory.return_value = "/path/to/chosen"

            # Call the choose_directory function with the specified default path and dialog title
            chosen_path = choose_directory(default_path, dialog_title)

            # Assert that the mock method was called with the correct arguments
            mock_get_directory.assert_called_once_with(None, dialog_title, str(default_path))

            # Assert that the chosen path is the expected path
            self.assertEqual(chosen_path, Path("/path/to/chosen"))

    def test_returns_none_if_user_cancels_dialog(self) -> None:
        """Returns None if the user cancels the dialog"""
        # Mock the QFileDialog.getExistingDirectory method to return an empty string
        with mock.patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory", return_value=""):
            # Call the choose_directory function
            result = choose_directory()

            # Check that the result is None
            self.assertIsNone(result)

    def test_dialog_window_closed_without_choosing_directory(self) -> None:
        """Returns None if the dialog window is closed without choosing a directory path."""
        # Mock the QFileDialog.getExistingDirectory method to return an empty string
        with mock.patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory", return_value=""):
            # Call the choose_directory function
            result = choose_directory()

            # Check that the result is None
            self.assertIsNone(result)
