"""
Module handles UI elements for the auxillary devices:
- potentiometer MCP4551
- amplifier
Current understanding:
Both devices will be initialized before the ADC.
The potentiometer is handling Voltage Control of the Photodetector
The amplifier?
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSlider, QVBoxLayout, QWidget


class DeviceConfigBase(QWidget):
    """Base class for all device configurations."""

    def __init__(self, logger, device_name) -> None:
        super().__init__()

        self.logger = logger
        self.device_name = device_name
        self.setup_ui()

    def setup_ui(self) -> None:
        """Creates the box layout, then creates the UI elements and adds them to the layout."""
        layout = QVBoxLayout(self)
        title = QLabel(f"{self.device_name} controls")
        layout.addWidget(title)
        self.setup_device_control(layout)

    def setup_device_control(self, layout: QVBoxLayout) -> None:
        """Override this method in subclasses to create specific device controls."""
        raise NotImplementedError("This method should be overridden in subclasses")

    def add_slider_with_labels(self, layout: QVBoxLayout, name: str, min_val: int, max_val: int, tick_interval: int):
        """Helper method to add a slider with labels for start, end, and increments."""
        slider_layout = QVBoxLayout()

        label = QLabel(name)
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_val)
        slider.setMaximum(max_val)
        slider.setValue((max_val + min_val) // 2)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setTickInterval(tick_interval)

        start_label = QLabel(str(min_val))
        end_label = QLabel(str(max_val))
        current_value_label = QLabel(str(slider.value()))

        def update_label(value) -> None:
            current_value_label.setText(str(value))

        slider.valueChanged.connect(update_label)
        slider_layout.addWidget(label)
        slider_layout.addWidget(slider)

        tick_layout = QHBoxLayout()
        tick_layout.addWidget(start_label)
        tick_layout.addStretch()
        tick_layout.addWidget(current_value_label)
        tick_layout.addStretch()
        tick_layout.addWidget(end_label)

        slider_layout.addLayout(tick_layout)
        layout.addLayout(slider_layout)


class AmplifierConfig(DeviceConfigBase):
    """Houses all UI elements for the amplifier."""

    def __init__(self, logger) -> None:
        super().__init__(logger, "Amplifier")

    def setup_device_control(self, layout: QVBoxLayout) -> None:
        """Create the UI elements to control the amplifier."""
        self.add_slider_with_labels(layout, "Gain", 0, 100, 10)


class PotentiometerConfig(DeviceConfigBase):
    """Houses all UI elements for the potentiometer."""

    def __init__(self, logger) -> None:
        super().__init__(logger, "Potentiometer")

    def setup_device_control(self, layout: QVBoxLayout) -> None:
        """Create the UI elements to control the potentiometer."""
        self.add_slider_with_labels(layout, "Resistance", 0, 100, 10)
