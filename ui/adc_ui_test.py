import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from ui.adc_controlpanel import ADCConfigWidget, ADCConfigManager
from app.logger_config import setup_logger


class TestWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.logger = setup_logger()
        self.setupUI()

    def setupUI(self) -> None:
        layout = QVBoxLayout(self)
        self.adc_config_widget = ADCConfigWidget(self.logger)
        self.adc_config_manager = ADCConfigManager(self.adc_config_widget, self.logger)
        layout.addWidget(self.adc_config_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    testWindow = TestWindow()
    testWindow.show()
    sys.exit(app.exec())
