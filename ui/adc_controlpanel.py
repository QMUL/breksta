"""Encapsulates the ADC-related GUI functionality
"""
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QRadioButton, QVBoxLayout

from app.logger_config import setup_logger
from device.adc_config import ADS1115Address as Address, ADS1115Gain as Gain


class ADCConfigWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setup_ui()
        self.logger = setup_logger()

    def setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        self.setup_bus_label(layout)
        self.setup_address_combo(layout)
        self.setup_gain_combo(layout)

        # Data Rate - Dropdown
        self.data_rate_combo = QComboBox()
        self.data_rate_combo.addItems(['8 SPS', '16 SPS', '32 SPS', '64 SPS'])
        layout.addWidget(QLabel("Data Rate:"))
        layout.addWidget(self.data_rate_combo)

        # Polling Mode - Binary Choice using Radio Buttons
        self.polling_mode_single = QRadioButton("Single-shot Operation")
        self.polling_mode_continuous = QRadioButton("Continuous Operation")
        self.polling_mode_single.setChecked(True)  # Default to Single-Shot
        layout.addWidget(QLabel("Polling Mode:"))
        layout.addWidget(self.polling_mode_single)
        layout.addWidget(self.polling_mode_continuous)

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

        layout.addWidget(gain_label)
        layout.addWidget(self.gain_combo)

    def get_config_values(self):
        return {
            "address": self.address_combo.currentText(),
            "gain": self.gain_combo.currentText(),
            "data_rate": self.data_rate_combo.currentText(),
            "polling_mode": self.polling_mode_single.isChecked()
        }
