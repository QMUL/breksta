"""This module contains unit tests for the CentralizedControlManager class from the ui/central_controlpanel module.

Each public method of CentralizedControlManager is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication, QVBoxLayout, QGroupBox, QSpacerItem
from ui.central_controlpanel import CentralizedControlManager, get_manager_instance

# In Qt, every GUI application must have exactly one instance of QApplication or one of its subclasses.
# It's a requirement for managing a lot of application-wide resources, for initializing various Qt
# subsystems and for handling events.
# If it already exists (due to running another test), don't create one.
app = QApplication.instance()
if not app:
    app = QApplication([])


class TestCentralizedControlManager(unittest.TestCase):
    """Defines the test cases for the CentralizedControlManager class.
    """

    def setUp(self) -> None:
        self.mock_logger = MagicMock()
        self.central_manager: CentralizedControlManager = get_manager_instance(self.mock_logger)

    def test_initiate_data_capture_takes_reading(self) -> None:
        """Test that initiate_data_capture takes a reading."""
        # Replace start_reading with a mock
        with patch('ui.central_controlpanel.CentralizedControlManager.start_reading') as mock_start_reading:
            # Simulate a click on the start button
            self.central_manager.capture_ui.start_button.click()

            # Check that start_reading was called
            mock_start_reading.assert_called_once()

    def test_qtimer_has_started(self) -> None:
        """Test that the QTimer object has initialized and is running."""
        # Check the QTimer has not started yet
        self.assertFalse(self.central_manager.capture_manager.sampling_timer.isActive())

        # Simulate a click on the start button
        self.central_manager.capture_ui.start_button.click()

        # Check the QTimer has started
        self.assertTrue(self.central_manager.capture_manager.sampling_timer.isActive())

    def test_qtimer_has_stopped(self) -> None:
        """Test that the QTimer object has stopped running."""
        # Check the QTimer has started
        self.central_manager.capture_ui.start_button.click()
        self.assertTrue(self.central_manager.capture_manager.sampling_timer.isActive())

        # Simulate a click on the stop button
        self.central_manager.capture_ui.stop_button.click()

        # Check the QTimer has stopped
        self.assertFalse(self.central_manager.capture_manager.sampling_timer.isActive())

    def test_layout_is_vboxlayout(self) -> None:
        """Test that the layout is a QVBoxLayout."""
        layout = self.central_manager.layout()
        self.assertIsInstance(layout, QVBoxLayout)

    def test_layout_item_count(self) -> None:
        """Test the count of items in the layout."""
        layout = self.central_manager.layout()
        expected_widget_count = 3
        actual_widget_count = layout.count()
        self.assertEqual(actual_widget_count, expected_widget_count)

    def test_layout_items(self) -> None:
        """Test the types of items in the layout."""
        layout = self.central_manager.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item.widget(), QGroupBox):
                continue  # GroupBox found, continue with the next item
            elif isinstance(item, QSpacerItem):
                continue  # SpacerItem found, continue with the next item
            else:
                self.fail(f"Unexpected item type at position {i}: {type(item).__name__}")
