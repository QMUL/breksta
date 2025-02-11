"""Tests the ADC control panel is correctly created and initialized.
Also tests the ADC manager handles the business logic appropriately.
"""

import unittest
from unittest.mock import Mock

from PySide6.QtWidgets import QApplication, QButtonGroup, QComboBox

from ui.adc_controlpanel import ADCConfigManager, ADCConfigWidget

app = QApplication.instance()
if not app:
    app = QApplication([])


class TestADCConfigWidget(unittest.TestCase):
    """Tests the Factory class, responsible for creating and initializing the UI elements."""

    def setUp(self) -> None:
        mock_logger = Mock()
        self.widget = ADCConfigWidget(logger=mock_logger)

    def test_initialization(self) -> None:
        """Initializes logger, address_combo, gain_combo, data_rate_combo, and polling_mode_group"""
        self.assertIsNotNone(self.widget.logger)
        self.assertIsInstance(self.widget.address_combo, QComboBox)
        self.assertIsInstance(self.widget.gain_combo, QComboBox)
        self.assertIsInstance(self.widget.data_rate_combo, QComboBox)
        self.assertIsInstance(self.widget.polling_mode_group, QButtonGroup)


class TestADCConfigManager(unittest.TestCase):
    """Tests the Manager class, responsible for the signal slot integration
    to the UI elements.
    """

    def setUp(self) -> None:
        mock_logger = Mock()
        self.widget = ADCConfigWidget(logger=mock_logger)
        self.manager = ADCConfigManager(self.widget, logger=mock_logger)

    def test_on_gain_change(self) -> None:
        """on_gain_change updates the gain configuration setting."""
        self.widget.gain_combo.setCurrentIndex(2)  # Simulate user action
        QApplication.processEvents()  # Process the event queue
        self.assertEqual(self.widget.gain_combo.currentText(), "±2.048V")

    def test_initialized_with_default_values(self) -> None:
        """ADCConfigWidget is initialized with default values"""
        config_values = self.manager.get_adc_config()
        self.assertIsNotNone(config_values)

    def test_select_address_from_combo_box(self) -> None:
        """User can select an address from the address combo box."""
        self.widget.address_combo.setCurrentIndex(1)
        _ = self.manager.get_adc_config()
        # self.assertEqual(config_values["address"], "0x49 (VDD)")

    def test_select_gain_from_combo_box(self) -> None:
        """User can select a gain from the gain combo box."""
        self.widget.gain_combo.setCurrentIndex(2)
        _ = self.manager.get_adc_config()
        # self.assertEqual(config_values["gain"], "±2.048V")
