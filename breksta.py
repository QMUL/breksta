

import sys, datetime, traceback

from PySide6.QtCore import QProcess, QTimer, QUrl, Signal, Slot, Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QStyledItemDelegate
    )
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


class ExportControl(QWidget):
    """
    A QWidget subclass that provides control buttons and functionalities for exporting data from the PMT database.
    """
    def __init__(self, tableWidget):
        """
        Initializes the export control panel with the 'Export' and 'Refresh' buttons. Refresh is placeholder
        """
        QWidget.__init__(self)

        # Create vertical box
        layout = QVBoxLayout()

        # Set Export button
        self.export_button = QPushButton("Export", self)
        self.export_button.clicked.connect(self.on_export_button_clicked)
        self.export_button.setEnabled(True)
        layout.addWidget(self.export_button)

        # Set Refresh button
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.on_refresh_button_clicked)
        self.refresh_button.setEnabled(True)
        layout.addWidget(self.refresh_button)

        # Initialize the box
        self.setLayout(layout)

        # link to TableWidget class
        # grants access to `selected_experiment_id`
        self.table = tableWidget

    def on_export_button_clicked(self):
        """
        Exports the data of the selected experiment when the export button is clicked.
        Also refreshes the table widget after the export.
        """
        # if `selected_experiment_id` is still default, user hasn't clicked on table
        # return control to parent
        if self.table.selected_experiment_id == -1:
            print("To export, please choose an experiment from the list")
            return

        # Disable button upon clicking. Acknowledge.
        self.export_button.setEnabled(False)
        print("Export button clicked. Exporting in progress...")

        try:
            # Initialize the database connection
            db = PmtDb()

            # Export the data
            db.export_data_single(self.table.selected_experiment_id)

        except Exception as e:
            # if export gone wrong
            print(f"Export failed due to: {e}")
            print(traceback.format_exc())

        else:
            # only runs if try is successful
            print("Export complete!")
            print("Refresh list...")
            self.table.populate_table()

        finally:
            # always runs - return control to button
            self.export_button.setEnabled(True)

    def on_refresh_button_clicked(self):
        print("Refreshing experiment list...")

class ExportWidget(QWidget):
    """
    A QWidget subclass that provides an interface for exporting PMT data. It includes TableWidget for displaying the
    experiment information and ExportControl for controlling the data export and refreshing the table.
    """
    def __init__(self, width):

        QWidget.__init__(self)

        # Horizontal box
        layout = QHBoxLayout()

        # controls depends on table to set `selected_experiment_id`
        table = TableWidget(width)
        table.setFixedWidth(int(0.61 * width))
        controls = ExportControl(table)
        controls.setFixedWidth(int(0.25 * width))

        layout.addWidget(controls)
        layout.addWidget(table)

        self.setLayout(layout)

class TableWidget(QTableWidget):
    """
    A QTableWidget subclass that displays PMT experiment information in a table format. It includes functionalities
    for populating the table with data from the PMT database and for handling user interaction with the table.
    """
    def __init__(self, width):
        """
        Initializes the table widget with 0 rows and 5 columns. The columns are labeled with 'Id', 'Name', 'Date started',
        'Date ended', 'Exported', and the table is populated with data from the PMT database.
        """
        QTableWidget.__init__(self, 0, 5)

        # initialise with invalid id, test
        self.selected_experiment_id = -1

        # set the column labels
        self.setHorizontalHeaderLabels(['Id', 'Name', 'Date started', 'Date ended', 'Exported'])

        # make the rows selectable
        self.setSelectionBehavior(QTableWidget.SelectRows)

        # adjust the column width
        self.setColumnWidth(0, int(0.03 * width))
        self.setColumnWidth(1, int(0.15 * width))
        self.setColumnWidth(2, int(0.15 * width))
        self.setColumnWidth(3, int(0.15 * width))
        self.setColumnWidth(4, int(0.1 * width))

        # retrieve the experiment data
        self.populate_table()

        # QTableWidgetItem can access the following - needed for text alignment
        self.setItemDelegate(QStyledItemDelegate())

        # grab experiment - table click signal
        self.cellClicked.connect(self.on_cell_click)

    def populate_table(self):
        """
        Populates the table with data from the PMT database. Each row in the table corresponds to an experiment from the database.
        """
        # Initialize the database connection
        db = PmtDb()

        # get_experiments() returns a list of tuples, each containing:
        # (id, name, date start, date end, exported status)
        experiments = db.get_experiments()

        # set num of rows to num of experiments in database
        self.setRowCount(len(experiments))

        # Set num of columns to length of tuple
        col = self.setColumnCount(len(experiments[0]))

        for row, experiment in enumerate(experiments):
            for col, entry in enumerate(experiment):
                new_item = QTableWidgetItem(entry.strftime('%Y-%m-%d %H:%M') if isinstance(entry, datetime.datetime) else str(entry))
                new_item.setTextAlignment(Qt.AlignCenter)  # Sets text alignment to center
                new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)  # Makes item non-editable
                self.setItem(row, col, new_item)

        # self.resizeColumnsToContents()  # Resizes columns to fit content

    def on_cell_click(self, row):
        """
        Handles user click on a cell in the table. The ID of the clicked experiment is stored for future use.
        """
        # assume that the experiment ID is in the first column
        item = self.item(row, 0)
        if item is not None:
            self.selected_experiment_id = int(item.text())
            print(item.text())

    def mousePressEvent(self, event):
        """
        Overrides the QTableWidget's mousePressEvent to maintain selection when a user clicks outside a valid item.
        """
        # sticky table line selection
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            return
        super().mousePressEvent(event)

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
