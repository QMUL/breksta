"""Tests the sine wave generator."""
import unittest
from unittest import mock

from app.sine_wave_generator import SineWaveGenerator
from device.adc_config import ADCConfig


class TestSineWaveGenerator(unittest.TestCase):
    """Test the sine wave generator behaves correctly,
    uses inherited ADCReader attributes."""

    def setUp(self) -> None:
        self.mock_logger = mock.Mock()
        self.mock_logger.debug = mock.Mock()
        config = ADCConfig()
        self.generator = SineWaveGenerator(config=config, channel=0, period=2, logger=self.mock_logger)

    def test_generates_sine_wave_with_noise(self) -> None:
        """generates a sine wave signal with some noise."""
        reading = self.generator.run_adc()
        self.assertIsInstance(reading, float)
