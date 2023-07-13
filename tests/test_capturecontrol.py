"""
This module contains unit tests for the CaptureControl class from the breksta module.

Each public method of CaptureControl is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest

from PySide6.QtWidgets import QApplication
from app.breksta import CaptureControl, TableWidget

# In Qt, every GUI application must have exactly one instance of QApplication or one of its subclasses.
# It's a requirement for managing a lot of application-wide resources, for initializing various Qt
# subsystems and for handling events.
# If it already exists (due to running another test), don't create one.
app = QApplication.instance()
if not app:
    app = QApplication([])


class TestCaptureControl(unittest.TestCase):
    """
    Defines the test cases for the CaptureControl class.

    The setUp method is called before executing each test method.
    In this case, a CaptureControl and a TableWidget object are set up before each test.
    """

    def setUp(self):
        width = 1
        self.table = TableWidget(width)
        self.capture_control = CaptureControl(self.table)

    def tearDown(self):
        self.capture_control = CaptureControl(self.table)

    def test_start_button_disabled_after_click(self):
        """Test that the start button is disabled after clicking it."""
        # Check the initial state: the button should be enabled
        self.assertTrue(self.capture_control.ui.start_button.isEnabled())

        # Simulate a click on the start button
        self.capture_control.ui.start_button.click()

        # Check the final state: the button should now be disabled
        self.assertFalse(self.capture_control.ui.start_button.isEnabled())

    def test_initiate_data_capture_starts_experiment(self):
        """Test that initiate_data_capture starts a new experiment."""
        # Setup: experiment_id is None
        self.assertIsNone(self.capture_control.experiment_id)

        # Simulate a click on the start button
        self.capture_control.ui.start_button.click()

        # Check that a new experiment was started
        self.assertGreater(self.capture_control.experiment_id, 0)

    def test_initiate_data_capture_takes_reading(self):
        """Test that initiate_data_capture takes a reading."""
        # Simulate a click on the start button
        self.capture_control.ui.start_button.click()

        # Check that a reading was taken
        self.assertIsNotNone(self.capture_control.device.take_reading())

    def test_qtimer_has_started(self):
        """Test that the QTimer object has initialized and is running."""
        # Check the QTimer has not started yet
        self.assertFalse(self.capture_control.sample_timer.isActive())

        # Simulate a click on the start button
        self.capture_control.ui.start_button.click()

        # Check the QTimer has started
        self.assertTrue(self.capture_control.sample_timer.isActive())

    def test_start_signal_emitted(self):
        """Test that the signal is correctly emitted on Start button click."""
        self.signal_emitted = False

        def slot(experiment_id):
            self.signal_emitted = True
            self.assertEqual(experiment_id, self.capture_control.experiment_id)

        self.capture_control.started.connect(slot)

        # Simulate a click on the start button
        self.capture_control.ui.start_button.click()

        self.assertTrue(self.signal_emitted)
