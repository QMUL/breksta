"""Module for manual inspection of the Capture control UI elements."""
import sys

from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget

from app.logger_config import setup_logger
from ui.capture_controlpanel import CaptureControlManager, CaptureControlUI


class TestWindow(QWidget):
    """Test harness class for manual inspection of Capture Control UI elements."""

    def __init__(self) -> None:
        super().__init__()
        self.logger = setup_logger()
        self.setup_ui()

    def setup_ui(self) -> None:
        """Creates and applies the layout."""
        layout = QVBoxLayout(self)
        self.capture_config_widget = CaptureControlUI(self.logger)
        self.capture_manager = CaptureControlManager(self.capture_config_widget, self.logger)
        layout.addWidget(self.capture_config_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    testWindow = TestWindow()
    testWindow.show()
    sys.exit(app.exec())
