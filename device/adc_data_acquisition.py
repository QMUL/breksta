"""
Focuses on acquiring data from the ADC.

- Functions for reading from ADC channels.
- Data processing or filtering methods specific to ADC data.
"""

import time

from app.logger_config import setup_logger
from device.adc_config import ADCConfig
from device.adc_interface import initialize_adc

logger = setup_logger()


def read_adc_single_channel(adc, channel) -> float:
    """
    Reads values from a channel. Should be mode-agnostic.

    Arguments: adc: the ADC object.
    Returns: float: the value
    """
    reading: float = adc.readADC(channel)
    return reading


def read_adc_single_shot(adc, channel, period):
    """Reads values from the ADC. Uses single mode."""
    logger.info("Starting single-shot read every %ss", period)
    while True:
        voltage = read_adc_single_channel(adc, channel)
        logger.debug("V: %s", voltage)
        time.sleep(period)


def read_adc_continuous(adc, channel, period):
    """Reads values from the ADC. Uses continuous operation mode."""
    logger.info("Starting continuous read every %ss", period)
    while True:
        voltage = read_adc_single_channel(adc, channel)
        logger.debug("V: %s", voltage)
        time.sleep(period)


def read_adc_values_all_channels(adc) -> dict:
    """
    Reads values from the ADC channels/pins.

    Arguments:
        adc: The ADC object.
    Returns:
        Dictionary of ADC values for each channel.
    """
    adc_values = {}
    voltage_factor = adc.toVoltage()

    # Assuming 4 channels (0 to 3), README calls them "Pins"
    for channel in range(4):
        value = adc.readADC(channel)
        voltage = value * voltage_factor
        adc_values[f"channel_{channel}"] = {"raw": value, "voltage": voltage}

    return adc_values


def adc_regular_read(period: float) -> None:
    """
    Orchestrates regular reading from the ADC.

    This function initializes the ADC and then enters a loop where it reads
    ADC values at a specified interval. If initialization fails, it logs an error and exits.

    Arguments:
        period (float): Time interval (in seconds) between successive ADC reads.
    """
    # Set up ADC configuration
    config = ADCConfig()
    # Initialize the ADC
    adc = initialize_adc(adc_config=config, logger=logger)
    if not adc:
        logger.error("Failed to initialize the ADC. Exiting.")
        return

    logger.info("Starting regular read every %s s", period)
    while True:
        # Read ADC values
        adc_values = read_adc_values_all_channels(adc)

        # Process and display the values
        for channel, values in adc_values.items():
            logger.debug(f"{channel}: {values['raw']}\t{values['voltage']:.3f} V")

        # Wait for a period of time before the next read
        time.sleep(period)
