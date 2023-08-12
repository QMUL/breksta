"""
This module contains unit tests for the ExportControl class from the breksta module. Specifically, general methods

Each public method of ExportControl is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication
from app.breksta import ExportControl, TableWidget
from app.logger_config import setup_logger

# In Qt, every GUI application must have exactly one instance of QApplication or one of its subclasses.
# It's a requirement for managing a lot of application-wide resources, for initializing various Qt
# subsystems and for handling events.
# If it already exists (due to running another test), don't create one.
app = QApplication.instance()
if not app:
    app = QApplication([])


class TestExportControl(unittest.TestCase):
    """Defines the test cases for the ExportControl class.

    The setUp method is called before executing each test method.

    The tearDown method is called after each test method.
    """

    def setUp(self):
        self.logger = setup_logger()
        self.logger.info('=' * 50)
        self.logger.info('TESTS STARTED')

        # Create instances of classes with the mock database
        self.mock_db = MagicMock()

        width = 1
        self.table = TableWidget(width, self.mock_db)
        self.export_control = ExportControl(self.table)

    def tearDown(self):
        self.export_control = ExportControl(self.table)

        self.logger.info('TESTS FINISHED')
        self.logger.info('=' * 50)
        return super().tearDown()

    @patch.object(ExportControl, "choose_directory", return_value=None)
    def test_choose_directory_no_folder_chosen(self, mock_choose_directory) -> None:
        """Test that cancelling the file dialog and not choosing a folder returns
        control to parent; does not export."""
        self.export_control.selected_experiment_id = 1
        self.export_control.folder_path = None

        self.export_control.on_export_button_clicked()

        mock_choose_directory.assert_called_once()
        self.assertTrue(self.export_control.export_button.isEnabled())

    @patch("PySide6.QtWidgets.QFileDialog.getExistingDirectory")
    def test_choose_directory_folder_chosen(self, mock_getExistingDirectory) -> None:
        """Test that choosing an export folder returns a valid filepath."""

        # Mock the QFileDialog's getExistingDirectory method to return a fake directory path.
        mock_path = "/fake/directory/path"
        mock_getExistingDirectory.return_value = mock_path

        # Act
        result = self.export_control.choose_directory()

        # Assert
        mock_getExistingDirectory.assert_called_once()
        self.assertEqual(result, mock_path)


    @patch.object(ExportControl, "choose_directory")
    def test_filepath_set_on_export_button_click(self, mock_choose_directory) -> None:
        """Test that on_export_button_click assigns a valid filepath to folder_path"""

        # Set folder_path to None and experiment id to not None,
        # and mock choose_directory to return a fake path.
        self.export_control.folder_path = None
        self.export_control.selected_experiment_id = 1

        mock_path = "/another/fake/directory/path"
        mock_choose_directory.return_value = mock_path

        self.export_control.on_export_button_clicked()

        mock_choose_directory.assert_called_once()
        self.assertEqual(self.export_control.folder_path, mock_path)

    def test_update_selected_experiment(self) -> None:
        """Test that the selected_experiment_id attribute is updated correctly."""

        # Setup
        experiment_id = 1234  # Sample ID

        # Act
        self.export_control.update_selected_experiment(experiment_id)

        # Assert
        self.assertEqual(self.export_control.selected_experiment_id, experiment_id)
