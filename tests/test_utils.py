"""Tests for general functionality utilities."""

import tempfile
import unittest
from pathlib import Path

import appdirs

from app.utils import get_db_path


class TestGetDbPath(unittest.TestCase):
    """Test get_db_path function."""

    def setUp(self) -> None:
        self.db_filename = "test.db"
        self.db_default_name = "pmt.db"

    def test_default_db_path(self) -> None:
        """Returns a Path object for the default database file name 'pmt.db' in the application-specific data directory."""
        # Call the get_db_path function
        result = get_db_path()

        # Assert that the result is a Path object
        self.assertIsInstance(result, Path)

        # Assert that the result has the correct file name and parent directory
        self.assertEqual(result.name, self.db_default_name)
        self.assertEqual(result.parent, Path(appdirs.user_data_dir("Breksta")))

    def test_custom_db_path(self) -> None:
        """Returns a Path object for a specified database file name in a non-existent subdirectory of the
        application-specific data directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Call the get_db_path function with a custom database file name and subdirectory
            result = get_db_path(db_filename=self.db_filename, subdirectory=temp_dir)

            # Assert that the result is a Path object
            self.assertIsInstance(result, Path)

            # Assert that the result has the correct file name and parent directory
            self.assertEqual(result.name, self.db_filename)
            self.assertEqual(result.parent, Path(appdirs.user_data_dir("Breksta")) / temp_dir)

    def test_returns_path_object(self) -> None:
        """Returns a Path object for a specified database file name in the application-specific data directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Call the get_db_path function
            result = get_db_path(self.db_filename, temp_dir)

            # Assert that the result is a Path object
            self.assertIsInstance(result, Path)

            # Assert that the result path is correct
            expected_path = Path(temp_dir) / self.db_filename
            self.assertEqual(result, expected_path)

    def test_get_db_path(self) -> None:
        """Returns a Path object for a specified database file name in a specified subdirectory of the
        application-specific data directory."""
        # Set up
        with tempfile.TemporaryDirectory() as temp_dir:
            expected_path = Path(temp_dir) / self.db_filename

            # Call the function
            result = get_db_path(self.db_filename, temp_dir)

            # Assert that the result is a Path object
            self.assertIsInstance(result, Path)

            # Assert that the result is equal to the expected path
            self.assertEqual(result, expected_path)

    def test_creates_target_directory(self) -> None:
        """Creates the target directory if it does not exist and returns a Path object for the
        specified database file name in the application-specific data directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Call the get_db_path function
            result = get_db_path(subdirectory=temp_dir)

            # Assert that the result is a Path object with the correct value
            self.assertIsInstance(result, Path)
            self.assertEqual(result, Path(temp_dir) / self.db_default_name)

            # Assert that the target directory was created
            self.assertTrue(result.parent.exists())
