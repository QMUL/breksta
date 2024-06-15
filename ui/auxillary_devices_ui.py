"""
Module handles UI elements for the auxillary devices:
- potentiometer MCP4551
- amplifier
Current understanding:
Both devices will be initialized before the ADC.
The potentiometer is handling Voltage Control of the Photodetector
The amplifier?
"""

from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget  # QComboBox, QLabel, QLineEdit, QPushButton


class AmplifierConfig(QWidget):
    """Houses all UI elements for the amplifier."""

    def __init__(self, logger) -> None:
        super().__init__()

        self.logger = logger
        self.setup_ui()

    def setup_ui(self) -> None:
        """Creates the box layout, then creates the UI elements and adds them to the layout."""
        layout = QVBoxLayout(self)
        self.setup_device_control(layout)

    def setup_device_control(self, layout: QVBoxLayout) -> None:
        """Create the UI element to control the amplifier."""
        element = QLabel("Amplifier controls")
        layout.addWidget(element)


class PotentiometerConfig(QWidget):
    """Houses all UI elements for the potentiometer."""

    def __init__(self, logger) -> None:
        super().__init__()

        self.logger = logger
        self.setup_ui()

    def setup_ui(self) -> None:
        """Creates the box layout, then creates the UI elements and adds them to the layout."""
        layout = QVBoxLayout(self)
        self.setup_device_control(layout)

    def setup_device_control(self, layout: QVBoxLayout) -> None:
        """Create the UI element to control the amplifier."""
        element = QLabel("Potentiometer controls")
        layout.addWidget(element)
