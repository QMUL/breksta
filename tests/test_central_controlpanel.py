"""This module contains unit tests for the CentralizedControlManager class from the ui/central_controlpanel module.

Each public method of CentralizedControlManager is tested to ensure that changes in the code do not unintentionally
break the application.
"""

import os
from unittest import TestCase
from unittest.mock import MagicMock, patch

from PySide6.QtWidgets import QApplication, QGroupBox, QSpacerItem, QVBoxLayout

from ui.central_controlpanel import CentralizedControlManager, get_manager_instance

# In Qt, every GUI application must have exactly one instance of QApplication or one of its subclasses.
# It's a requirement for managing a lot of application-wide resources, for initializing various Qt
# subsystems and for handling events.
# If it already exists (due to running another test), don't create one.
app = QApplication.instance()
if not app:
    app = QApplication([])

os.environ["USE_MOCK_DEVICE"] = "1"


class TestCentralizedControlManager(TestCase):
    """Defines the test cases for the CentralizedControlManager class."""

    def setUp(self) -> None:
        self.mock_logger = MagicMock()
        self.central_manager: CentralizedControlManager = get_manager_instance(self.mock_logger)

    def test_initiate_data_capture_takes_reading(self) -> None:
        """Test that initiate_data_capture takes a reading."""
        # Replace start_reading with a mock
        with patch("ui.central_controlpanel.CentralizedControlManager.start_reading") as mock_start_reading:
            # Simulate a click on the start button
            self.central_manager.on_experiment_started()

            # Check that start_reading was called
            mock_start_reading.assert_called_once()

    def test_qtimer_has_started(self) -> None:
        """Test that the QTimer object has initialized and is running."""
        # Check the QTimer has not started yet
        self.assertFalse(self.central_manager.timer.isActive())

        # Simulate a click on the start button
        self.central_manager.on_experiment_started()

        # Check the QTimer has started
        self.assertTrue(self.central_manager.timer.isActive())

    def test_qtimer_has_stopped(self) -> None:
        """Test that the QTimer object has stopped running."""
        # Check the QTimer has started
        self.central_manager.on_experiment_started()
        self.assertTrue(self.central_manager.timer.isActive())

        # Simulate a click on the stop button
        self.central_manager.on_experiment_stopped()

        # Check the QTimer has stopped
        self.assertFalse(self.central_manager.timer.isActive())

    def test_qtimer_slot_emits_result(self) -> None:
        """Test that the timer slot emits the result upon starting."""
        received_data: list[float] = []

        def test_slot(data) -> None:
            received_data.append(data)

        self.central_manager.output_signal.connect(test_slot)

        self.central_manager.output_signal.emit(1.5)
        self.assertEqual(received_data[0], 1.5)

    def test_start_experiment_successfully(self) -> None:
        """starts experiment successfully, disables ADC UI, starts ADC reading process, starts timer."""
        # Simulate start button signal
        self.central_manager.on_experiment_started()

        # Check that ADC UI is disabled
        self.assertFalse(self.central_manager.adc_ui.isEnabled())

        # Check that ADC reader is initialized
        self.assertIsNotNone(self.central_manager.adc_reader)

        # Check that timer is started
        self.assertTrue(self.central_manager.timer.isActive())

    def test_stop_experiment_successfully(self) -> None:
        """stops experiment successfully, re-enables ADC UI, stops ADC reading process, stops timer."""
        # Simulate start button signal
        self.central_manager.on_experiment_started()

        # Simulate stop button signal
        self.central_manager.on_experiment_stopped()

        # Check that ADC UI is enabled
        self.assertTrue(self.central_manager.adc_ui.isEnabled())

        # Check that timer is stopped
        self.assertFalse(self.central_manager.timer.isActive())

    # def test_qtimer_is_not_connected_after_stopping(self) -> None:
    #     """Test that the timer object stops connecting"""
    #     received_data: list[float] = []

    #     def test_slot(data) -> None:
    #         received_data.append(data)

    #     self.central_manager.output_signal.connect(test_slot)

    #     # Perform a full cycle
    #     self.central_manager.capture_manager.frequency = 0
    #     self.central_manager.capture_ui.start_button.click()

    #     self.central_manager.capture_ui.stop_button.click()

    #     full_count: int = len(received_data)
    #     self.assertGreater(full_count, 0)

    #     # Forcefully emit result and see if the slot received it
    #     self.central_manager.output_signal.emit(1.5)
    #     self.assertEqual(len(received_data), full_count)

    def test_layout_is_vboxlayout(self) -> None:
        """Test that the layout is a QVBoxLayout."""
        layout = self.central_manager.layout()
        self.assertIsInstance(layout, QVBoxLayout)

    def test_layout_item_count(self) -> None:
        """Test the count of items in the layout."""
        layout = self.central_manager.layout()
        # sigh
        expected_widget_count = 7
        actual_widget_count = layout.count()
        self.assertEqual(actual_widget_count, expected_widget_count)

    def test_layout_items(self) -> None:
        """Test the types of items in the layout."""
        layout = self.central_manager.layout()
        for i in range(layout.count()):
            item = layout.itemAt(i)
            if isinstance(item.widget(), QGroupBox):
                continue  # GroupBox found, continue with the next item
            if isinstance(item, QSpacerItem):
                continue  # SpacerItem found, continue with the next item

            self.fail(f"Unexpected item type at position {i}: {type(item).__name__}")
