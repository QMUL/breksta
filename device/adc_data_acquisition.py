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


def read_adc_values(adc) -> dict:
    """
    Reads values from the ADC channels.

    Arguments:
        adc: The ADC object.
    Returns:
        Dictionary of ADC values for each channel.
    """
    adc_values = {}
    voltage_factor = adc.toVoltage()

    for channel in range(4):  # Assuming 4 channels (0 to 3)
        value = adc.readADC(channel)
        voltage = value * voltage_factor
        adc_values[f'channel_{channel}'] = {'raw': value, 'voltage': voltage}

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
    adc = initialize_adc(adc_config=config)
    if not adc:
        logger.error("Failed to initialize the ADC. Exiting.")
        return

    logger.info("Starting regular read every %s s", period)
    while True:
        # Read ADC values
        adc_values = read_adc_values(adc)

        # Process and display the values
        for channel, values in adc_values.items():
            logger.debug(f"{channel}: {values['raw']}\t{values['voltage']:.3f} V")

        # Wait for a period of time before the next read
        time.sleep(period)
