"""Encapsulates the ADC-related GUI functionality
"""
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QRadioButton, QVBoxLayout

from app.logger_config import setup_logger
from device.adc_config import ADS1115Address as Address, ADS1115Gain as Gain, ADS1115DataRate as DR


class ADCConfigWidget(QWidget):
    """Handles the creation and initialization of the ADC configuration UI elements.
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.logger = setup_logger()
        self.address_combo = None
        self.data_rate_combo = None
        self.polling_mode_single = None
        self.polling_mode_continuous = None
        self.gain_combo = None

        self.setup_ui()

    def setup_ui(self) -> None:
        """Creates the layout and the elements, then binds them together.
        """
        layout = QVBoxLayout(self)

        self.setup_bus_label(layout)
        self.setup_address_combo(layout)
        self.setup_gain_combo(layout)
        self.setup_polling_mode(layout)
        self.setup_data_rate(layout)

        self.logging_setup()

    def logging_setup(self) -> None:
        """Helper to house all logging."""
        self.logger.debug("Setting up ADC control panel UI elements and values:")
        self.logger.debug("Address: %s", self.address_combo.currentText())

    def setup_bus_label(self, layout: QVBoxLayout) -> None:
        """Creates the Bus fixed text element."""
        bus_label = QLabel("Bus: 1")
        layout.addWidget(bus_label)

    def setup_address_combo(self, layout: QVBoxLayout) -> None:
        """Creates the Address combo text element.
        Uses the ADS1115 class to populate the values."""
        address_label = QLabel("Address:")
        self.address_combo = QComboBox()

        for address in [
            Address.GND,
            Address.VDD,
            Address.SDA,
            Address.SCL
        ]:
            self.address_combo.addItem(f"0x{address:X}", address)

        # Hard-set the default value
        self.address_combo.setCurrentIndex(0)

        layout.addWidget(address_label)
        layout.addWidget(self.address_combo)

    def setup_gain_combo(self, layout: QVBoxLayout) -> None:
        """Creates the Gain combo text element.
        Uses the ADS1115 class to populate the values."""
        gain_label = QLabel("Gain:")
        self.gain_combo = QComboBox()

        # Mapping of gain constants to descriptive strings
        gain_mapping: dict[int, str] = {
            Gain.PGA_6_144V: "±6.144V (Default)",
            Gain.PGA_4_096V: "±4.096V",
            Gain.PGA_2_048V: "±2.048V",
            Gain.PGA_1_024V: "±1.024V",
            Gain.PGA_0_512V: "±0.512V",
            Gain.PGA_0_256V: "±0.256V"
        }

        for gain_value, gain_text in gain_mapping.items():
            self.gain_combo.addItem(gain_text, gain_value)

        # Hard-set the default value
        self.gain_combo.setCurrentIndex(0)

        layout.addWidget(gain_label)
        layout.addWidget(self.gain_combo)

    def setup_data_rate(self, layout: QVBoxLayout) -> None:
        """Creates the Data Rate combo box element.
        Uses the ADS1115 class to populate the values."""
        self.data_rate_combo = QComboBox()

        # Mapping of data rate values to descriptive strings
        data_rate_mapping: dict[int, str] = {
            DR.DR_ADS111X_8: "8 SPS (Slowest)",
            DR.DR_ADS111X_16: "16 SPS",
            DR.DR_ADS111X_32: "32 SPS",
            DR.DR_ADS111X_64: "64 SPS",
            DR.DR_ADS111X_128: "128 SPS (Default)",
            DR.DR_ADS111X_250: "250 SPS",
            DR.DR_ADS111X_475: "475 SPS",
            DR.DR_ADS111X_860: "860 SPS (Fastest)"
        }

        for data_rate_value, data_rate_text in data_rate_mapping.items():
            self.data_rate_combo.addItem(data_rate_text, data_rate_value)

        # Hard-set the default value
        self.data_rate_combo.setCurrentIndex(4)

        self.data_rate_combo.setEnabled(False)
        layout.addWidget(QLabel("Data Rate:"))
        layout.addWidget(self.data_rate_combo)

    def setup_polling_mode(self, layout: QVBoxLayout) -> None:
        """Creates the Polling mode Radio buttons elements.
        Uses the ADS1115 class to populate the values."""
        self.polling_mode_single = QRadioButton("Single-shot Operation")
        self.polling_mode_continuous = QRadioButton("Continuous Operation")
        self.polling_mode_single.setChecked(True)  # Default to Single-Shot
        layout.addWidget(QLabel("Polling Mode:"))
        layout.addWidget(self.polling_mode_single)
        layout.addWidget(self.polling_mode_continuous)

    def get_config_values(self):
        return {
            "address": self.address_combo.currentText(),
            "gain": self.gain_combo.currentText(),
            "data_rate": self.data_rate_combo.currentText(),
            "polling_mode": self.polling_mode_single.isChecked()
        }
