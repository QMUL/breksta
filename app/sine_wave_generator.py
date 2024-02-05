"""Encapsulate all mock device/sine wave generator functionality."""

import math
import random
from datetime import datetime
from device.adc_run import ADCReader


class SineWaveGenerator(ADCReader):
    """Class that simulates a data capture device, aligned with the ADCReader interface.
    Simulates ADC reading using a sine wave with some noise.
    """
    def init_instance(self, config, channel, period, logger) -> None:
        super().init_instance(config, channel, period, logger)
        self.logger = logger
        self.config = config
        self.channel = channel
        self.period = period
        self.start_time = datetime.now()
        self.omega = 2.0 * math.pi / 60  # Omega for sine wave, assuming a 1-minute cycle
        self.is_initialized = True

    def run_adc(self) -> float:
        """Simulates taking an ADC reading, matching the ADCReader interface.
        Returns:
            float: The simulated ADC reading.
        """
        noise: float = (0.08 * random.random()) - 0.04  # Generate random noise
        signal: float = 0.92 * math.sin(self.omega * (datetime.now() - self.start_time).total_seconds())  # Sine wave signal
        reading: int = 32768 + int(32768 * (signal + noise))  # Convert to simulated reading
        self.logger.debug("Simulated ADC reading: %s", reading)
        return float(reading)
