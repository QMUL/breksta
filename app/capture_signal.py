"""
EXPERIMENTAL module that tries to encapsulate the Capture controls and Database access
in order to write readings to the database.
"""

import sys
from typing import Optional
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Slot  # Signal
from app.capture import PmtDb
from app.logger_config import setup_logger
from ui.central_controlpanel import CentralizedControlManager, get_manager_instance


class DeviceCapture:
    """Class that handles the signal capturing and database pushing of readings."""

    # external signal for the slot in the ChartWidget
    # experiment_started_signal = Signal(int)

    def __init__(self, manager: CentralizedControlManager, database, logger) -> None:
        self.logger = logger
        self.manager = manager
        self.database = database

        self.experiment_id: Optional[int] = None
        self.experiment_name: Optional[str] = None

        self.setup_connections()

    def setup_connections(self) -> None:
        """Connect to the ADCReader signal."""
        self.manager.output_signal.connect(self.write_to_database)
        self.manager.capture_ui.start_button_signal.connect(self.create_experiment)
        self.manager.capture_ui.stop_button_signal.connect(self.stop_experiment)

    @Slot()
    def create_experiment(self) -> None:
        """Database actions when Starting an experiment."""
        # Grab the experiment name, create new database entry and accompanying experiment ID
        self.experiment_name = self.manager.capture_ui.name_box.text()
        self.experiment_id = self.database.start_experiment(self.experiment_name)
        # self.experiment_started_signal.emit(self.experiment_id)
        self.logger.debug(
            "Experiment started named: %s and ID: %d", self.experiment_name, self.experiment_id)

    @Slot()
    def stop_experiment(self) -> None:
        """Database actions when Stopping an experiment."""
        # Close up database entry and clean up
        self.database.stop_experiment()
        self.logger.debug(
            "Experiment stopping named: %s and ID: %d", self.experiment_name, self.experiment_id)
        self.experiment_id = None

    @Slot(float)
    def write_to_database(self, data) -> None:
        """Logic to write data to the database"""
        try:
            self.database.write_reading(data)
            self.logger.debug("Reading: %s", data)
        except Exception as err:
            self.logger.error(f"Error writing to database: {err}", exc_info=True)
            raise


def main():
    app = QApplication(sys.argv)
    _logger = setup_logger()

    window: CentralizedControlManager = get_manager_instance(_logger)
    window.show()
    _database = PmtDb()

    device_capture = DeviceCapture(manager=window, database=_database, logger=_logger)

    sys.exit(app.exec())


if __name__ == "__main__":
    import cProfile
    cProfile.run('main()', 'profile_output')
