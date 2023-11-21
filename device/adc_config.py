"""Manages ADC configuration settings like gain and address."""


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
