"""
Module that houses all the UI element creation and initialization for signal capturing.
"""
from PySide6.QtWidgets import QWidget, QLabel, QComboBox, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit

from app.logger_config import setup_logger


class CaptureControlUI(QWidget):
    """QWidget subclass that houses all UI control elements for data capture.
    It is responsible for setting up the UI layout and elements.
    """
    DEFAULT_EXPERIMENT_NAME = "experiment-name"
    DEFAULT_EXPERIMENT_DURATION = 1  # 1 hour

    def __init__(self, logger) -> None:
        super().__init__()

        self.logger = logger if logger else setup_logger()
        self.setup_ui()

    def setup_ui(self) -> None:
        """Sets up all data capture-related UI elements, buttons, labels, text fields, and
        dropdown menus. It also configures the layout of these elements within the widget.
        """
        layout = QVBoxLayout()
        self.start_button = QPushButton('Start')
        self.stop_button = QPushButton('Stop')
        self.name_box = QLineEdit()
        self.freq_box = QComboBox()
        self.dur_box = QComboBox()

        self.setup_start_button(self.start_button, layout)
        self.setup_stop_button(self.stop_button, layout)
        self.setup_experiment_name(self.name_box, layout)
        self.setup_frequency_box(self.freq_box, layout)
        self.setup_experiment_duration_box(self.dur_box, layout)

        self.setLayout(layout)

    def setup_start_button(self, button, layout: QVBoxLayout) -> None:
        """Create Start button"""
        button.setEnabled(True)
        layout.addWidget(button)

    def setup_stop_button(self, button, layout: QVBoxLayout) -> None:
        """Create Stop button"""
        button.setEnabled(False)
        layout.addWidget(button)

    def setup_experiment_name(self, name_box, layout: QVBoxLayout) -> None:
        """Creates the Experiment Name UI element."""
        name_label = QLabel('Experiment name')
        name_box.setText(self.DEFAULT_EXPERIMENT_NAME)

        name_layout = QHBoxLayout()
        name_layout.addWidget(name_label)
        name_layout.addWidget(name_box)
        layout.addLayout(name_layout)

    def setup_frequency_box(self, freq_box, layout: QVBoxLayout) -> None:
        """Creates the capturing frequency combo box."""
        freq_label = QLabel('Frequency (s)')
        freq_box.addItems(list(map(str, (2, 4, 8, 10, 15, 30, 60, 120))))
        freq_box.setCurrentIndex(0)

        freq_layout = QHBoxLayout()
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(freq_box)
        layout.addLayout(freq_layout)

    def setup_experiment_duration_box(self, dur_box, layout: QVBoxLayout) -> None:
        """Creates the experiment duration combo box."""
        dur_label = QLabel('Experiment duration (hr)')
        dur_box.addItems(list(map(str, (1, 2, 4, 6, 8, 10, 12, 24, 36, 48, 72, 240))))
        dur_box.setCurrentIndex(0)

        dur_layout = QHBoxLayout()
        dur_layout.addWidget(dur_label)
        dur_layout.addWidget(dur_box)
        layout.addLayout(dur_layout)


class CaptureControlManager:
    """Manages the User interactions with the Capture Control UI
    elements.

    This manager class is responsible for connecting the CaptureControlUI class
    elements to logical handlers that update the settings.

    Attributes:
        capture_ui (CaptureControlUI): The associated class that
        creates the UI elements.
    """

    def __init__(self, capture_ui: CaptureControlUI, logger) -> None:
        self.logger = logger if logger is not None else setup_logger()

        self.capture_ui = capture_ui
        self.duration = int(self.capture_ui.dur_box.currentText())
        self.frequency = int(self.capture_ui.freq_box.currentText())
        self.logger.debug("Experiment duration: %sh:", self.duration)
        self.logger.debug("Signal capturing frequency: %ss", self.frequency)
        self.setup_connections()

    def setup_connections(self) -> None:
        """Establishes connections between UI elements and their event handlers.

        This method connects the change signals from the UI elements to their respective slot functions.
        Ensures the signal capture controls are updated dynamically as the user interacts with the control panel.
        """
        # Connect UI events to the corresponding methods
        self.capture_ui.start_button.clicked.connect(self.on_start_button_click)
        self.capture_ui.stop_button.clicked.connect(self.on_stop_button_click)
        self.capture_ui.freq_box.currentTextChanged.connect(self.on_frequency_change)
        self.capture_ui.dur_box.currentTextChanged.connect(self.on_duration_change)

    def on_start_button_click(self) -> None:
        """Handle user interaction with the "Start" button.

        This method is called when the user clicks the "Start" button. It disables certain
        UI components to prevent user interaction during the data capture process,
        including the "Start" button itself, the frequency selection box, the duration
        selection box, and the name input box. It also enables the "Stop" button to
        allow the user to end the data capture process.
        """
        self.logger.debug("Start button pressed")
        self.capture_ui.start_button.setEnabled(False)
        self.capture_ui.stop_button.setEnabled(True)
        self.capture_ui.freq_box.setEnabled(False)
        self.capture_ui.dur_box.setEnabled(False)
        self.capture_ui.name_box.setEnabled(False)

    def on_stop_button_click(self) -> None:
        """Handle user interaction with the "Stop" button.

        This method is called when the user clicks the "Stop" button. Enables the
        "Start" button, the frequency selection box, the duration selection box,
        and the name input box, and disables the "Stop" button.
        """
        self.logger.debug("Stop button pressed")
        self.capture_ui.stop_button.setEnabled(False)
        self.capture_ui.start_button.setEnabled(True)
        self.capture_ui.freq_box.setEnabled(True)
        self.capture_ui.dur_box.setEnabled(True)
        self.capture_ui.name_box.setEnabled(True)

    def on_duration_change(self) -> None:
        """Handle the experiment duration change."""
        self.duration = int(self.capture_ui.dur_box.currentText())
        self.logger.debug("Experiment duration changed to: %sh", self.duration)

    def on_frequency_change(self) -> None:
        """Handle the frequency change."""
        self.frequency = int(self.capture_ui.freq_box.currentText())
        self.logger.debug("Frequency changed to: %ss", self.frequency)
