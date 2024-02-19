"""This module contains unit tests for the CaptureControlUI and CaptureControlManager classes from the ui module.

The public methods both classes are tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest
from unittest.mock import MagicMock

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QComboBox, QLineEdit, QPushButton

from ui.capture_controlpanel import CaptureControlManager, CaptureControlUI

# In Qt, every GUI application must have exactly one instance of QApplication or one of its subclasses.
# It's a requirement for managing a lot of application-wide resources, for initializing various Qt
# subsystems and for handling events.
# If it already exists, don't create another one
app = QApplication.instance()
if not app:
    app = QApplication([])


class TestCaptureUI(unittest.TestCase):
    """Defines the test cases for the CaptureUI class.

    The setUp method is called before executing each test method, and it's used to set up any objects
    that are utilized by the test methods. In this case, a CaptureUI object is set up before each test.
    """

    def setUp(self) -> None:
        self.mock_logger = MagicMock()

        self.capture_ui = CaptureControlUI(self.mock_logger)

    def test_ui_elements_initialization(self) -> None:
        """Tests the initialization of UI elements in CaptureUI.

        This test ensures that all UI elements are of the correct type and are initialized as expected.
        """
        self.assertIsInstance(self.capture_ui.start_button, QPushButton)
        self.assertIsInstance(self.capture_ui.stop_button, QPushButton)
        self.assertIsInstance(self.capture_ui.name_box, QLineEdit)
        self.assertIsInstance(self.capture_ui.freq_box, QComboBox)
        self.assertIsInstance(self.capture_ui.dur_box, QComboBox)

    def test_default_values(self) -> None:
        """Tests the default values of UI elements in CaptureUI.

        This test checks that the experiment name, sample frequency, and experiment duration are set to
        their expected default values.
        """
        self.assertEqual(self.capture_ui.name_box.text(), self.capture_ui.DEFAULT_EXPERIMENT_NAME)
        self.assertEqual(self.capture_ui.freq_box.currentText(), str(self.capture_ui.DEFAULT_EXPERIMENT_POLLRATE))
        self.assertEqual(self.capture_ui.dur_box.currentText(), str(self.capture_ui.DEFAULT_EXPERIMENT_DURATION))


class TestCaptureControlManager(unittest.TestCase):
    """Defines the test cases for the CaptureUI class.

    The setUp method is called before executing each test method, and it's used to set up any objects
    that are utilized by the test methods. In this case, a CaptureUI object is set up before each test.
    """

    def setUp(self) -> None:
        self.mock_logger = MagicMock()

        self.capture_ui = CaptureControlUI(self.mock_logger)
        self.capture_manager = CaptureControlManager(self.capture_ui, self.mock_logger)

    def test_on_start_button_click(self) -> None:
        """Test that the on_start_button_click method updates the UI elements correctly."""
        # Call the on_start_button_click method
        self.capture_manager.on_start_button_click()

        # Check that the start button is now disabled
        self.assertFalse(self.capture_ui.start_button.isEnabled())

        # Check that the stop button is now enabled
        self.assertTrue(self.capture_ui.stop_button.isEnabled())

        # Check that the frequency and duration dropdown menus are now disabled
        self.assertFalse(self.capture_ui.freq_box.isEnabled())
        self.assertFalse(self.capture_ui.dur_box.isEnabled())

        # Check that the name box is now disabled
        self.assertFalse(self.capture_ui.name_box.isEnabled())

    def test_on_stop_button_click(self) -> None:
        """Test that the on_stop_button_click method updates the UI elements correctly."""
        # Call the on_stop_button_click method
        self.capture_manager.on_stop_button_click()

        # Check that the start button is now enabled
        self.assertTrue(self.capture_ui.start_button.isEnabled())

        # Check that the stop button is now disabled
        self.assertFalse(self.capture_ui.stop_button.isEnabled())

        # Check that the frequency and duration dropdown menus are enabled
        self.assertTrue(self.capture_ui.freq_box.isEnabled())
        self.assertTrue(self.capture_ui.dur_box.isEnabled())

        # Check that the name box is now enabled
        self.assertTrue(self.capture_ui.name_box.isEnabled())

    def test_start_button_disabled_after_click(self) -> None:
        """Test that the start button is disabled after clicking it."""
        # Check the initial state: the button should be enabled
        self.assertTrue(self.capture_ui.start_button.isEnabled())

        # Simulate a click on the start button
        self.capture_ui.start_button.click()

        # Check the final state: the button should now be disabled
        self.assertFalse(self.capture_ui.start_button.isEnabled())

    def test_init_sample_frequency(self) -> None:
        """Test that the sample_frequency attribute is set based on the initial UI value."""
        expected_frequency = int(self.capture_ui.freq_box.itemText(0))
        self.assertEqual(self.capture_manager.frequency, expected_frequency)

    def test_init_duration(self) -> None:
        """Test that the duration attribute is set based on the initial UI value."""
        expected_duration = int(self.capture_ui.dur_box.itemText(0))
        self.assertEqual(self.capture_manager.duration, expected_duration)

    def test_set_freq(self) -> None:
        """Test set_freq correctly updates sample_frequency from the drop-down menu.
        Limitation: Choosing Index 0 when 0 is default, will not trigger the update."""
        # Set the current index of the frequency combo box to 1
        self.capture_ui.freq_box.setCurrentIndex(1)

        # Check that the sample frequency was updated correctly
        expected_frequency = int(self.capture_ui.freq_box.itemText(1))
        self.assertEqual(self.capture_manager.frequency, expected_frequency)

        # Check again, for Index 0
        self.capture_ui.freq_box.setCurrentIndex(0)
        expected_frequency = int(self.capture_ui.freq_box.itemText(0))
        self.assertEqual(self.capture_manager.frequency, expected_frequency)

    def test_set_dur(self) -> None:
        """Test set_dur correctly updates experiment's duration from the drop-down menu.
        Limitation: Choosing Index 0 when 0 is default, will not trigger the update."""
        # Set the current index of the duration combo box to 2
        self.capture_ui.dur_box.setCurrentIndex(2)

        # Check that the duration was updated correctly
        expected_duration = int(self.capture_ui.dur_box.itemText(2))
        self.assertEqual(self.capture_manager.duration, expected_duration)

        # Check again for Index 0
        self.capture_ui.dur_box.setCurrentIndex(0)
        expected_duration = int(self.capture_ui.dur_box.itemText(0))
        self.assertEqual(self.capture_manager.duration, expected_duration)

    def test_init_sample_timer(self) -> None:
        """Test that a QTimer instance is created for the sample_timer attribute."""
        self.assertIsInstance(self.capture_manager.sampling_timer, QTimer)
