"""
Houses all functionality to talk to the I2C.
The specific sensor model we use corresponds to the ADS1x15.ADS1115 object.
If the device changes, the initializer will also have to change.
"""

import ADS1x15 as ads

from device.adc_config import ADCConfig, ADS1115Mode


def initialize_adc(adc_config: ADCConfig, logger) -> ads.ADS1115 | None:
    """
    Initializes and configures the ADC using the provided configuration.

    Args:
        adc_config (ADCConfig): Configuration object containing settings for the ADC,
                                including I2C bus number, address, gain, and data rate.
        logger: The main logger object, dependency injected by parents.

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
    logger.debug("Polling mode: %s", adc_config.poll_mode)

    try:
        # Initialize the ADC with the specified I2C bus and address
        adc = ads.ADS1115(adc_config.i2c_bus, adc_config.address)
    except OSError as e:
        logger.error("Initializing ADS failed: %s", e)
        return None

    # Set the polling mode before the single read
    set_adc_polling_mode(adc, adc_config, logger)

    # Check if a critical method exists
    if not hasattr(adc, "setGain"):
        logger.error("Initializing ADS failed: missing method 'setGain'.")
        return None

    adc.setGain(adc_config.gain)
    adc.setDataRate(adc_config.data_rate)

    # commit changes
    singular_read = commit_adc_config(adc, logger)
    if not singular_read:
        return None

    # validate the device's reported configuration matches the adc_config
    if not is_adc_config_match(adc, adc_config, logger):
        return None

    logger.info("Initialization of ADC/I2C interface completed.")

    return adc


def set_adc_polling_mode(adc, config: ADCConfig, logger) -> None:
    """
    Sets the ADC polling mode to single-shot or continuous operation.
    """
    if config.poll_mode == ADS1115Mode.poll_mode_single:
        adc.setMode(adc.MODE_SINGLE)
        logger.debug("ADC polling mode: Single-shot operation.")
    elif config.poll_mode == ADS1115Mode.poll_mode_continuous:
        adc.setMode(adc.MODE_CONTINUOUS)
        logger.debug("ADC polling mode: Continuous operation.")
    else:
        logger.error("Invalid ADC mode: %s", config.poll_mode)
        logger.error("Defaulting to Single-shot operation.")
        adc.setMode(adc.MODE_SINGLE)


def commit_adc_config(adc, logger) -> bool:
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


def is_adc_config_match(adc, config: ADCConfig, logger) -> bool:
    """Use the getter device functions to ascertain the config has been correctly set."""
    gain = adc.getGain()  # Get programmable gain amplifier configuration
    if config.gain != gain:
        logger.error("ADC Configuration mismatch gain: input %s vs device %s", config.gain, gain)
        return False

    data_rate = adc.getDataRate()  # Get data rate configuration
    if config.data_rate != data_rate:
        logger.error("ADC Configuration mismatch data rate: input %s vs device %s", config.data_rate, data_rate)
        return False
    return True
