"""Tests the ADC configuration is correctly assembled, shown in the UI,
and committed to the device."""
import unittest
from unittest.mock import MagicMock, patch

import device.adc_config as adcC
from device.adc_config import ADCConfig, ADS1115Address, ADS1115DataRate, ADS1115Gain


class TestADCConfig(unittest.TestCase):
    """Check the configuration assembly for validity."""

    def setUp(self) -> None:
        self.mock_logger = MagicMock()
        # Mock the logger within adc_config module
        self.logger_patch = patch("device.adc_config.logger", return_value=self.mock_logger)
        self.logger_patch.start()
        adcC.logger = self.mock_logger

    def tearDown(self) -> None:
        self.logger_patch.stop()
        return super().tearDown()

    def test_default_values(self) -> None:
        """ADCConfig is instantiated with default values."""
        config = ADCConfig()
        self.assertEqual(config.i2c_bus, 1)
        self.assertEqual(config.address, ADS1115Address.GND)
        self.assertEqual(config.gain, ADS1115Gain.PGA_6_144V)
        self.assertEqual(config.data_rate, ADS1115DataRate.DR_ADS111X_128)

    def test_valid_values_all_attributes(self) -> None:
        """ADCConfig is instantiated with valid values for all attributes."""
        config = ADCConfig(
            i2c_bus=2, address=ADS1115Address.VDD, gain=ADS1115Gain.PGA_4_096V, data_rate=ADS1115DataRate.DR_ADS111X_64
        )
        self.assertEqual(config.i2c_bus, 2)
        self.assertEqual(config.address, ADS1115Address.VDD)
        self.assertEqual(config.gain, ADS1115Gain.PGA_4_096V)
        self.assertEqual(config.data_rate, ADS1115DataRate.DR_ADS111X_64)

    def test_valid_values_some_attributes_default_values_others(self) -> None:
        """ADCConfig is instantiated with valid values for some attributes and default values for others."""
        config = ADCConfig(i2c_bus=2, gain=ADS1115Gain.PGA_4_096V)
        self.assertEqual(config.i2c_bus, 2)
        self.assertEqual(config.address, ADS1115Address.GND)
        self.assertEqual(config.gain, ADS1115Gain.PGA_4_096V)
        self.assertEqual(config.data_rate, ADS1115DataRate.DR_ADS111X_128)

    def test_invalid_values_all_attributes_post_init_called_fixed(self) -> None:
        """ADCConfig is instantiated with invalid values for all attributes, and __post_init__ is called and sets
        all attributes to their default values."""
        config = ADCConfig(i2c_bus=3, address=0x4C, gain=10, data_rate=9)
        self.assertEqual(config.address, ADS1115Address.GND)
        self.assertEqual(config.gain, ADS1115Gain.PGA_6_144V)
        self.assertEqual(config.data_rate, ADS1115DataRate.DR_ADS111X_128)

    def test_invalid_values_some_attributes_post_init_called(self) -> None:
        """ADCConfig is instantiated with invalid values for some attributes and valid values for others,
        and __post_init__ is called and sets the invalid attributes to their default values.
        """
        config = ADCConfig(i2c_bus=3, address=0x4C, gain=ADS1115Gain.PGA_4_096V, data_rate=9)
        self.assertEqual(config.i2c_bus, 3)
        self.assertEqual(config.address, ADS1115Address.GND)
        self.assertEqual(config.gain, ADS1115Gain.PGA_4_096V)
        self.assertEqual(config.data_rate, ADS1115DataRate.DR_ADS111X_128)

    def test_invalid_values_all_attributes_post_init_not_called(self) -> None:
        """ADCConfig is instantiated with invalid values for all attributes, and __post_init__ is not called."""
        config = ADCConfig(i2c_bus=3, address=0x4C, gain=10, data_rate=9)
        self.assertEqual(config.i2c_bus, 3)
        self.assertEqual(config.address, ADS1115Address.GND)
        self.assertEqual(config.gain, ADS1115Gain.PGA_6_144V)
        self.assertEqual(config.data_rate, ADS1115DataRate.DR_ADS111X_128)
