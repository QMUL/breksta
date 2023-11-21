"""
Houses all functionality to talk to the I2C.
The specific sensor model we use corresponds to the ADS1x15.ADS1115 object.
If the device changes, the initializer will also have to change.
"""
import time

import ADS1x15 as ads
from device.adc_config import ADS1115Gain, ADS1115Address
from app.logger_config import setup_logger

logger = setup_logger()


def initialize_adc(i2c_bus=1, address=ADS1115Address.GND, gain=ADS1115Gain.PGA_4_096V) -> ads.ADS1115 | None:
    """
    Initializes and configures the ADC.

    Arguments:
        i2c_bus (int): The I2C bus number (default is 1).
        address (int): The I2C address of the ADC (default is GND).
        gain (int): Gain setting for the ADC (default is 4.096V).

    Returns:
        adc: Configured ADC object.
        None: If initialization failed
    """
    logger.info("Initializing device interface...")
    logger.debug("Bus ID: %s", i2c_bus)
    logger.debug("Address: %s", address)
    logger.debug("Gain: %s", gain)

    if not ADS1115Gain.is_valid(gain):
        logger.info("Gain value is invalid. See documentation.")
        logger.debug("Gain value is %s", gain)
        return None

    if not ADS1115Address.is_valid(address):
        logger.info("Address value is invalid. See documentation.")
        logger.debug("Address value is %s", address)
        return None

    try:
        # Initialize the ADC with the specified I2C bus and address
        adc = ads.ADS1115(i2c_bus, address)
    except Exception as e:
        logger.error("Initializing ADS failed: %s", e)
        return None

    # Set the gain if the method exists
    if hasattr(adc, 'setGain'):
        adc.setGain(gain)

    return adc


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
    # Initialize the ADC
    adc = initialize_adc()
    logger.info("Starting regular read every %s s", period)
    if not adc:
        logger.error("Failed to initialize the ADC. Exiting.")
        return

    while True:
        # Read ADC values
        adc_values = read_adc_values(adc)

        # Process and display the values
        for channel, values in adc_values.items():
            logger.debug(f"{channel}: {values['raw']}\t{values['voltage']:.3f} V")

        # Wait for a period of time before the next read
        time.sleep(period)
