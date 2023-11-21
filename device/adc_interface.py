"""
Houses all functionality to talk to the I2C.
The specific sensor model we use corresponds to the ADS1x15.ADS1115 object.
If the device changes, the initializer will also have to change.
"""
import time

import ADS1x15 as ads
from device.adc_config import ADCConfig
from app.logger_config import setup_logger

logger = setup_logger()


def initialize_adc(adc_config: ADCConfig) -> ads.ADS1115 | None:
    """
    Initializes and configures the ADC using the provided configuration.

    Args:
        adc_config (ADCConfig): Configuration object containing settings for the ADC,
                                including I2C bus number, address, gain, and data rate.

    Returns:
        ads.ADS1115 | None: Configured ADC object or None if initialization fails.

    The function attempts to initialize the ADC with the given configuration.
    It also validates that the ADC configuration has been correctly set by performing a test read
    and comparing the device's actual settings against the intended configuration.
    """
    logger.info("Initializing ADC/I2C device interface...")
    logger.debug("Bus ID: %s", adc_config.i2c_bus)
    logger.debug("Address: %s", adc_config.address)
    logger.debug("Gain: %s", adc_config.gain)
    logger.debug("Data rate: %s", adc_config.data_rate)

    try:
        # Initialize the ADC with the specified I2C bus and address
        adc = ads.ADS1115(adc_config.i2c_bus, adc_config.address)
    except Exception as e:
        logger.error("Initializing ADS failed: %s", e)
        return None

    # Check if a critical method exists
    if not hasattr(adc, 'setGain'):
        logger.error("Initializing ADS failed: missing method 'setGain'.")
        return None

    adc.setGain(adc_config.gain)
    adc.setDataRate(adc_config.data_rate)

    # commit changes
    single_read = commit_adc_config(adc)
    if not single_read:
        return None

    # validate the device's reported configuration matches the adc_config
    if not is_adc_config_match(adc, adc_config):
        return None

    logger.info("Initialization of ADC/I2C interface completed.")

    return adc


def commit_adc_config(adc) -> bool:
    """
    Performs a test read to commit the ADC configuration.

    Returns:
        bool: True if the read operation is successful, False otherwise.
    """
    channel = 0
    test = adc.readADC(channel)

    # Check if the read value is a known error condition (e.g., 0 for invalid pin)
    if test == 0:
        logger.error("ADC returned an error value for channel %s. Read value: %s", channel, test)
        return False

    return True


def is_adc_config_match(adc, config: ADCConfig) -> bool:
    """Use the getter device functions to ascertain the config has been correctly set.
    """
    gain = adc.getGain()  # Get programmable gain amplifier configuration
    if config.gain != gain:
        logger.error("ADC Configuration mismatch gain: input %s vs device %s", config.gain, gain)
        return False

    data_rate = adc.getDataRate()  # Get data rate configuration
    if config.data_rate != data_rate:
        logger.error("ADC Configuration mismatch data rate: input %s vs device %s", config.data_rate, data_rate)
        return False
    return True


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
