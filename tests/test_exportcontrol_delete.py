"""
This module contains unit tests for the ExportControl class from the breksta module.

Each public method of ExportControl is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest
import tempfile
from unittest import mock
from unittest.mock import MagicMock

from PySide6.QtWidgets import QApplication, QMessageBox
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

    def test_delete_button_no_experiment_selected(self) -> None:
        """Test that delete button does not call delete_experiment when no experiment is selected"""
        # Create a mock for the delete_experiment method
        self.mock_db.delete_experiment = MagicMock()

        # Try to delete without selecting an experiment
        self.export_control.selected_experiment_id = None
        self.export_control.on_delete_button_clicked()

        # Check that delete_experiment was not called
        self.mock_db.delete_experiment.assert_not_called()

    def test_delete_button_experiment_selected(self) -> None:
        """Test that delete button calls delete_experiment with correct id when an experiment is selected"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Mock the choose_directory method to return the temporary directory path
            with mock.patch.object(self.export_control, 'choose_directory', return_value=tmpdirname):
                self.export_control.folder_path = tmpdirname
                print(self.export_control.folder_path)
                # Create a mock for the delete_experiment method
                self.mock_db.delete_experiment = MagicMock()

                # Mock the return value of the table item's text method
                mock_item = MagicMock()
                mock_item.text.return_value = 'True'
                self.export_control.table.item = MagicMock(return_value=mock_item)

                # Mock the QMessageBox.question method to return 'Yes'
                with mock.patch('PySide6.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):
                    # Select an experiment and try to delete it
                    self.export_control.selected_experiment_id = 1
                    self.export_control.table.selected_row = 0
                    self.export_control.on_delete_button_clicked()

                    # Check that delete_experiment was called with the correct id
                    self.mock_db.delete_experiment.assert_called_with(1)

    def test_delete_button_experiment_not_exported(self) -> None:
        """Test that delete button calls delete_experiment with correct id when an experiment is not exported"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Mock the choose_directory method to return the temporary directory path
            with mock.patch.object(self.export_control, 'choose_directory', return_value=tmpdirname):
                self.export_control.folder_path = tmpdirname
                # Create a mock for the delete_experiment method
                self.mock_db.delete_experiment = MagicMock()

                # Mock the return value of the table item's text method
                mock_item = MagicMock()
                # This time we're simulating the case when the experiment is not exported
                mock_item.text.return_value = 'False'
                self.export_control.table.item = MagicMock(return_value=mock_item)

                # Mock the QMessageBox.question method to return 'Yes'
                with mock.patch('PySide6.QtWidgets.QMessageBox.question', return_value=QMessageBox.Yes):

                    # Select an experiment and try to delete it
                    self.export_control.selected_experiment_id = 1
                    self.export_control.table.selected_row = 0
                    self.export_control.on_delete_button_clicked()

                    # Check that delete_experiment was called with the correct id
                    self.mock_db.delete_experiment.assert_called_with(1)

    def test_delete_experiment_when_declined(self) -> None:
        """Test that delete_experiment is not called if user declines deletion"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Mock the choose_directory method to return the temporary directory path
            with mock.patch.object(self.export_control, 'choose_directory', return_value=tmpdirname):
                self.export_control.folder_path = tmpdirname
            # Mock the QMessageBox.question method to return QMessageBox.No
                with mock.patch('PySide6.QtWidgets.QMessageBox.question', return_value=QMessageBox.No):
                    # Select an experiment and try to delete it
                    self.export_control.selected_experiment_id = 1
                    self.export_control.table.selected_row = 0
                    self.export_control.on_delete_button_clicked()
                    # Assert that delete_experiment was not called
                    self.mock_db.delete_experiment.assert_not_called()

    def test_delete_experiment_when_declined_second_time(self) -> None:
        """Test that delete_experiment is not called if user declines deletion"""
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Mock the choose_directory method to return the temporary directory path
            with mock.patch.object(self.export_control, 'choose_directory', return_value=tmpdirname):
                self.export_control.folder_path = tmpdirname
            # Mock the QMessageBox.question method to return QMessageBox.No
                with mock.patch('PySide6.QtWidgets.QMessageBox.question', side_effect=[QMessageBox.Yes, QMessageBox.No]):
                    # Select an experiment and try to delete it
                    self.export_control.selected_experiment_id = 1
                    self.export_control.table.selected_row = 0
                    self.export_control.on_delete_button_clicked()
                    # Assert that delete_experiment was not called
                    self.mock_db.delete_experiment.assert_not_called()
