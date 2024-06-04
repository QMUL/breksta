"""Encapsulates the ADC-related GUI functionality.

Includes:
- creating and initializing the ADC configuration UI elements,
- connecting the UI elements with their event handlers
- creating the ADC configuration object
- selecting the ADC reading operation mode
"""

import os

from PySide6.QtWidgets import QButtonGroup, QComboBox, QLabel, QRadioButton, QVBoxLayout, QWidget

from app.logger_config import setup_logger
from app.sine_wave_generator import SineWaveGenerator
from device.adc_config import ADCConfig
from device.adc_config import ADS1115Address as Address
from device.adc_config import ADS1115DataRate as DR
from device.adc_config import ADS1115Gain as Gain
from device.adc_config import ADS1115Mode as Mode
from device.adc_run import ADCReader, ContinuousADCReader, SingleShotADCReader
from ui.layout import create_horizontal_box


class ADCConfigWidget(QWidget):
    """Handles the creation and initialization of the ADC configuration UI elements."""

    BUS = 1
    ADDRESS_DEFAULT = Address.GND
    GAIN_DEFAULT = Gain.PGA_6_144V
    MODE_DEFAULT = Mode.poll_mode_single
    DATA_RATE_DEFAULT = DR.DR_ADS111X_128

    def __init__(self, logger, parent=None) -> None:
        super().__init__(parent)
        self.logger = logger if logger is not None else setup_logger()

        self.setup_ui()  # Directly call the setup_ui method to initialize UI components

    def setup_ui(self) -> None:
        """Creates the box layout, then creates the UI elements and adds them to the layout."""
        layout = QVBoxLayout(self)
        self.address_combo = QComboBox()
        self.gain_combo = QComboBox()
        self.data_rate_combo = QComboBox()
        self.polling_mode_group = QButtonGroup()
        self.logger.debug("Setting up ADC control panel UI elements and values:")

        self.setup_bus_label(layout)
        self.setup_address_combo(layout)
        self.setup_gain_combo(layout)
        self.setup_polling_mode(layout)
        self.setup_data_rate(layout)

    def setup_bus_label(self, layout: QVBoxLayout) -> None:
        """Creates the Bus fixed text element."""
        bus_label = QLabel("Bus: 1")
        layout.addWidget(bus_label)

    def setup_address_combo(self, layout: QVBoxLayout) -> None:
        """Creates the Address combo text element.
        Uses the ADS1115 class to populate the values."""
        address_label = QLabel("Address:")

        # Mapping of addresses to descriptive strings
        address_mapping: dict[int, str] = {Address.GND: "GND", Address.VDD: "VDD", Address.SDA: "SDA", Address.SCL: "SCL"}

        for index, (address, description) in enumerate(address_mapping.items()):
            self.address_combo.addItem(f"0x{address:X} ({description})", address)
            if address == self.ADDRESS_DEFAULT:
                self.address_combo.setCurrentIndex(index)

        self.logger.debug("Address: %s", self.address_combo.currentText())

        # Add label and UI element in Horizontal box
        box = create_horizontal_box(self.address_combo, address_label)
        layout.addLayout(box)

    def setup_gain_combo(self, layout: QVBoxLayout) -> None:
        """Creates the Gain combo text element.
        Uses the ADS1115 class to populate the values."""
        gain_label = QLabel("Gain:")

        # Mapping of gain constants to descriptive strings
        gain_mapping: dict[int, str] = {
            Gain.PGA_6_144V: "±6.144V (Default)",
            Gain.PGA_4_096V: "±4.096V",
            Gain.PGA_2_048V: "±2.048V",
            Gain.PGA_1_024V: "±1.024V",
            Gain.PGA_0_512V: "±0.512V",
            Gain.PGA_0_256V: "±0.256V",
        }

        for index, (gain_value, gain_text) in enumerate(gain_mapping.items()):
            self.gain_combo.addItem(gain_text, gain_value)
            if gain_value == self.GAIN_DEFAULT:
                self.gain_combo.setCurrentIndex(index)

        self.logger.debug("Gain: %s", self.gain_combo.currentText())

        # Add label and UI element in Horizontal box
        box = create_horizontal_box(self.gain_combo, gain_label)
        layout.addLayout(box)

    def setup_data_rate(self, layout: QVBoxLayout) -> None:
        """Creates the Data Rate combo box element.
        Uses the ADS1115 class to populate the values."""
        data_rate_label = QLabel("Data Rate:")

        # Mapping of data rate values to descriptive strings
        data_rate_mapping: dict[int, str] = {
            DR.DR_ADS111X_8: "8 SPS (Slowest)",
            DR.DR_ADS111X_16: "16 SPS",
            DR.DR_ADS111X_32: "32 SPS",
            DR.DR_ADS111X_64: "64 SPS",
            DR.DR_ADS111X_128: "128 SPS (Default)",
            DR.DR_ADS111X_250: "250 SPS",
            DR.DR_ADS111X_475: "475 SPS",
            DR.DR_ADS111X_860: "860 SPS (Fastest)",
        }

        for index, (data_rate_value, data_rate_text) in enumerate(data_rate_mapping.items()):
            self.data_rate_combo.addItem(data_rate_text, data_rate_value)
            if data_rate_value == self.DATA_RATE_DEFAULT:
                self.data_rate_combo.setCurrentIndex(index)

        self.data_rate_combo.setEnabled(False)
        self.logger.debug("Data Rate: %s", self.data_rate_combo.currentText())

        # Add label and UI element in Horizontal box
        box = create_horizontal_box(self.data_rate_combo, data_rate_label)
        layout.addLayout(box)

    def setup_polling_mode(self, layout: QVBoxLayout) -> None:
        """Creates the Polling mode Radio buttons elements."""
        # Create radio buttons
        polling_mode_single = QRadioButton("Single-shot Operation")
        polling_mode_continuous = QRadioButton("Continuous Operation")

        # Add radio buttons to the group with Enums as IDs
        self.polling_mode_group.addButton(polling_mode_single, Mode.poll_mode_single.value)
        self.polling_mode_group.addButton(polling_mode_continuous, Mode.poll_mode_continuous.value)

        self.polling_mode_group.button(self.MODE_DEFAULT.value).setChecked(True)

        # Add radio buttons to the layout
        layout.addWidget(QLabel("Polling Mode:"))
        layout.addWidget(polling_mode_single)
        layout.addWidget(polling_mode_continuous)
        self.logger.debug("Polling: %s", self.polling_mode_group.checkedButton().text())


class ADCConfigManager:
    """Manages the configuration interactions for an ADCConfigWidget instance.

    This manager class is responsible for connecting the ADCConfigWidget user interface elements
    to logical handlers that update the ADC configuration settings.

    Attributes:
        config_widget (ADCConfigWidget): The associated class that creates the UI elements.
    """

    def __init__(self, config_widget: ADCConfigWidget, logger) -> None:
        self.logger = logger if logger is not None else setup_logger()

        self.config_widget = config_widget

        self.address = self.config_widget.address_combo.itemData(self.config_widget.address_combo.currentIndex())
        self.gain = self.config_widget.gain_combo.itemData(self.config_widget.gain_combo.currentIndex())
        self.data_rate = self.config_widget.data_rate_combo.itemData(self.config_widget.data_rate_combo.currentIndex())
        polling_mode_id = self.config_widget.polling_mode_group.checkedId()
        self.polling_mode = Mode(polling_mode_id)  # Convert to Mode enum

        self.setup_connections()

    def setup_connections(self) -> None:
        """Establish connections between UI elements and their event handlers.

        This method connects the change signals from the UI elements to their respective slot functions.
        Ensures the ADC configuration is updated dynamically as the user interacts with the control panel.
        """
        self.config_widget.address_combo.currentIndexChanged.connect(self.on_address_change)
        self.config_widget.gain_combo.currentIndexChanged.connect(self.on_gain_change)
        self.config_widget.data_rate_combo.currentIndexChanged.connect(self.on_data_rate_change)
        # Connect the button group's 'idToggled' signal to the handler
        self.config_widget.polling_mode_group.idToggled.connect(self.on_polling_mode_change)

    def on_address_change(self, index: int) -> None:
        """Handle the address change"""
        self.address = self.config_widget.address_combo.itemData(index)
        self.logger.debug("Address changed to: 0x%X", self.address)

    def on_gain_change(self, index: int) -> None:
        """Handle the gain change"""
        self.gain = self.config_widget.gain_combo.itemData(index)
        self.logger.debug("Gain changed to: %s", self.gain)

    def on_data_rate_change(self, index: int) -> None:
        """Handle the gain change"""
        self.data_rate = self.config_widget.data_rate_combo.itemData(index)
        self.logger.debug("Data Rate changed to: %s", self.data_rate)

    def on_polling_mode_change(self, button_id, checked) -> None:
        """Adjust the ADC configuration based on the selected polling mode.

        Enables or disables the data rate configuration based on the selected mode. Single-shot operation
        does not require a data rate, hence the associated control is disabled to reflect this dependency.

        Args:
            button_id: The identifier of the radio button that triggered the event.
            checked: A boolean indicating whether the radio button is checked.
        """
        mode: str = "Error in radio button."
        # Only act on the signal when a button is checked, not unchecked
        if checked:
            if button_id == Mode.poll_mode_single.value:
                mode = "Single-shot Operation"
                self.config_widget.data_rate_combo.setEnabled(False)
            elif button_id == Mode.poll_mode_continuous.value:
                mode = "Continuous Operation"
                self.config_widget.data_rate_combo.setEnabled(True)
            self.logger.debug("Polling Mode changed to: %s", mode)

            polling_mode_id: int = self.config_widget.polling_mode_group.checkedId()
            self.polling_mode = Mode(polling_mode_id)  # Convert to Mode enum

    def get_adc_config(self) -> ADCConfig:
        """Extract the current ADC configuration values from the UI."""

        config = ADCConfig(
            i2c_bus=self.config_widget.BUS,
            address=self.address,
            gain=self.gain,
            data_rate=self.data_rate,
            poll_mode=self.polling_mode,
        )

        self.logger.debug("Pushing ADC Configuration: %s", config)
        return config

    def get_adc_reader(self, config: ADCConfig, channel: int, period: int) -> ADCReader:
        """Selects the appropriate ADC Reader object, according to the operation mode."""
        self.logger.debug("Selecting ADC Reader for %s operation", config.poll_mode)

        match config.poll_mode:
            case Mode.poll_mode_single:
                return SingleShotADCReader(config, channel, period, self.logger)
            case Mode.poll_mode_continuous:
                return ContinuousADCReader(config, channel, period, self.logger)
            case _:
                raise ValueError(f"Invalid ADC mode: {config.poll_mode}")

    def get_device(self, config, channel, period) -> ADCReader:
        """Wrapper method to select between real and mock ADC Readers based on application context."""

        if os.getenv("USE_MOCK_DEVICE", "0") == "1":
            self.logger.info("Using Mock Sine Wave Generator for testing")
            return SineWaveGenerator(config, channel, period, self.logger)

        # Use the existing helper to get the ADC
        return self.get_adc_reader(config, channel, period)
