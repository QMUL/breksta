"""
This module integrates ADC (Analog-to-Digital Converter) functionalities with the Breksta application.
It provides classes to read data from ADC devices in both single-shot and continuous modes.
"""

from abc import ABC, abstractmethod
from device.adc_interface import initialize_adc
from device.adc_data_acquisition import read_adc_single_channel
from app.logger_config import setup_logger


class ADCReader(ABC):
    """
    An abstract base class for ADC reading operation modes.

    This class provides a common interface for different ADC reading strategies. It initializes
    the ADC device, manages state, and defines the basic structure for ADC data acquisition.

    Attributes:
        logger: Logger for logging information.
        adc: The initialized ADC device.
        is_initialized: Boolean indicating if the ADC was successfully initialized.
        channel: The ADC channel to read from.
        period: The time period for ADC data acquisition.
        to_voltage: The conversion factor from ADC reading to voltage (if applicable).

    Methods:
        is_operational: Checks if the ADCReader is properly initialized and operational.
        run_adc: Abstract method to be implemented for ADC data acquisition.
    """
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
    """
    A concrete implementation of ADCReader for single-shot ADC readings.

    This class overrides the run_adc method to perform a single ADC data acquisition.
    """

    def run_adc(self) -> float:
        """
        Performs a single ADC data acquisition.

        This method reads a single data point from the ADC channel specified in the class instance.
        It logs the result and returns the ADC reading converted to voltage if applicable.

        Returns:
            float: The ADC reading converted to voltage, or 0.0 if the ADCReader is not operational.
        """

        if not self.is_operational():
            self.logger.error("ADCReader is not operational.")
            return 0.0

        result: float = read_adc_single_channel(self.adc, self.channel)
        self.logger.debug(result * self.to_voltage)
        return result * self.to_voltage


class ContinuousADCReader(ADCReader):
    """
    A concrete implementation of ADCReader for continuous ADC readings.

    This class overrides the run_adc method to continuously read data from the ADC.
    Note: The current implementation is similar to SingleShotADCReader, and may need
    further development for true continuous reading functionality.
    """

    def run_adc(self) -> float:
        """
        Intended for continuous ADC data acquisition.

        Currently, this method behaves similarly to the run_adc method in SingleShotADCReader,
        performing a single ADC data acquisition. Future implementations should modify this method
        to facilitate true continuous data acquisition.

        Returns:
            float: The ADC reading converted to voltage, or 0.0 if the ADCReader is not operational.
        """

        if not self.is_operational():
            self.logger.error("ADCReader is not operational.")
            return 0.0

        result: float = read_adc_single_channel(self.adc, self.channel)
        self.logger.debug(result * self.to_voltage)
        return result * self.to_voltage
