import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from ui.capture_controlpanel import CaptureControlUI, CaptureControlManager
from app.logger_config import setup_logger


class TestWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.logger = setup_logger()
        self.setupUI()

    def setupUI(self) -> None:
        layout = QVBoxLayout(self)
        self.capture_config_widget = CaptureControlUI(self.logger)
        self.capture_manager = CaptureControlManager(self.capture_config_widget, self.logger)
        layout.addWidget(self.capture_config_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    testWindow = TestWindow()
    testWindow.show()
    sys.exit(app.exec())
