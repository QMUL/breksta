"""Module for manual inspection of the Capture control UI elements."""

import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from app.logger_config import setup_logger
from ui.auxillary_devices_ui import AmplifierConfig, PotentiometerConfig


class TestWindow(QWidget):
    """Test harness class for manual inspection of Capture Control UI elements."""

    def __init__(self) -> None:
        super().__init__()
        self.logger = setup_logger()
        self.setup_ui()

    def setup_ui(self) -> None:
        """Creates and applies the layout."""
        layout = QVBoxLayout(self)
        self.amplifier = AmplifierConfig(self.logger)
        layout.addWidget(self.amplifier)
        self.potentiometer = PotentiometerConfig(self.logger)
        layout.addWidget(self.potentiometer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    testWindow = TestWindow()
    testWindow.show()

    print("Amplifier slider value:", testWindow.amplifier.get_slider_value())
    print("Potentiometer slider value:", testWindow.potentiometer.get_slider_value())

    sys.exit(app.exec())
