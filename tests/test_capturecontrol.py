"""
This module contains unit tests for the CaptureControl class from the breksta module.

Each public method of CaptureControl is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest

from PySide6.QtWidgets import QApplication, QVBoxLayout
from PySide6.QtCore import QTimer
from app.breksta import CaptureControl, TableWidget
from app.capture import DevCapture
from app.logger_config import setup_logger

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
        self.logger = setup_logger()
        self.logger.info('=' * 50)
        self.logger.info('TESTS STARTED')

        # Create instances of classes with the mock database session
        self.mock_db = PmtDb(Session)
        self.mock_device = DevCapture(self.mock_db)

        width = 1
        self.table = TableWidget(width, self.mock_db)
        self.capture_control = CaptureControl(self.table)

    def tearDown(self):
        self.capture_control = CaptureControl(self.table)
        self.logger.info('TESTS FINISHED')
        self.logger.info('=' * 50)
        return super().tearDown()

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

    def test_stop_button_disabled_after_click(self):
        """Test that the stop button is disabled after clicking it."""
        # Check the initial state: the button should be enabled
        self.capture_control.ui.start_button.click()
        self.assertTrue(self.capture_control.ui.stop_button.isEnabled())

        # Simulate a click on the stop button
        self.capture_control.ui.stop_button.click()

        # Check the final state: the button should now be disabled
        self.assertFalse(self.capture_control.ui.stop_button.isEnabled())

    def test_terminate_data_capture_resets_experiment_id(self):
        """Test that terminate_data_capture resets experiment_id."""
        # Setup: experiment_id is Int>0
        self.capture_control.ui.start_button.click()

        # Simulate a click on the stop button
        self.capture_control.ui.stop_button.click()

        # Check that a new experiment was started
        self.assertIsNone(self.capture_control.experiment_id)

    def test_qtimer_has_stopped(self):
        """Test that the QTimer object has stopped running."""
        # Check the QTimer has started
        self.capture_control.ui.start_button.click()
        self.assertTrue(self.capture_control.sample_timer.isActive())

        # Simulate a click on the stop button
        self.capture_control.ui.stop_button.click()

        # Check the QTimer has stopped
        self.assertFalse(self.capture_control.sample_timer.isActive())

    def test_set_freq(self):
        """Test set_freq correctly updates sample_frequency from the drop-down menu.
        Limitation: Choosing Index 0 when 0 is default, will not trigger the update."""
        # Set the current index of the frequency combo box to 1
        self.capture_control.ui.freq_box.setCurrentIndex(1)

        # Check that the sample frequency was updated correctly
        expected_frequency = int(self.capture_control.ui.freq_box.itemText(1))
        self.assertEqual(self.capture_control.sample_frequency, expected_frequency)

        # Check again, for Index 0
        self.capture_control.ui.freq_box.setCurrentIndex(0)
        expected_frequency = int(self.capture_control.ui.freq_box.itemText(0))
        self.assertEqual(self.capture_control.sample_frequency, expected_frequency)

    def test_set_dur(self):
        """Test set_dur correctly updates experiment's duration from the drop-down menu.
        Limitation: Choosing Index 0 when 0 is default, will not trigger the update."""
        # Set the current index of the duration combo box to 2
        self.capture_control.ui.dur_box.setCurrentIndex(2)

        # Check that the duration was updated correctly
        expected_duration = int(self.capture_control.ui.dur_box.itemText(2))
        self.assertEqual(self.capture_control.duration, expected_duration)

        # Check again for Index 0
        self.capture_control.ui.dur_box.setCurrentIndex(0)
        expected_duration = int(self.capture_control.ui.dur_box.itemText(0))
        self.assertEqual(self.capture_control.duration, expected_duration)

    def test_init_table(self):
        """Test that the table attribute is initialized with the provided argument."""
        dummy_table = object()  # Just a placeholder object
        capture_control = CaptureControl(dummy_table)
        self.assertIs(capture_control.table, dummy_table)

    def test_init_experiment_id(self):
        """Test that the experiment_id attribute is initialized to None."""
        self.assertIsNone(self.capture_control.experiment_id)

    def test_init_sample_frequency(self):
        """Test that the sample_frequency attribute is set based on the initial UI value."""
        expected_frequency = int(self.capture_control.ui.freq_box.itemText(0))
        self.assertEqual(self.capture_control.sample_frequency, expected_frequency)

    def test_init_duration(self):
        """Test that the duration attribute is set based on the initial UI value."""
        expected_duration = int(self.capture_control.ui.dur_box.itemText(0))
        self.assertEqual(self.capture_control.duration, expected_duration)

    def test_init_layout(self):
        """Test that the layout is a QVBoxLayout and contains the CaptureUI widget."""
        self.assertIsInstance(self.capture_control.layout(), QVBoxLayout)
        self.assertEqual(self.capture_control.layout().count(), 1)
        self.assertIs(self.capture_control.layout().itemAt(0).widget(), self.capture_control.ui)

    def test_init_device(self):
        """Test that a DevCapture instance is created for the device attribute."""
        self.assertIsInstance(self.capture_control.device, DevCapture)

    def test_init_sample_timer(self):
        """Test that a QTimer instance is created for the sample_timer attribute."""
        self.assertIsInstance(self.capture_control.sample_timer, QTimer)
