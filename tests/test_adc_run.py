"""Tests the Abstract ADC Reader implementations."""

import unittest
from unittest import mock

from app.sine_wave_generator import SineWaveGenerator
from device.adc_config import ADCConfig
from device.adc_run import ContinuousADCReader, SingleShotADCReader


class TestADCReaderImplementations(unittest.TestCase):
    """Defines the test cases for the implementations of the Abstract class ADCReader.

    ADCReader is a singleton for every type of implementation.
    """

    def setUp(self) -> None:
        self.mock_logger = mock.MagicMock()
        self.config = ADCConfig()

    def test_single_shot_id_not_change(self) -> None:
        """Tests that repeated instances of the SingleShot implementation have the same id."""
        reader = SingleShotADCReader(self.config, 0, 1, self.mock_logger)
        reader_id = id(reader)

        reader_repeat = SingleShotADCReader(self.config, 0, 1, self.mock_logger)
        self.assertEqual(id(reader_repeat), reader_id)

    def test_continuous_id_not_change(self) -> None:
        """Tests that repeated instances of the Continuous implementation have the same id."""
        reader = ContinuousADCReader(self.config, 0, 1, self.mock_logger)
        reader_id = id(reader)

        reader_repeat = ContinuousADCReader(self.config, 0, 1, self.mock_logger)
        self.assertEqual(id(reader_repeat), reader_id)

    def test_sinewave_generator_id_not_change(self) -> None:
        """Tests that repeated instances of the SineWave Generator implementation have the same id."""
        reader = SineWaveGenerator(self.config, 0, 1, self.mock_logger)
        reader_id = id(reader)

        reader_repeat = SineWaveGenerator(self.config, 0, 1, self.mock_logger)
        self.assertEqual(id(reader_repeat), reader_id)

    def test_singleshot_to_continuous(self) -> None:
        """Tests that an instance of the SingleShot implementation has a different id
        than an instance of the Continuous implementation."""
        reader = SingleShotADCReader(self.config, 0, 1, self.mock_logger)
        reader_id = id(reader)

        reader_repeat = ContinuousADCReader(self.config, 0, 1, self.mock_logger)
        self.assertNotEqual(id(reader_repeat), reader_id)

    def test_continuous_to_singleshot(self) -> None:
        """Tests that an instance of the Continuous implementation has a different id
        than an instance of the SingleShot implementation."""
        reader = ContinuousADCReader(self.config, 0, 1, self.mock_logger)
        reader_id = id(reader)

        reader_repeat = SingleShotADCReader(self.config, 0, 1, self.mock_logger)
        self.assertNotEqual(id(reader_repeat), reader_id)
