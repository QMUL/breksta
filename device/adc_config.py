"""Manages ADC configuration settings like gain and address."""
from dataclasses import dataclass
from enum import Enum
from app.logger_config import setup_logger

logger = setup_logger()


class ADS1115Address:
    """
    Encapsulates the I2C address configurations for the ADS1115 ADC.

    The ADS1115 ADC's I2C address varies based on how the ADDR pin is connected. This class
    provides constants for each possible configuration and a method to validate the I2C
    address.

    Attributes:
        GND (int): I2C address when the ADDR pin is connected to GND (0x48).
        VDD (int): I2C address when the ADDR pin is connected to VDD (0x49).
        SDA (int): I2C address when the ADDR pin is connected to SDA (0x4A).
        SCL (int): I2C address when the ADDR pin is connected to SCL (0x4B).

    Class Methods:
        is_valid(address): Checks if a given address matches one of the defined constants.
    """
    GND = 0x48  # Default
    VDD = 0x49
    SDA = 0x4A
    SCL = 0x4B

    @classmethod
    def is_valid(cls, address) -> bool:
        """
        Validates the provided I2C address.

        Arguments:
            address (int): The I2C address to validate.

        Returns:
            bool: True if the address is valid, False otherwise.
        """
        return address in [cls.GND, cls.VDD, cls.SDA, cls.SCL]


class ADS1115Gain:
    """
    Represents the gain settings for the ADS1115 ADC.

    This class defines constants for different programmable gain amplifier (PGA) settings
    available on the ADS1115 ADC. It also provides a method to validate if a given gain
    setting is supported by the ADC.

    Attributes:
        PGA_6_144V (int): Gain setting for a full-scale range of ±6.144V (default).
        PGA_4_096V (int): Gain setting for a full-scale range of ±4.096V.
        PGA_2_048V (int): Gain setting for a full-scale range of ±2.048V.
        PGA_1_024V (int): Gain setting for a full-scale range of ±1.024V.
        PGA_0_512V (int): Gain setting for a full-scale range of ±0.512V.
        PGA_0_256V (int): Gain setting for a full-scale range of ±0.256V.

    Class Methods:
        is_valid(gain): Validates if the provided gain value is among the defined constants.
    """
    PGA_6_144V = 0  # Default
    PGA_4_096V = 1
    PGA_2_048V = 2
    PGA_1_024V = 4
    PGA_0_512V = 8
    PGA_0_256V = 16

    @classmethod
    def is_valid(cls, gain) -> bool:
        """
        Validates the provided gain setting.

        Arguments:
            gain (int): The gain setting to validate.

        Returns:
            bool: True if the gain setting is valid, False otherwise.
        """
        return gain in [cls.PGA_6_144V, cls.PGA_4_096V, cls.PGA_2_048V,
                        cls.PGA_1_024V, cls.PGA_0_512V, cls.PGA_0_256V]


class ADS1115DataRate:
    """
    Represents the data rate settings for the ADS1115 ADC.

    This class defines constants for different programmable data rate settings
    available on the ADS1115 ADC. It also provides a method to validate if a given
    setting is supported by the ADC.

    Attributes:
            DR_ADS111X_8 (int): 8 samples/s
            DR_ADS111X_16 (int): 16 samples/s
            DR_ADS111X_32 (int): 32 samples/s
            DR_ADS111X_64 (int): 64 samples/s
            DR_ADS111X_128 (int): 128 samples/s (default)
            DR_ADS111X_250 (int): 250 samples/s
            DR_ADS111X_475 (int): 475 samples/s
            DR_ADS111X_860 (int): 860 samples/s

    Class Methods:
        is_valid(gain): Validates if the provided data rate value is among the defined constants.
    """
    DR_ADS111X_8 = 0  # slowest
    DR_ADS111X_16 = 1
    DR_ADS111X_32 = 2
    DR_ADS111X_64 = 3
    DR_ADS111X_128 = 4  # default
    DR_ADS111X_250 = 5
    DR_ADS111X_475 = 6
    DR_ADS111X_860 = 7  # fastest

    @classmethod
    def is_valid(cls, data_rate) -> bool:
        """
        Validates the provided data rate setting.

        Arguments:
            data_rate (int): The data rate setting to validate.

        Returns:
            bool: True if the data rate setting is valid, False otherwise.
        """
        return data_rate in [cls.DR_ADS111X_8, cls.DR_ADS111X_16, cls.DR_ADS111X_32, cls.DR_ADS111X_64,
                             cls.DR_ADS111X_128, cls.DR_ADS111X_250, cls.DR_ADS111X_475, cls.DR_ADS111X_860]


class ADS1115Mode(Enum):
    """
    Sets the polling mode.

    Attributes:
        poll_mode_continuous (int): reads in continuously
        poll_mode_single (int): reads in single-shot results
    """
    poll_mode_single = 1
    poll_mode_continuous = 0


@dataclass
class ADCConfig:
    """
    Represents the configuration settings for an ADC (Analog-to-Digital Converter).

    Attributes:
        i2c_bus (int): The I2C bus number. Default value is 1.
        address (int): The address of the ADC. Default value is ADS1115Address.GND.
        gain (int): The gain setting of the ADC. Default value is ADS1115Gain.PGA_6_144V.
        data_rate (int): The data rate of the ADC. Default value is ADS1115DataRate.DR_ADS111X_128.
        poll_mode (Enum): The polling/reading mode of the ADC. Default is ADS1115Mode.poll_mode_single.
    """

    i2c_bus: int = 1
    address: int = ADS1115Address.GND
    gain: int = ADS1115Gain.PGA_6_144V
    data_rate: int = ADS1115DataRate.DR_ADS111X_128
    poll_mode: ADS1115Mode = ADS1115Mode.poll_mode_single

    def __post_init__(self) -> None:
        """
        Validates and sets the configuration values to their defaults if they are invalid.
        """
        if not ADS1115Gain.is_valid(self.gain):
            logger.error("Invalid gain, using default.")
            self.gain = ADS1115Gain.PGA_6_144V

        if not ADS1115Address.is_valid(self.address):
            logger.error("Invalid address, using default.")
            self.address = ADS1115Address.GND

        if not ADS1115DataRate.is_valid(self.data_rate):
            logger.error("Invalid data rate, using default.")
            self.data_rate = ADS1115DataRate.DR_ADS111X_128

        try:
            # This will check if self.poll_mode is a valid enum member
            self.poll_mode = ADS1115Mode(self.poll_mode)
        except ValueError:
            # This block executes if self.poll_mode is not a valid ADS1115Mode value
            logger.error("Invalid ADC polling mode, using default single-shot operation.")
            self.poll_mode = ADS1115Mode.poll_mode_single  # Set to default or handle as needed
