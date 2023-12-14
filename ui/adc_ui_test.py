import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout
from ui.adc_controlpanel import ADCConfigWidget


class TestWindow(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setupUI()

    def setupUI(self) -> None:
        layout = QVBoxLayout(self)
        self.adc_configWidget = ADCConfigWidget()
        layout.addWidget(self.adc_configWidget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    testWindow = TestWindow()
    testWindow.show()
    sys.exit(app.exec())
