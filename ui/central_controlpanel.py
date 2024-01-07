"""
Glues together all UI and Manager classes for the Capture Tab.
"""
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from ui.adc_controlpanel import ADCConfigWidget, ADCConfigManager
from ui.capture_controlpanel import CaptureControlUI, CaptureControlManager
from ui.layout import create_group_box
from ui.chart_manager import start_chart_process as start_chart, stop_chart_process as stop_chart
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
        self.channel = self.DEFAULT_CHANNEL

        self.create_layout(self.capture_ui, self.adc_ui)
        self.setup_connections()

    def setup_connections(self) -> None:
        """Connect signals to slots"""
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
        # Start/resume charting
        start_chart(self.logger)

        # Handle ADC-related logic
        self.adc_ui.setEnabled(False)
        self.logger.debug("Experiment started - ADC controls disabled.")
        adc = self.adc_manager.get_adc_config()
        period: int = self.capture_manager.frequency
        self.reader = self.adc_manager.get_adc_reader(adc, self.channel, period)
        # with self.adc_manager.get_adc_reader(adc, self.channel, period) as reader:
        self.capture_manager.sampling_timer.timeout.connect(self.reader.run_adc)
        self.capture_manager.set_timer(
            self.capture_manager.sampling_timer,
            period
        )

    def on_experiment_stopped(self) -> None:
        """
        Handles the necessary actions when an experiment is stopped.

        Re-enables the ADC UI to allow further configurations and prepares the system for
        subsequent experiments. This method is crucial for resetting the state of the UI
        post-experiment.
        """
        # Stop charting
        stop_chart(self.logger)

        # Handle ADC-related logic
        self.adc_ui.setEnabled(True)
        self.logger.debug("Experiment stopped - ADC controls enabled.")
        self.capture_manager.sampling_timer.stop()

    def create_layout(self, capture, adc) -> None:
        """Creates the final Capture tab layout, which encompasses UI elements in their own box."""
        layout = QVBoxLayout()

        controls_group_box = create_group_box(capture, "Controls")
        layout.addWidget(controls_group_box)

        adc_group_box = create_group_box(adc, "ADC Settings")
        layout.addWidget(adc_group_box)

        self.setLayout(layout)


def get_manager_instance(logger) -> CentralizedControlManager:
    """Instantiates all dependencies, injects them, and returns the Central instance."""
    capt_ui = CaptureControlUI(logger)
    adc_ui = ADCConfigWidget(logger)
    capt_manager = CaptureControlManager(capt_ui, logger)
    adc_manager = ADCConfigManager(adc_ui, logger)
    return CentralizedControlManager(capt_ui, capt_manager, adc_ui, adc_manager, logger)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    _logger = setup_logger()

    window: CentralizedControlManager = get_manager_instance(_logger)
    window.show()
    sys.exit(app.exec())
