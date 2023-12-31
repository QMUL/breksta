"""
Glues together all UI and Manager classes.
"""
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QGroupBox, QWidget
from ui.adc_controlpanel import ADCConfigWidget, ADCConfigManager
from ui.capture_controlpanel import CaptureControlUI, CaptureControlManager
# from device.adc_run import
from app.logger_config import setup_logger


class CentralizedControlManager(QWidget):
    """
    Central Manager class.

    Currently handling UI elements and signals.
    """
    def __init__(
            self,
            capture_ui: CaptureControlUI,
            capture_manager: CaptureControlManager,
            adc_ui: ADCConfigWidget,
            adc_manager: ADCConfigManager,
            logger
    ) -> None:
        super().__init__()
        self.logger = logger if logger else setup_logger()
        self.capture_ui = capture_ui
        self.capture_manager = capture_manager
        self.adc_ui = adc_ui
        self.adc_manager = adc_manager
        self.period = self.capture_manager.frequency

        # Connect signals to slots
        self.capture_ui.experimentStarted.connect(self.on_experiment_started)
        self.capture_ui.experimentStopped.connect(self.on_experiment_stopped)

    def on_experiment_started(self):
        # REPLACE
        channel = 0
        # Logic to handle experiment start
        self.adc_ui.setEnabled(False)
        self.logger.debug("Experiment started - ADC controls disabled.")
        adc = self.adc_manager.get_adc_config()

        with self.adc_manager.get_adc_reader(adc, channel, self.period) as reader:
            reader.run_adc()

    def on_experiment_stopped(self):
        # Logic to handle experiment stop
        self.adc_ui.setEnabled(True)
        self.logger.debug("Experiment stopped - ADC controls enabled.")

    def create_group_box_layout(self, widget, name: str) -> QGroupBox:
        """
        Creates a Vertical box layout and encapsulates it into a Group Box with a given name.
        """
        group_box = QGroupBox(name)
        group_layout = QVBoxLayout()
        group_layout.addWidget(widget)
        group_box.setLayout(group_layout)
        return group_box

    def create_layout(self, capture, adc):
        # Code to display the UI
        layout = QVBoxLayout()

        controls_group_box = self.create_group_box_layout(capture, "Controls")
        layout.addWidget(controls_group_box)

        adc_group_box = self.create_group_box_layout(adc, "ADC Settings")
        layout.addWidget(adc_group_box)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    logger = setup_logger()

    capt_ui = CaptureControlUI(logger)
    ADC_ui = ADCConfigWidget(logger)
    capt_manager = CaptureControlManager(capt_ui, logger)
    ADC_manager = ADCConfigManager(ADC_ui, logger)
    manager = CentralizedControlManager(capt_ui, capt_manager, ADC_ui, ADC_manager, logger)
    manager.create_layout(capt_ui, ADC_ui)
    manager.show()
    sys.exit(app.exec())
