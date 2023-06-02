

import sys

from PySide6.QtCore import QProcess, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget)
from PySide6.QtWebEngineWidgets import QWebEngineView

from capture import DevCapture
from capture import PmtDb

class CaptureControl(QWidget):
    '''
    Widget with all the controls for data capture.
    See the example at:
        https://doc.qt.io/qtforpython/PySide6/QtCore/Signal.html

    '''

    # external signal for the slot in the ChartWidget
    started = Signal(int)

    def __init__(self):

        QWidget.__init__(self)

        self.experiment_id = None

        self.sample_frequency = 2
        self.duration = 1

        self.device = DevCapture()
        # https://doc.qt.io/qtforpython/PySide6/QtCore/QTimer.html
        self.sample_timer = QTimer()
        # Here, the repeating timer provokes the data capture:
        self.sample_timer.timeout.connect(self.device.take_reading)

        # https://www.pythonguis.com/tutorials/pyside6-layouts/
        # https://doc.qt.io/qtforpython/overviews/layout.html
        layout = QVBoxLayout()

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start)
        layout.addWidget(self.start_button)

        self.stop_button = QPushButton('Stop')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop)
        layout.addWidget(self.stop_button)

        # https://doc.qt.io/qtforpython/PySide6/QtWidgets/QLineEdit.html
        name_label = QLabel('experiment name')
        self.name_box = QLineEdit()
        self.name_box.setText('experiment_1')
        name_layout = QHBoxLayout()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_box)
        layout.addLayout(name_layout)

        freq_label = QLabel('sample frequency (s)')
        self.freq_box = QComboBox()
        self.freq_box.addItems(list(map(str, (2, 4, 8, 10, 15, 30, 60, 120))))
        self.freq_box.currentTextChanged.connect(self.set_freq)
        freq_layout = QHBoxLayout()
        freq_layout.addWidget(freq_label)
        freq_layout.addWidget(self.freq_box)
        layout.addLayout(freq_layout)

        dur_label = QLabel('experiment duration (hr)')
        self.dur_box = QComboBox()
        self.dur_box.addItems(list(map(str, (1, 2, 4, 6, 8, 10, 12, 24, 36, 48))))
        dur_layout = QHBoxLayout()
        dur_layout.addWidget(dur_label)
        dur_layout.addWidget(self.dur_box)
        layout.addLayout(dur_layout)

        self.setLayout(layout)

    def start(self):
        self.start_button.setEnabled(False)
        self.experiment_id = self.device.start_experiment(self.name_box.text())
        self.device.take_reading()
        self.sample_timer.start(1000 * self.sample_frequency)
        # signal to the ChartWidget is sent here:
        self.started.emit(self.experiment_id)
        self.stop_button.setEnabled(True)

    def stop(self):
        self.stop_button.setEnabled(False)
        self.device.stop_experiment()
        self.sample_timer.stop()
        # What should the ChartWidget display when capture stops?
        # TODO: Send another signal here:
        self.experiment_id = None
        self.start_button.setEnabled(True)

    def set_freq(self, txt):
        self.sample_frequency = int(txt)
        # TODO Tidy away DEBUG prints, use a propper Python logger.
        # Set log-level from an Env Var?
        # Detect if we're running a Pi?
        print(self.sample_frequency)


class ChartWidget(QWebEngineView):
    '''
    Sub-classed WebView:
        https://doc.qt.io/qt-6/webengine-widgetexamples.html
    Probably want to sub-class from QWidget, embded the Web#view in a
    layout with some more native UI to control scaling, etc...

    '''
    def __init__(self):


        QWebEngineView.__init__(self)

    '''
    Slot to receive the started signal from CaptureControl.
    Could pass the experiment ID as a parameter to the web app.
    https://doc.qt.io/qtforpython/PySide6/QtCore/Slot.html
    '''
    @Slot(int)
    def plot_experiment(self, experiment):
        url = QUrl('http://localhost:8050/')
        self.load(url)


class CaptureWidget(QWidget):
    '''
    Stick the capture and chart widgets in a parent layout.
    '''
    def __init__(self, width):

        QWidget.__init__(self)

        layout = QHBoxLayout()

        # Partition the window real-estate how thou wilt:

        controls = CaptureControl()
        controls.setFixedWidth(int(0.25 * width))

        chart = ChartWidget()
        chart.setFixedWidth(int(0.75 * width))

        # Signal from the controls to the chart routed here.
        # Helps avoid a hideous God Object.
        controls.started.connect(chart.plot_experiment)

        layout.addWidget(controls)
        layout.addWidget(chart)

        self.setLayout(layout)


class ExportWidget(QWidget):

    def __init__(self, width):

        QWidget.__init__(self)

        layout = QHBoxLayout()

        self.export_button = QPushButton("Export", self)
        self.export_button.clicked.connect(self.on_export_button_clicked)

        self.export_button.setFixedWidth(int(0.25 * width))
        self.export_button.setEnabled(True)

        layout.addWidget(self.export_button)

        self.setLayout(layout)

    def on_export_button_clicked(self):
        # Disable button upon clicking. Acknowledge.
        self.export_button.setEnabled(False)
        print("Export button clicked. Exporting in progress...")

        # Initialize the database connection
        db = PmtDb()

        # Export the data
        db.export_data()

        print("Export complete!")
        self.export_button.setEnabled(True)

# https://doc.qt.io/qtforpython/tutorials/datavisualize/
class MainWindow(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        # Launch the plotly/dash web-app in here:
        self.web_process = QProcess()

        self.setWindowTitle("Breksta")

        geometry = self.screen().availableGeometry()

        win_width = int(geometry.width() * 0.95)
        win_height = int(geometry.height() * 0.95)

        self.setFixedSize(win_width, win_height)

        capture = CaptureWidget(win_width)
        export = ExportWidget(win_width)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.addTab(capture, 'Capture')
        tabs.addTab(export, 'Export')

        self.setCentralWidget(tabs)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)

    # https://www.pythonguis.com/tutorials/pyside-qprocess-external-programs/
    # https://doc.qt.io/qtforpython/PySide6/QtCore/QProcess.html
    def start_web(self):
        self.web_process.start("python3", ['chart.py'])


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.start_web()
    window.show()
    sys.exit(app.exec())
