"""Manual inspection module for the creation and instantiation of Capture tab UI elements."""

import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from app.logger_config import setup_logger
from ui.adc_controlpanel import ADCConfigManager, ADCConfigWidget
from ui.capture_controlpanel import CaptureControlManager, CaptureControlUI
from ui.layout import create_group_box


class TestWindow(QWidget):
    """Test harness class for manual inspection of the Capture tab UI elements."""

    def __init__(self) -> None:
        super().__init__()
        self.logger = setup_logger()
        self.capture_control = CaptureControlUI(self.logger)
        self.capture_manager = CaptureControlManager(self.capture_control, self.logger)
        self.adc_config_widget = ADCConfigWidget(self.logger)
        self.adc_config_manager = ADCConfigManager(self.adc_config_widget, self.logger)
        self.setup_ui()
        self.config = self.adc_config_manager.get_adc_config()

    def setup_ui_adc(self) -> None:
        """Creates the ADC UI interface only. Has to be explicitly called."""
        layout = QVBoxLayout(self)
        layout.addWidget(self.adc_config_widget)

    def setup_ui(self) -> None:
        """
        Creates the Unified UI interface.

        - Create a vertical box layout
        - Create a group box that encapsulates a vertical box layout for general "Controls"
        - Create a group box that encapsulates a vertical box layout for "ADC Settings"
        """
        layout = QVBoxLayout()

        controls_group_box = create_group_box(self.capture_control, "Controls")
        layout.addWidget(controls_group_box)

        adc_group_box = create_group_box(self.adc_config_widget, "ADC Settings")
        layout.addWidget(adc_group_box)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    testWindow = TestWindow()
    testWindow.show()
    sys.exit(app.exec())
