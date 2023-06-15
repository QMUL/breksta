

import sys, datetime, traceback, os
# Programmatically set PYTHONPATH for breksta ONLY
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import plotly.graph_objects as go

from PySide6.QtCore import QProcess, QTimer, QUrl, Signal, Slot, Qt, QDir
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel, QLineEdit,
    QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QStyledItemDelegate, QFileDialog
    )
from PySide6.QtWebEngineWidgets import QWebEngineView

from app.capture import DevCapture
from app.capture import PmtDb

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
    def __init__(self, table):
        """
        Initializes the export control panel with the 'Export' and 'Refresh' buttons. Refresh is placeholder.
        Args:
            table: A TableWidget instance to interact with.
        """
        QWidget.__init__(self)

        # Create vertical box
        layout = QVBoxLayout()

        # Set up Export button
        self.export_button = QPushButton("Export", self)
        self.export_button.clicked.connect(self.on_export_button_clicked)
        self.export_button.setEnabled(True)
        layout.addWidget(self.export_button)

        # Set up Refresh button
        self.refresh_button = QPushButton("Refresh", self)
        self.refresh_button.clicked.connect(self.on_refresh_button_clicked)
        self.refresh_button.setEnabled(True)
        layout.addWidget(self.refresh_button)

        # Initialize the box
        self.setLayout(layout)

        # Initialize the experiment_id to receive signal
        self.selected_experiment_id = -1

        # Link to TableWidget instance
        self.table = table
        self.table.experimentSelected.connect(self.update_selected_experiment)

    @Slot(int)
    def update_selected_experiment(self, experiment_id):
        try:
            self.selected_experiment_id = experiment_id
            print(f"signal received {self.selected_experiment_id}. ID {id(self)}")
        except Exception as e:
            print(f"{e}")

        # No folder path set
        self.folder_path = None

    def on_export_button_clicked(self):
        """
        Exports the data of the selected experiment when the export button is clicked.
        Also refreshes the table widget after the export.
        """
        # if `selected_experiment_id` is still default, user hasn't clicked on table
        if self.selected_experiment_id == -1:
            print("To export, please choose an experiment from the list")
            return

        # Disable button during the exporting process
        self.export_button.setEnabled(False)
        print("Export button clicked. Exporting in progress...")

        # first time export is invoked, choose export folder
        # if cancelled, return control to parent
        if self.folder_path is None:
            self.choose_directory()
            if self.folder_path is None:
                print("No folder chosen.. Please, try again")
                self.export_button.setEnabled(True)
                return

        try:
            # Initialize the database connection
            db = PmtDb()

            # Export the data
            db.export_data_single(self.selected_experiment_id)

        except (OSError) as e:
            # if export gone wrong - OSError might catch pmt.db permissions issues
            print(f"Export button failed due to: {e}")
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

    def choose_directory(self):
        """
        Opens a dialog for the user to choose an export folder for the experiment data.
        The default directory opened in the dialog is the user's home directory (`$HOME`).
        Note: To open the dialog at the current working directory (`$CWD`) instead, replace `QDir.homePath()` with `QDir.currentPath()`.

        Returns:
            str or None: The chosen directory path, or None if no directory was chosen.
        """
        self.dialog = QFileDialog()
        self.folder_path = self.dialog.getExistingDirectory(None, "Select Folder", QDir.homePath())

        # Upon cancelling, folder_path will return an empty string, reset
        if self.folder_path == '':
            self.folder_path = None

        return self.folder_path

class ExportWidget(QWidget):
    """
    A QWidget subclass that provides an interface for exporting PMT data. It includes TableWidget for displaying the
    experiment information and ExportControl for controlling the data export and refreshing the table.
    """
    def __init__(self, width, table):

        QWidget.__init__(self)

        # Horizontal box
        layout = QHBoxLayout()

        # add export controls
        controls = ExportControl(table)
        controls.setFixedWidth(int(0.25 * width))

        # add experiment widget
        experiment_data = ExperimentWidget(width, table, controls)
        experiment_data.setFixedWidth(int(0.61 * width))

        layout.addWidget(controls)
        layout.addWidget(experiment_data)

        self.setLayout(layout)

class TableWidget(QTableWidget):
    """
    A QTableWidget subclass that displays PMT experiment information in a table format. It includes functionalities
    for populating the table with data from the PMT database and for handling user interaction with the table.
    """

    # create a signal that carries an integer
    experimentSelected = Signal(int)

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

        # connect cell clicked event to the appropriate method
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

        # check if database has data
        if not experiments: # list is empty
            print("Database has no data... table is empty")
            return

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
            # emit the signal
            self.experimentSelected.emit(self.selected_experiment_id)
            print(f"Cell clicked, row {row}, experiment id {self.selected_experiment_id}")

    def mousePressEvent(self, event):
        """
        Overrides the QTableWidget's mousePressEvent to maintain selection when a user clicks outside a valid item.
        """
        # sticky table line selection
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            return
        super().mousePressEvent(event)

class ExperimentGraph(QWebEngineView):
    """
    A QWebEngineView subclass that displays a Plotly graph for the selected experiment.
    """
    def __init__(self, width, table):
        QWebEngineView.__init__(self)

        # Reference to TableWidget instance, used to access `selected_experiment_id`
        self.table = table

        # Display a placeholder graph initially
        self.display_placeholder_graph(width)

    def display_placeholder_graph(self, width):
        """
        Display a placeholder graph before an experiment is selected.
        """
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=[0, 1],
            y=[0, 1],
            mode='markers',
            marker=dict(size=[0, 0])  # invisible points
        ))

        fig.update_layout(
            annotations=[
                go.layout.Annotation(
                    x=0.5,
                    y=0.5,
                    text="GRAPH",
                    showarrow=False,
                    font=dict(
                        size=84
                    )
                )
            ],
            xaxis=dict(showgrid=False, zeroline=False, visible=False),
            yaxis=dict(showgrid=False, zeroline=False, visible=False),
            autosize=False,
            width=width/2,
            height=width/4,
        )

        # Convert the Plotly figure to HTML and load it
        raw_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
        self.setHtml(raw_html)

    def refresh_graph(self):
        """
        Refresh the graph to reflect the data for the currently selected experiment.
        """

        if self.table.selected_experiment_id == -1:
            print("No experiment selected")
            return

        # Initialize the database connection
        db = PmtDb()

        exp_data = db.latest_readings(self.table.selected_experiment_id)

        if exp_data is not None:
            # Create a scatter plot with timestamp as x and value as y
            fig = go.Figure(data=go.Scatter(x=exp_data['ts'], y=exp_data['value']))

            # Convert the Plotly figure to HTML and load it
            raw_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
            self.setHtml(raw_html)
        else:
            print("No data to plot for the selected experiment")

class ExperimentWidget(QWidget):
    """
    A QWidget subclass that provides an interface for viewing PMT experiment data.
    It includes a TableWidget for displaying the experiment list and an ExperimentGraph for displaying experiment data.
    """
    def __init__(self, width, table, export_control):

        QWidget.__init__(self)

        # Vertical box layout
        layout = QVBoxLayout()

        # Create table and graph widgets
        self.graph = ExperimentGraph(width, table)
        self.export_control = export_control

        # Add widgets to layout in order: table first, graph second
        layout.addWidget(table)
        layout.addWidget(self.graph)

        self.setLayout(layout)

        # connect the experimentSelected signal to the slots
        table.experimentSelected.connect(self.graph.refresh_graph)
        table.experimentSelected.connect(self.export_control.update_selected_experiment)

# https://doc.qt.io/qtforpython/tutorials/datavisualize/
class MainWindow(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        # Launch the plotly/dash web-app in here:
        self.web_process = QProcess(self)
        # Connect a slot to QProcess.finished to cleanup when your process ends
        self.web_process.finished.connect(self.on_process_finished)

        self.setWindowTitle("Breksta")

        geometry = self.screen().availableGeometry()

        win_width = int(geometry.width() * 0.95)
        win_height = int(geometry.height() * 0.95)

        self.setFixedSize(win_width, win_height)

        self.table = TableWidget(win_width)  # Only create one instance of TableWidget

        capture = CaptureWidget(win_width)
        export = ExportWidget(win_width, self.table)

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
        '''
        Initializes the web process to start the Dash server running "chart.py".
        This function assumes that "chart.py" resides in the same directory as "breksta.py".
        The process is run in its own thread.
        '''
        # Connect the readyReadStandardError signal to the handle_stderr slot
        # This allows us to read any error messages output by the web process
        self.web_process.readyReadStandardError.connect(self.handle_stderr)
        try:
            # Connect the errorOccurred signal to the handle_error slot
            # This allows us to react to errors that occur while the process is running
            self.web_process.errorOccurred.connect(self.handle_error)
            # Start the web process using python3 and the module path to chart.py
            self.web_process.start("python3", ["-m", "app.chart"])
            # Wait for the process to start, print a failure message if it doesn't
            if not self.web_process.waitForStarted():
                print("Failed to start web process.")
        except Exception as e:
            print('web process fell over:', str(e))
        else:
            print("starting web process")

    def handle_error(self, error):
        # Function to handle errors that occur in the web process
        print("An error occurred in the web process:", error)

    def handle_stderr(self):
        # Function to handle standard error output from the web process
        # Reads the standard error output, decodes it, and prints it
        stderr = self.web_process.readAllStandardError().data().decode()
        print(stderr)

    def on_process_finished(self):
        # Function to handle the process finishing
        # Closes the web process when it finishes running
        self.web_process.close()

    def closeEvent(self, event):
        '''
        Override the QMainWindow close event to properly shut down the web process.
        If the web process is running, it is terminated, with a timeout for graceful termination.
        If the process does not terminate within the timeout, it is forcibly killed.
        '''
        # Check if the web process is running
        if self.web_process.state() == QProcess.Running:
            # If it is, terminate the process
            self.web_process.terminate()
            # Wait a moment for the process to finish
            # If it doesn't finish within the timeout, forcibly kill the process
            if not self.web_process.waitForFinished(1000):
                self.web_process.kill()
        # Accept the close event, allowing the main window to close
        event.accept()

if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.start_web()
    window.show()
    sys.exit(app.exec())
