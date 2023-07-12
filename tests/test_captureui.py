"""
This module contains unit tests for the CaptureUI class from the breksta module.

Each public method of CaptureUI is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest

from PySide6.QtWidgets import QApplication, QPushButton, QLineEdit, QComboBox
from app.breksta import CaptureUI

# In Qt, every GUI application must have exactly one instance of QApplication or one of its subclasses.
# It's a requirement for managing a lot of application-wide resources, for initializing various Qt
# subsystems and for handling events.
app = QApplication([])


class TestCaptureUI(unittest.TestCase):
    """
    Defines the test cases for the CaptureUI class.

    The setUp method is called before executing each test method, and it's used to set up any objects
    that are utilized by the test methods. In this case, a CaptureUI object is set up before each test.
    """

    def setUp(self):
        self.capture_ui = CaptureUI()

    def test_ui_elements_initialization(self):
        """
        Tests the initialization of UI elements in CaptureUI.

        This test ensures that all UI elements are of the correct type and are initialized as expected.
        """
        self.assertIsInstance(self.capture_ui.start_button, QPushButton)
        self.assertIsInstance(self.capture_ui.stop_button, QPushButton)
        self.assertIsInstance(self.capture_ui.name_box, QLineEdit)
        self.assertIsInstance(self.capture_ui.freq_box, QComboBox)
        self.assertIsInstance(self.capture_ui.dur_box, QComboBox)

    def test_default_values(self):
        """
        Tests the default values of UI elements in CaptureUI.

        This test checks that the experiment name, sample frequency, and experiment duration are set to
        their expected default values.
        """
        self.assertEqual(self.capture_ui.name_box.text(), 'experiment_1')
        self.assertEqual(self.capture_ui.freq_box.currentText(), '2')
        self.assertEqual(self.capture_ui.dur_box.currentText(), '1')
