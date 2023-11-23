"""
Handles the integration of the ADC functionality with other parts of the application.

- Functions or classes that tie ADC functionalities into Breksta.
"""
from device.adc_config import ADCConfig
from device.adc_interface import initialize_adc


def config_adc_on_click():
    """
    On button click:
    - Create a new adc configuration
    - initialize adc
    """
    config: ADCConfig = modify_adc_config()
    adc = initialize_adc(adc_config=config)
    if not adc:
        return None
    return adc


def get_gui_i2c_bus_value():
    """We are not checking for bus values. The only mention and valid value is '1'.
    """
    return 1


def get_gui_gain_value():
    return -1


def get_gui_address_value():
    return -1


def get_gui_data_rate_value():
    """WIP"""
    return -1


def get_gui_poll_mode_value():
    """WIP"""
    return -1


def modify_adc_config() -> ADCConfig:
    """
    Gathers ADC configuration settings from GUI elements and returns a new ADCConfig object.
    This function should be connected to a button press event in the GUI.
    """
    new_gain = get_gui_gain_value()
    new_address = get_gui_address_value()
    new_data_rate = get_gui_data_rate_value()
    new_i2c_bus = get_gui_i2c_bus_value()
    new_poll_mode = get_gui_poll_mode_value()

    # Create and return a new ADCConfig object with values from the GUI
    return ADCConfig(
        i2c_bus=new_i2c_bus,
        address=new_address,
        gain=new_gain,
        data_rate=new_data_rate,
        poll_mode=new_poll_mode
    )


if __name__ == '__main__':
    config_adc_on_click()
