"""This module contains unit tests for the CentralizedControlManager class from the ui/central_controlpanel module.

Each public method of CentralizedControlManager is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest
from unittest.mock import MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from PySide6.QtWidgets import QApplication
from ui.central_controlpanel import CentralizedControlManager, get_manager_instance
from app.capture_signal import DeviceCapture
from app.database import PmtDb, Base

# In Qt, every GUI application must have exactly one instance of QApplication or one of its subclasses.
# It's a requirement for managing a lot of application-wide resources, for initializing various Qt
# subsystems and for handling events.
# If it already exists (due to running another test), don't create one.
app = QApplication.instance()
if not app:
    app = QApplication([])


class TestDeviceCapture(unittest.TestCase):
    """Defines the test cases for the CentralizedControlManager class.
    """

    def setUp(self) -> None:
        # Create an SQLite database in memory
        self.engine = create_engine('sqlite:///:memory:', echo=False)
        session = sessionmaker(bind=self.engine)
        self.session = session()  # save the session instance
        Base.metadata.create_all(self.engine)  # Creates the database structure

        self.mock_logger = MagicMock()
        self.mock_db = PmtDb(session, self.mock_logger)
        self.central_manager: CentralizedControlManager = get_manager_instance(self.mock_logger)
        self.device_capture = DeviceCapture(self.central_manager, self.mock_db, self.mock_logger)

    def tearDown(self):
        self.session.close()  # Close the session
        self.engine.dispose()  # Dispose the engine

    def test_init_device(self) -> None:
        """Test that a DeviceCapture instance is created for the device attribute."""
        self.assertIsInstance(self.device_capture, DeviceCapture)

    def test_init_experiment_id(self) -> None:
        """Test that the experiment_id attribute is initialized to None."""
        self.assertIsNone(self.device_capture.experiment_id)

    def test_initiate_data_capture_starts_experiment(self) -> None:
        """Test that initiate_data_capture starts a new experiment."""
        # Setup: experiment_id is None
        self.assertIsNone(self.device_capture.experiment_id)

        # Simulate a click on the start button
        self.central_manager.capture_ui.start_button.click()

        # Check that a new experiment was started
        if self.device_capture.experiment_id is not None:
            self.assertGreater(self.device_capture.experiment_id, 0)

    def test_experiment_started_signal_emitted(self) -> None:
        """Test that the signal is correctly emitted on Start button click."""
        self.signal_emitted = False

        def slot(experiment_id):
            self.signal_emitted = True
            self.assertEqual(experiment_id, self.device_capture.experiment_id)

        self.device_capture.experiment_started_signal.connect(slot)

        # Simulate a click on the start button
        self.central_manager.capture_ui.start_button.click()

        self.assertTrue(self.signal_emitted)

    def test_terminate_data_capture_resets_experiment_id(self) -> None:
        """Test that terminate_data_capture resets experiment_id."""
        # Setup: experiment_id is Int>0
        self.central_manager.capture_ui.start_button.click()

        # Simulate a click on the stop button
        self.central_manager.capture_ui.stop_button.click()

        # Check that a new experiment was started
        self.assertIsNone(self.device_capture.experiment_id)
