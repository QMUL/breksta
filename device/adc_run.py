"""
Handles the integration of the ADC functionality with other parts of the application.

- Functions or classes that tie ADC functionalities into Breksta.
"""
from abc import ABC, abstractmethod
from device.adc_interface import initialize_adc
from device.adc_data_acquisition import read_adc_single_channel
from app.logger_config import setup_logger


class ADCReader(ABC):
    def __init__(self, config, channel, period, logger) -> None:
        self.logger = logger if logger else setup_logger()

        self.adc = initialize_adc(adc_config=config)
        self.is_initialized = self.adc is not None
        if not self.is_initialized:
            self.logger.critical("ADC could not be initialized.")

        self.channel: int = channel
        self.period: int = period

        if hasattr(self.adc, 'toVoltage'):
            self.to_voltage: float = self.adc.toVoltage()

    def is_operational(self) -> bool:
        """ Check if the ADCReader is in a valid state. """
        return self.is_initialized

    def __enter__(self):
        # Setup actions (if any)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Teardown actions (like closing resources)
        pass

    @abstractmethod
    def run_adc(self) -> float:
        pass


class SingleShotADCReader(ADCReader):
    def run_adc(self) -> float:
        if not self.is_operational():
            self.logger.error("ADCReader is not operational.")
            return 0.0

        result: float = read_adc_single_channel(self.adc, self.channel)
        self.logger.debug(result * self.to_voltage)
        return result * self.to_voltage


class ContinuousADCReader(ADCReader):
    def run_adc(self) -> float:
        if not self.is_operational():
            self.logger.error("ADCReader is not operational.")
            return 0.0

        result: float = read_adc_single_channel(self.adc, self.channel)
        self.logger.debug(result * self.to_voltage)
        return result * self.to_voltage
