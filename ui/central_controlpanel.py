"""
Glues together all UI and Manager classes.
"""
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QGroupBox, QWidget
from ui.adc_controlpanel import ADCConfigWidget, ADCConfigManager
from ui.capture_controlpanel import CaptureControlUI, CaptureControlManager
from app.logger_config import setup_logger


class CentralizedControlManager(QWidget):
    """
    Central Capture Manager class.

    This class acts as the orchestrator for the entire Capture Tab. It initializes and manages
    the UI components and their interactions, ensuring that UI changes are reflected in the
    application's behavior. It handles the starting and stopping of experiments and updates
    the ADC and capture settings based on user interactions.

    Attributes:
        capture_ui (CaptureControlUI): The UI component for capture control.
        capture_manager (CaptureControlManager): Manages the capture operations.
        adc_ui (ADCConfigWidget): The UI component for ADC configuration.
        adc_manager (ADCConfigManager): Manages ADC configurations and operations.
        logger: Used for logging events and activities within the manager.
        period (int): The frequency/period for capture operations.
    """
    DEFAULT_CHANNEL = 0

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
        self.channel = self.DEFAULT_CHANNEL

        # Connect signals to slots
        self.capture_ui.experimentStarted.connect(self.on_experiment_started)
        self.capture_ui.experimentStopped.connect(self.on_experiment_stopped)

    def on_experiment_started(self) -> None:
        """
        Handles the logic to be executed when an experiment starts.

        Disables the ADC UI to prevent configuration changes during an active experiment and
        initiates the ADC reading process based on the current configuration. This method
        ensures that the ADC reader is contextually managed to handle its lifecycle effectively
        during the experiment.
        """
        self.adc_ui.setEnabled(False)
        self.logger.debug("Experiment started - ADC controls disabled.")
        adc = self.adc_manager.get_adc_config()

        with self.adc_manager.get_adc_reader(adc, self.channel, self.period) as reader:
            reader.run_adc()

    def on_experiment_stopped(self) -> None:
        """
        Handles the necessary actions when an experiment is stopped.

        Re-enables the ADC UI to allow further configurations and prepares the system for
        subsequent experiments. This method is crucial for resetting the state of the UI
        post-experiment.
        """
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

    def create_layout(self, capture, adc) -> None:
        """Creates the final Capture tab layout, which encompasses UI elements in their own box."""
        layout = QVBoxLayout()

        controls_group_box = self.create_group_box_layout(capture, "Controls")
        layout.addWidget(controls_group_box)

        adc_group_box = self.create_group_box_layout(adc, "ADC Settings")
        layout.addWidget(adc_group_box)

        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    def_logger = setup_logger()

    capt_ui = CaptureControlUI(def_logger)
    ADC_ui = ADCConfigWidget(def_logger)
    capt_manager = CaptureControlManager(capt_ui, def_logger)
    ADC_manager = ADCConfigManager(ADC_ui, def_logger)
    manager = CentralizedControlManager(capt_ui, capt_manager, ADC_ui, ADC_manager, def_logger)
    manager.create_layout(capt_ui, ADC_ui)
    manager.show()
    sys.exit(app.exec())
