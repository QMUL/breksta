"""This module contains the main application for managing experiments.
It includes the main window UI, the data capture and charting functionalities.
"""
import sys
import datetime
import os
import shutil
from typing import Optional

from PySide6.QtCore import QProcess, QUrl, Signal, Slot, Qt, QDir
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QHBoxLayout, QMainWindow,
    QPushButton, QTabWidget, QVBoxLayout, QWidget, QTableWidget,
    QTableWidgetItem, QStyledItemDelegate, QFileDialog, QMessageBox)
from PySide6.QtWebEngineWidgets import QWebEngineView

from app.database import PmtDb, setup_session
from app.logger_config import setup_logger
from app.capture_signal import DeviceCapture
from ui.central_controlpanel import CentralizedControlManager, get_manager_instance
from app.components.figure import initialize_figure, plot_data, display_placeholder_graph, downsample_data

# Programmatically set PYTHONPATH for breksta ONLY
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


class ChartWidget(QWebEngineView):
    """Sub-classed WebView:
        https://doc.qt.io/qt-6/webengine-widgetexamples.html
    Probably want to sub-class from QWidget, embded the Web#view in a
    layout with some more native UI to control scaling, etc...
    """
    DASH_APP_PORT = 8050

    def __init__(self, logger) -> None:

        QWebEngineView.__init__(self)

        self.logger = logger  # if logger else setup_logger()
        self.logger.debug("WebEngineView initialized.")

    def _on_downloadRequested(self, download) -> None:
        """Handles the download request signal from the web view.

        Parameters:
            download: The download request object.

        Returns:
            None
        """
        download.accept()

    @Slot(int)
    def plot_experiment(self, experiment_id: int) -> str:
        """Plots the experiment data in a web view by loading a local web server URL.

        This method assumes that a Plotly Dash application is running on localhost at port 8050,
        and that this application can plot the experiment when provided with an experiment ID.

        Args:
            experiment_id (int): The ID of the experiment to be plotted.

        Slot to receive the started signal from CaptureControl.
        Could pass the experiment ID as a parameter to the web app.
        https://doc.qt.io/qtforpython/PySide6/QtCore/Slot.html
        """

        self.logger.debug("WebEngineView starting..")

        if experiment_id is None:
            self.logger.error("experiment_id is None. Invalid value.")

        # Constuct URL
        base_url = f'http://localhost:{self.DASH_APP_PORT}/'
        url = QUrl(f'{base_url}?experiment={experiment_id}')
        self.logger.debug("Emitting URL: %s", url.toString())

        # Serve QUrl object on the server
        self.load(url)

        return url.toString()


class CaptureWidget(QWidget):
    """Stick the capture and chart widgets in a parent layout.
    """
    def __init__(self, width, database, logger) -> None:

        QWidget.__init__(self)

        self.logger = logger  # if logger else setup_logger()
        self.database = database

        self.controls, self.capture_db, self.chart = self.instantiate_objects()

        self.controls.setFixedWidth(int(0.2 * width))
        self.chart.setFixedWidth(int(0.8 * width))

        self.chart.page().profile().downloadRequested.connect(self.chart._on_downloadRequested)

        # Signal from capture_signal to the chart routed here. Helps avoid a hideous God Object.
        self.capture_db.experiment_started_signal.connect(self.chart.plot_experiment)

        layout = self.create_layout(self.controls, self.chart)
        self.setLayout(layout)

    def instantiate_objects(self) -> tuple[CentralizedControlManager, DeviceCapture, ChartWidget]:
        """Create the instances of all objects."""
        controls: CentralizedControlManager = get_manager_instance(self.logger)
        capture_db = DeviceCapture(manager=controls, logger=self.logger, database=self.database)
        chart = ChartWidget(self.logger)
        return controls, capture_db, chart

    def create_layout(self, controls, chart) -> QHBoxLayout:
        """
        Create the Controls tab layout.
        There are two components: the controls and the chart objects.
        """
        layout = QHBoxLayout()
        layout.addWidget(controls)
        layout.addWidget(chart)
        return layout


class ExportControl(QWidget):
    """A QWidget subclass that provides control buttons and functionalities for
    exporting data from the database.
    """
    def __init__(self, table, logger) -> None:
        """Initializes the export control panel with the 'Export' and 'Delete' buttons.
        Args:
            table: The TableWidget instance to interact with.
        """
        QWidget.__init__(self)

        self.logger = logger  # if logger else setup_logger()

        # Create vertical box
        layout = QVBoxLayout()

        # Set up Export button
        self.export_button = QPushButton("Export", self)
        self.export_button.clicked.connect(self.on_export_button_clicked)
        self.export_button.setEnabled(True)
        layout.addWidget(self.export_button)

        # Set up Delete button
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.on_delete_button_clicked)
        self.delete_button.setEnabled(True)
        layout.addWidget(self.delete_button)

        # Initialize the box
        self.setLayout(layout)

        # Initialize the experiment_id to receive signal
        self.selected_experiment_id: Optional[int] = None

        # Link to TableWidget instance
        self.table = table
        self.table.experimentSelected.connect(self.update_selected_experiment)

        # Initialize attributes with default values
        self.folder_path: Optional[str] = None

    @Slot(int)
    def update_selected_experiment(self, experiment_id) -> None:
        """Updates the currently selected experiment ID.

        This method is typically connected to a signal that emits an experiment ID when an experiment is selected in the UI.

        Args:
            experiment_id (int): The ID of the experiment to be selected.
        """
        self.selected_experiment_id = experiment_id
        self.logger.debug("signal received %s. ID %s", self.selected_experiment_id, id(self))

    def on_export_button_clicked(self) -> None:
        """Handles the click event of the export button.
        If a folder is chosen and the database connection is established successfully,
        the data of the selected experiment is exported to the chosen directory.
        If an error occurs during the process (such as permission issues), an error log is created.
        """
        # if selected_experiment_id is still default, user hasn't clicked on table
        if self.selected_experiment_id is None:
            self.logger.warning("To export, please choose an experiment from the list")
            return

        # Disable button during the exporting process
        self.export_button.setEnabled(False)
        self.logger.info("Export button clicked. Exporting in progress...")

        # first time export is invoked, choose export folder
        # if cancelled, return control to parent
        if not self.folder_path:
            chosen_dir = self.choose_directory()
            if not chosen_dir:
                self.logger.warning("No folder chosen.. Please, try again")
                self.export_button.setEnabled(True)
                return
            self.folder_path = chosen_dir

        # Propagate the database connection
        database = self.table.database

        try:
            database.export_data_single(self.selected_experiment_id, self.folder_path)

        except (OSError) as err:
            # catch pmt.db permissions issues
            self.logger.critical("Export button failed due to: %s", err)

        else:
            # only runs if try is successful
            self.logger.info("Export complete! Refresh table list...")
            self.table.populate_table()

        finally:
            # always runs - return control to button
            self.export_button.setEnabled(True)

    def choose_directory(self) -> str | None:
        """Opens a dialog for the user to choose an export folder for the experiment data.
        The default directory opened in the dialog is the user's home directory ($HOME).
        Note: To open the dialog at the current working directory ($CWD) instead,
        replace QDir.homePath() with QDir.currentPath().

        Returns:
            str or None: The chosen directory path, or None if no directory was chosen.
        """
        dialog = QFileDialog()
        chosen_path = dialog.getExistingDirectory(None, "Select Folder", QDir.homePath())

        # Upon cancelling, chosen_path will return an empty string, reset
        if not chosen_path:
            return None

        self.logger.debug("Exporting directory chosen as: %s", chosen_path)
        return chosen_path

    def on_delete_button_clicked(self) -> None:
        """Deletes the selected experiment when the delete button is clicked.
        Also refreshes the table widget after the deletion.
        """
        # if selected_experiment_id is still default, user hasn't clicked on table
        if self.selected_experiment_id is None:
            self.logger.info("To delete, please choose an experiment from the list")
            return

        # Disable button during the deleting process
        self.delete_button.setEnabled(False)
        self.logger.info("Delete button clicked. Deleting in progress...")

        # first time delete is invoked, choose database folder
        # if cancelled, return control to parent
        if not self.folder_path:
            chosen_dir = self.choose_directory()
            if not chosen_dir:
                self.logger.warning("No folder chosen.. Please, try again")
                self.delete_button.setEnabled(True)
                return
            self.folder_path = chosen_dir

        # Propagate the database connection
        database = self.table.database

        try:
            # backup the database in preparation of destructive manipulation
            self.backup_database()
            # find if exported and handle deletion user prompting
            item = self.table.item(self.table.selected_row, 4)
            self.logger.debug("selected row is: %s", self.table.selected_row)

            # item.text() does not return a boolean, handle truthiness
            is_exported = item.text() == "True"
            export_status = 'exported' if is_exported else 'not exported'
            self.logger.debug("Experiment is %s", export_status)

            reply = self.confirm_delete(is_exported)
            self.logger.debug("User wants to delete ID %s: %s", self.selected_experiment_id, reply)

            if reply:  # only attempt deletion if the user confirmed
                database.delete_experiment(self.selected_experiment_id)

        except OSError as err:
            self.logger.exception("Operation failed due to: %s", err)
            self.restore_database()

        else:
            if reply:  # only if the user confirmed
                self.logger.info("Deletion complete! Refresh experiment list...")
                self.table.populate_table()

        finally:
            # always runs - return control to button
            self.delete_button.setEnabled(True)

    def confirm_delete(self, is_exported):
        """Handles user prompts to confirm the deletion of an experiment.
        If the experiment hasn't been exported yet, it prompts for an additional confirmation.
        Returns True if deletion is confirmed, False otherwise.
        """
        def confirm_dialog(title, text):
            reply = QMessageBox.question(
                self, title, text,
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No)  # type: ignore
            return reply == QMessageBox.Yes  # type: ignore

        if not is_exported and not confirm_dialog(
                'Delete Unexported Experiment',
                "This experiment has not been exported. Are you sure you want to delete?"):
            return False

        return confirm_dialog(
            'Delete Experiment',
            "Are you sure you want to delete this experiment?")

    def backup_database(self, filename=None):
        """Creates a database backup.

        If a filename is provided, it is used as a prefix to the timestamp in the backup filename.
        This is intended for manual backups and prevents overwriting previous backups.

        If no filename is provided, an automatic backup named "backup.db" is created.
        This backup gets updated with each deletion for automatic error handling.

        Returns:
            str: backup_path, the location where the database was stored.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")

        db_path = self.get_root_dir()

        if filename:
            # If a filename is provided, use it as a prefix to the timestamp
            backup_path = os.path.join(self.folder_path, f'{filename}_{timestamp}.db')
        else:
            # If no filename is provided, create an automatic backup named "backup.db"
            backup_path = os.path.join(self.folder_path, 'backup.db')

        shutil.copy(db_path, backup_path)
        return backup_path

    def restore_database(self, filename=None) -> None:
        """Restores the database from a backup.
        If a filename is provided, it is used as the name of the backup file.
        Otherwise, a default name "backup.db" is used.
        """
        db_path = self.get_root_dir()

        # folder_path has to be str for the join()
        if self.folder_path is not None:
            # Set backup_path based on whether filename is provided or not
            if filename:
                backup_path = os.path.join(self.folder_path, filename)
            else:
                backup_path = os.path.join(self.folder_path, 'backup.db')
        else:
            raise ValueError("self.folder_path is None")

        # Then check if backup file exists
        if not os.path.isfile(backup_path):
            raise FileNotFoundError(f"Backup file {backup_path} does not exist.")

        shutil.copy(backup_path, db_path)

    def get_root_dir(self) -> str:
        """Grabs root directory - by default where we save 'pmt.db'
        """
        script_path = os.path.dirname(os.path.realpath(__file__))
        root_path = os.path.dirname(script_path)
        db_path = os.path.join(root_path, 'pmt.db')
        return db_path


class ExportWidget(QWidget):
    """A QWidget subclass that provides an interface for exporting data.
    It includes TableWidget for displaying the experiment information and
    ExportControl for controlling the data export and refreshing the table.
    """
    def __init__(self, width, table, logger) -> None:

        QWidget.__init__(self)

        self.logger = logger  # if logger else setup_logger()

        # Horizontal box
        layout = QHBoxLayout()

        # add export controls
        controls = ExportControl(table, self.logger)
        controls.setFixedWidth(int(0.2 * width))

        # add experiment widget
        experiment_data = ExperimentWidget(width, table, controls, self.logger)
        experiment_data.setFixedWidth(int(0.75 * width))

        layout.addWidget(controls)
        layout.addWidget(experiment_data)

        self.setLayout(layout)


class TableWidget(QTableWidget):
    """A QTableWidget subclass that displays experiment information in a table format.
    It includes methods for populating the table with data from the PMT database
    and for handling user interaction with the table.
    """

    # create a signal that carries an integer
    experimentSelected = Signal(int)

    def __init__(self, width, database, logger) -> None:
        """Initializes the table widget with 0 rows and 5 columns.
        The columns are labeled with 'Id', 'Name', 'Date started', 'Date ended', and 'Exported'.
        """

        num_of_columns = 5
        num_of_rows = 0

        QTableWidget.__init__(self, num_of_rows, num_of_columns)

        self.logger = logger  # if logger else setup_logger()

        # Database connection initialized in MainWindow ONCE in breksta
        self.database = database

        # initialise with invalid id, test
        self.selected_experiment_id: Optional[int] = None
        self.selected_row: Optional[int] = None

        # set the column labels
        self.setHorizontalHeaderLabels(['Id', 'Name', 'Date started', 'Date ended', 'Exported'])

        # make the rows selectable
        self.setSelectionBehavior(QTableWidget.SelectRows)  # type: ignore

        # adjust the column width
        self.setColumnWidth(0, int(0.03 * width))
        self.setColumnWidth(1, int(0.15 * width))
        self.setColumnWidth(2, int(0.15 * width))
        self.setColumnWidth(3, int(0.15 * width))
        self.setColumnWidth(4, int(0.1 * width))

        # retrieve and present all experiment data
        self.populate_table()

        # QTableWidgetItem can access the following - needed for text alignment
        self.setItemDelegate(QStyledItemDelegate())

        # connect cell clicked event to the appropriate method
        self.cellClicked.connect(self.on_cell_click)

    def populate_table(self) -> None:
        """Populates the table with data from the PMT database.
        Each row in the table corresponds to an experiment from the database.
        """
        # get_experiments() returns a list of tuples, each containing:
        # (id, name, date start, date end, exported status)
        experiments = self.database.get_experiments()

        # check if database has data. If list empty, may be first run
        if not experiments:
            self.logger.warning("Database has no data... table is empty")
            return

        # set num of rows to num of experiments in database
        self.setRowCount(len(experiments))

        # Set num of columns to length of tuple
        self.setColumnCount(len(experiments[0]))

        for row, experiment in enumerate(experiments):
            for col, entry in enumerate(experiment):
                if isinstance(entry, datetime.datetime):
                    new_item = QTableWidgetItem(entry.strftime('%Y-%m-%d %H:%M'))
                else:
                    new_item = QTableWidgetItem(str(entry))
                new_item.setTextAlignment(Qt.AlignCenter)  # type: ignore # Sets text alignment to center
                new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)  # type: ignore # Makes item non-editable
                self.setItem(row, col, new_item)

    def on_cell_click(self, row) -> None:
        """Handles user click on a cell in the table.
        The ID of the clicked experiment is stored for future use.
        """
        # assume that the experiment ID is in the first column
        item = self.item(row, 0)
        if item is not None:
            self.selected_experiment_id = int(item.text())
            self.selected_row = row
            # emit the signal
            self.experimentSelected.emit(self.selected_experiment_id)
            self.logger.debug(
                "Cell clicked, row %s, experiment id %s", row, self.selected_experiment_id)

    def mousePressEvent(self, event) -> None:
        """Overrides the QTableWidget's mousePressEvent.
        Maintains selection when a user clicks outside a valid item.
        """
        # sticky table line selection
        index = self.indexAt(event.position().toPoint())
        if not index.isValid():
            return
        super().mousePressEvent(event)


class ExperimentGraph(QWebEngineView):
    """A QWebEngineView subclass.
    Displays a Plotly graph for the selected experiment.
    """
    def __init__(self, width, table, logger) -> None:
        QWebEngineView.__init__(self)

        self.logger = logger  # if logger else setup_logger()

        # Reference to TableWidget instance, used to access selected_experiment_id
        self.table = table

        # Display a placeholder graph initially
        preview = display_placeholder_graph(width)
        self.setHtml(preview)

        self.figure = initialize_figure()

    def refresh_graph(self) -> None:
        """Refresh the graph to reflect the data for the currently selected experiment.
        """

        experiment_id: int = self.table.selected_experiment_id
        if experiment_id is None:
            self.logger.debug("Cannot refresh preview graph. No experiment selected.")
            return

        database = self.table.database

        df = database.latest_readings(experiment_id)
        if df is None:
            self.logger.warning("Cannot create preview. Dataframe empty.")
            return

        df_scaled = downsample_data(df)
        figure = plot_data(self.figure, df_scaled)

        raw_html = figure.to_html(full_html=False, include_plotlyjs='cdn')
        self.setHtml(raw_html)


class ExperimentWidget(QWidget):
    """A QWidget subclass.
    Provides an interface for viewing PMT experiment data.
    It includes a TableWidget for displaying the experiment list
    and an ExperimentGraph for displaying experiment data.
    """
    def __init__(self, width, table, export_control, logger) -> None:

        QWidget.__init__(self)

        self.logger = logger  # if logger else setup_logger()

        # Vertical box layout
        layout = QVBoxLayout()

        # Create table and graph widgets
        self.graph = ExperimentGraph(width, table, self.logger)
        self.export_control = export_control

        # Add widgets to layout in order: table first, graph second
        layout.addWidget(table)
        layout.addWidget(self.graph)

        self.setLayout(layout)

        self.setup_connections(table)

    def setup_connections(self, table) -> None:
        """connect the experimentSelected signal to the slots"""
        table.experimentSelected.connect(self.graph.refresh_graph)
        table.experimentSelected.connect(self.export_control.update_selected_experiment)


# https://doc.qt.io/qtforpython/tutorials/datavisualize/
class MainWindow(QMainWindow):
    """The main window of the application.
    Includes all widgets and controls. It also handles the lifecycle of the
    web process running the Dash server.
    """
    def __init__(self, logger) -> None:

        QMainWindow.__init__(self)

        # Initialize logging
        self.logger = logger
        self.logger.info('=' * 50)
        self.logger.info('APP SPOOLING UP!')

        # Launch the plotly/dash web-app in here:
        self.web_process = QProcess(self)
        # Connect a slot to QProcess.finished to cleanup when your process ends
        self.web_process.finished.connect(self.on_process_finished)

        self.setWindowTitle("Breksta")

        geometry = self.screen().availableGeometry()

        win_width = int(geometry.width() * 0.95)
        win_height = int(geometry.height() * 0.95)

        self.setFixedSize(win_width, win_height)

        self.capture, self.export = self.instantiate_objects(win_width, self.logger)

        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)  # type: ignore
        tabs.addTab(self.capture, 'Capture')
        tabs.addTab(self.export, 'Export')

        self.setCentralWidget(tabs)

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)  # type: ignore
        exit_action.triggered.connect(self.close)

    def instantiate_objects(self, win_width, logger) -> tuple[CaptureWidget, ExportWidget]:
        """Create the instances of all objects."""
        session = setup_session()
        database = PmtDb(session=session, logger=logger)
        capture = CaptureWidget(win_width, database, logger)
        table = TableWidget(win_width, database, logger)
        export = ExportWidget(win_width, table, logger)
        return capture, export

    # https://www.pythonguis.com/tutorials/pyside-qprocess-external-programs/
    # https://doc.qt.io/qtforpython/PySide6/QtCore/QProcess.html
    def start_web(self) -> None:
        """Initializes the web process to start the Dash server running "chart.py".
        This function assumes that "chart.py" resides in the same directory as "breksta.py".
        The process is run in its own thread.
        """
        # Connect the readyReadStandardError signal to the handle_stderr slot
        # This allows us to read any error messages output by the web process
        self.web_process.readyReadStandardError.connect(self.handle_stderr)
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                # Connect the errorOccurred signal to the handle_error slot
                # This allows us to react to errors that occur while the process is running
                self.web_process.errorOccurred.connect(self.handle_error)
                # Start the web process using python3 and the module path to chart.py
                self.web_process.start("python3", ["-m", "app.chart"])

                # Wait for the process to start, print a failure message if it doesn't
                if self.web_process.waitForStarted():
                    self.logger.info("Starting web process...")
                    break

                self.logger.warning("Failed to start web process. Attempt %d of %d.", attempt + 1, retry_attempts)

            except (TypeError, RuntimeError, QProcess.StartFailed) as err:  # type: ignore
                self.logger.debug('web process fell over: %s', err)
        else:
            # Alert the user of the failure with a QMessageBox
            QMessageBox.critical(
                self,
                "Web Process Error",
                "Failed to start the web process after several attempts. The application may not work correctly.")
            self.logger.critical("Failed to start web process after %d attempts.", retry_attempts)

    def handle_error(self, error) -> None:
        """Handles errors that occur in the web process
        """
        self.logger.debug("An error occurred in the web process: %s", error)

    def handle_stderr(self) -> None:
        """Handles standard error output from the web process.
        Reads the standard error output, decodes it, and prints it
        """
        stderr = self.web_process.readAllStandardError().data().decode()
        self.logger.debug(stderr)

    def on_process_finished(self) -> None:
        """Handles the process finishing.
        Closes the web process when it finishes running
        """
        self.web_process.close()

    def closeEvent(self, event) -> None:
        """Overrides the QMainWindow close event to properly shut down the web process.
        If the web process is running, it is terminated, with a timeout for graceful termination.
        If the process does not terminate within the timeout, it is forcibly killed.
        Args:
            event: The close event triggered when the main window is closed.
        """
        # Check if the web process is running
        if self.web_process.state() == QProcess.Running:  # type: ignore
            # If it is, terminate the process
            self.web_process.terminate()
            # Wait a moment for the process to finish
            # If it doesn't finish within the timeout, forcibly kill the process
            if not self.web_process.waitForFinished(1000):
                self.web_process.kill()

        self.logger.info('APP WINDING DOWN!')
        self.logger.info('=' * 50)

        # Accept the close event, allowing the main window to close
        event.accept()


if __name__ == "__main__":
    _logger = setup_logger("DEBUG")
    app = QApplication()
    window = MainWindow(_logger)
    window.start_web()
    window.show()
    sys.exit(app.exec())
