"""This module contains unit tests for the ExportControl class from the breksta module.

Each public method of ExportControl is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest
import tempfile
from unittest import mock
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication, QMessageBox
from app.breksta import ExportControl, TableWidget

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

    def setUp(self) -> None:
        # Create a mock logger
        self.mock_logger = MagicMock()

        # Mock the database to separate testing from actual database; also avoids side-effects.
        self.mock_db = MagicMock()

        # Create instances of classes with the mock database
        width = 1
        self.table = TableWidget(width, self.mock_db, self.mock_logger)
        self.export_control = ExportControl(self.table, self.mock_logger)

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
        """Test that delete_experiment is not called if the user declines deletion.

        This test emulates a scenario where the user is asked to confirm the
        deletion of an experiment. If the user declines (chooses "No"), then
        the experiment should not be deleted, and the `delete_experiment` method
        should not be called.
        """
        # Use a temporary directory to mock the chosen directory path.
        with tempfile.TemporaryDirectory() as tmpdirname:

            # Mock the directory choice to return the temporary directory.
            with mock.patch.object(self.export_control, 'choose_directory', return_value=tmpdirname):
                self.export_control.folder_path = tmpdirname

            # Simulate a user response of "No" via the QMessageBox.
            # This mock ensures that the user's decision to decline deletion
            # is captured and affects the behavior of the method under test.
            with mock.patch('PySide6.QtWidgets.QMessageBox.question', return_value=QMessageBox.No):

                # Create a mock item with a text method.
                # You can adjust this mock's return value to align with the specific
                # behavior you're testing.
                mock_item = MagicMock()
                mock_item.text.return_value = "False"  # Assuming the experiment is exported by default.

                # Mock the table's item method to return the mock item.
                with mock.patch.object(self.export_control.table, 'item', return_value=mock_item):

                    # Set the experiment and row to be "selected" in the test.
                    self.export_control.selected_experiment_id = 1
                    self.export_control.table.selected_row = 0

                    # Invoke the method under test.
                    self.export_control.on_delete_button_clicked()

                    # The main assertion for this test: ensure that delete_experiment was not invoked.
                    self.mock_db.delete_experiment.assert_not_called()

    def test_delete_experiment_when_declined_second_time(self) -> None:
        """Test that delete_experiment is not called if user declines deletion.

        This test simulates a scenario where the user is prompted to confirm
        the deletion of an experiment that has already been exported.
        The expected behavior is that a single affirmative response (Yes)
        will not result in the deletion of the experiment.
        """
        # Use a temporary directory to mock the chosen directory path.
        with tempfile.TemporaryDirectory() as tmpdirname:
            # Mock the directory choice to return the temporary directory.
            with mock.patch.object(self.export_control, 'choose_directory', return_value=tmpdirname):
                self.export_control.folder_path = tmpdirname

            # Simulate two user responses via the QMessageBox: first Yes, then No.
            # The order of these responses is crucial to the test, as the logic
            # of the method being tested depends on the exported status of the experiment.
            with mock.patch('PySide6.QtWidgets.QMessageBox.question', side_effect=[QMessageBox.Yes, QMessageBox.No]):

                # Create a mock item with a text method that always returns "True".
                # This ensures that the is_exported status will always be True,
                # which, in turn, affects the behavior of the method being tested.
                mock_item = MagicMock()
                mock_item.text.return_value = "False"

                # Mock the table's item method to return the mock item.
                with mock.patch.object(self.export_control.table, 'item', return_value=mock_item):

                    # Set the experiment and row to be "selected" in the test.
                    self.export_control.selected_experiment_id = 1
                    self.export_control.table.selected_row = 0

                    # Invoke the method under test.
                    self.export_control.on_delete_button_clicked()

                    # The core assertion of this test: ensure that delete_experiment was not called.
                    self.mock_db.delete_experiment.assert_not_called()
