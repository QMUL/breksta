"""
Glues together all UI and Manager classes for the Capture Tab.
"""
import sys
from typing import Optional
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget
from PySide6.QtCore import Signal, Slot, Qt
from app.logger_config import Logger
from device.adc_run import ADCReader
from ui.adc_controlpanel import ADCConfigWidget, ADCConfigManager
from ui.capture_controlpanel import CaptureControlUI, CaptureControlManager
from ui.layout import create_group_box
from ui.chart_manager import start_chart_process as start_chart, stop_chart_process as stop_chart


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
    output_signal = Signal(float)

    def __init__(
            self,
            capture_ui: CaptureControlUI,
            capture_manager: CaptureControlManager,
            adc_ui: ADCConfigWidget,
            adc_manager: ADCConfigManager,
            logger
    ) -> None:
        super().__init__()
        self.logger = logger  # if logger else setup_logger()
        self.capture_ui = capture_ui
        self.capture_manager = capture_manager
        self.adc_ui = adc_ui
        self.adc_manager = adc_manager
        self.channel = self.DEFAULT_CHANNEL
        self.adc_reader: Optional[ADCReader] = None
        self.timer = self.capture_manager.sampling_timer

        self.create_layout(self.capture_ui, self.adc_ui)
        self.setup_connections()

    def setup_connections(self) -> None:
        """Connect signals to slots"""
        self.capture_ui.start_button_signal.connect(self.on_experiment_started, Qt.ConnectionType.QueuedConnection)
        self.capture_ui.stop_button_signal.connect(self.on_experiment_stopped, Qt.ConnectionType.QueuedConnection)

    @Slot()
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

        # Handle ADC-related logic. Get a valid config, push it to ADC, initialize ADC, choose Reader
        self.adc_ui.setEnabled(False)
        self.logger.debug("Experiment started - ADC controls disabled.")
        adc_config = self.adc_manager.get_adc_config()
        period: int = self.capture_manager.frequency

        self.adc_reader = self.adc_manager.get_device(adc_config, self.channel, period)

        if self.adc_reader.adc is None:
            # Failure cascading - STOP the experiment
            self.logger.error("Stopping the experiment...")
            self.capture_ui.stop_button.click()
            return

        self.start_reading(self.adc_reader, self.timer, period)

    @Slot()
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
        self.timer.stop()
        if self.adc_reader.adc is not None:
            self.timer.timeout.disconnect()

    def start_reading(self, adc_reader, timer, period) -> None:
        """Checks the ADC is initialized successfully and starts the timer."""
        if adc_reader.is_operational():

            def on_timeout() -> None:
                result: float = adc_reader.run_adc()
                self.output_signal.emit(result)

            timer.timeout.connect(on_timeout)
            timer.start(period * 1000)

    def create_layout(self, capture, adc) -> None:
        """Creates the final Capture tab layout, which encompasses UI elements in their own box."""
        layout = QVBoxLayout()

        controls_group_box = create_group_box(capture, "Controls")
        layout.addWidget(controls_group_box)

        adc_group_box = create_group_box(adc, "ADC Settings")
        layout.addWidget(adc_group_box)
        layout.addStretch()

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
    _logger = Logger.get_instance()

    window: CentralizedControlManager = get_manager_instance(_logger)
    window.show()
    sys.exit(app.exec())
