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


        # Create a mock logger
        self.mock_logger = MagicMock()
        # Mock the logger within ExportControl module
        self.logger_patch = patch("app.breksta.setup_logger", return_value=self.mock_logger)
        self.logger_patch.start()

        # Create instances of classes with the mock database
        self.mock_db = MagicMock()

        width = 1
        self.table = TableWidget(width, self.mock_db)
        self.export_control = ExportControl(self.table)

    def tearDown(self) -> None:
        width = 1
        self.table = TableWidget(width, self.mock_db)
        self.export_control = ExportControl(self.table)
        self.logger_patch.stop()

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

    def test_on_export_experiment_not_selected(self) -> None:
        """Test that clicking the export button when an experiment has not been selected
        asserts that a warning is logged about choosing an experiment, and ensures no further
        methods are called/control returns."""
        self.export_control.selected_experiment_id = None

        self.export_control.on_export_button_clicked()

        self.mock_logger.warning.assert_called_once_with("To export, please choose an experiment from the list")

    @patch.object(ExportControl, "choose_directory", return_value="/mock/directory")
    def test_successful_export_on_export_button_clicked(self, mock_choose_directory) -> None:
        """Test that clicking the export button successfully exports the data."""
        self.export_control.selected_experiment_id = 123  # mock ID
        self.export_control.folder_path = "/mock/directory"

        # Mock the instance's method
        self.export_control.table.database.export_data_single = MagicMock()

        self.export_control.on_export_button_clicked()

        self.export_control.table.database.export_data_single.assert_called_once_with(123, "/mock/directory")

    @patch.object(ExportControl, "choose_directory", return_value="/mock/directory")
    def test_failed_export_on_export_button_clicked(self, mock_choose_directory) -> None:
        """Test that clicking the export button raises an OSError and is logged as a critical error."""
        self.export_control.selected_experiment_id = 123  # mock ID
        self.export_control.folder_path = "/mock/directory"

        mock_export_data_single = MagicMock(side_effect=OSError("mock error"))
        self.export_control.table.database.export_data_single = mock_export_data_single

        self.export_control.on_export_button_clicked()
        mock_export_data_single.assert_called_once()

        # look for our expected message in all calls to the logger
        calls_to_critical = self.mock_logger.critical.call_args_list
        formatted_errors = [call_args[0][0] % call_args[0][1] for call_args in calls_to_critical if len(call_args[0]) == 2]

        # Now, we just check if our expected message appears in any of the formatted messages
        expected_message = "Export button failed due to: %s" % "mock error"
        self.assertIn(expected_message, formatted_errors)
