"""
Handles the integration of the ADC functionality with other parts of the application.

- Functions or classes that tie ADC functionalities into Breksta.
"""
from abc import ABC, abstractmethod
from device.adc_config import ADCConfig
from device.adc_interface import initialize_adc
from device.adc_data_acquisition import read_adc_single_shot, read_adc_continuous, read_adc_single_channel
from app.logger_config import setup_logger


class ADCReader(ABC):
    def __init__(self, config, channel, period, logger) -> None:
        self.logger = logger if logger else setup_logger()

        try:
            self.adc = self.configure_adc(config)
            if self.adc is None:
                self.logger.critical("ADC could not be initialized.")
        except Exception as err:
            self.logger.exception("ADC initialization failed: %s", err)
            raise

        self.channel = channel
        self.period = period

    def configure_adc(self, config: ADCConfig):
        """
        On instantiation of the class, create a new adc configuration by reading all GUI-related values
        and initialize the ADC device.
        """
        adc = initialize_adc(adc_config=config)
        if not adc:
            return None
        return adc

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
        # read_adc_single_shot(self.adc, self.channel, self.period)
        return read_adc_single_channel(self.adc, self.channel)


class ContinuousADCReader(ADCReader):
    def run_adc(self) -> float:
        # read_adc_continuous(self.adc, self.channel, self.period)
        return read_adc_single_channel(self.adc, self.channel)
