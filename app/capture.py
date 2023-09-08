
"""While data is being captured it could be simultaenously being read by the local chart plotter,
remotely (if we want to do that) and by the export functionality. Negotiating locks on flat
.csv files will Not Be Fun. We could keep everything in shared memory, but we'd probably
rather data was sent to disk as soon as it's captured. SQLAlchemys Object Relational
Mapper (ORM) is one painless way to achieve this:
    https://docs.sqlalchemy.org/en/20/orm/quickstart.html
There'll only be one write at a time, so SQLite from the standard library will
*probably* do:
    https://www.sqlite.org/whentouse.html
Otherwise, SQLAlchemy speaks Postgres, so it should be able to talk to
QuestDB, a column-store for IOT time-series:
    https://questdb.io/
"""
import math
import random
import os
from datetime import datetime
from typing import Optional
from pathvalidate import sanitize_filename

import pandas as pd
from sqlalchemy import create_engine, ForeignKey, String, exc
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.logger_config import setup_logger


class Base(DeclarativeBase):
    """Creates a new base class for SQLAlchemy declarative models. In SQLAlchemy, the
    declarative base class serves as the foundation for all declarative model definitions.
    `Base` is just an instance of `DeclarativeBase`, and it will be used as the base class for
    all models in the application.
    The pass keyword is used when you need to create a block of code syntactically, but you
    want that block to do nothing
    """
    pass


class Experiment(Base):
    """Metadata for each experiment run.
    Add whatever else we need.
    """
    __tablename__ = "experiment"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    start: Mapped[datetime]
    end: Mapped[Optional[datetime]]
    exported: Mapped[bool] = mapped_column(default=False)


class PmtReading(Base):
    """Store the readings against each experiment here.
    Might as well have wall-clock time as the time-stamp so
    it can be a unique primary key.
    """
    __tablename__ = "reading"

    experiment: Mapped[int] = mapped_column(ForeignKey("experiment.id"))
    value: Mapped[int]
    ts: Mapped[datetime] = mapped_column(primary_key=True)


class PmtDb:
    """Handles interactions with the database which contains experiments and PMT readings.
    The class provides functionalities to start and stop experiments, write readings to the database,
    fetch the latest readings, export data, delete experiments, and mark experiments as exported.
    """
    def __init__(self, Session=None) -> None:

        self.logger = setup_logger()

        if Session is None:
            engine = create_engine('sqlite:///pmt.db')
            Base.metadata.create_all(engine)
            self.Session = sessionmaker(bind=engine)
        else:
            self.Session = Session

        self.experiment_id: Optional[int] = None
        self.start_time: Optional[datetime] = None

    def start_experiment(self, name):
        """Starts a new experiment and writes it to the database.
        The start time is recorded as the current time.

        Args:
            name (str): The name of the experiment.

        Returns:
            int: The ID of the started experiment.
        """
        assert self.experiment_id is None

        with self.Session() as sess:
            self.start_time = datetime.now()
            exp = Experiment(name=name, start=self.start_time)
            sess.add(exp)
            sess.commit()
            # Need to refresh the model to get the auto-incremented ID:
            sess.refresh(exp)

        self.experiment_id = exp.id

        return self.experiment_id

    def stop_experiment(self) -> None:
        """Stops the current experiment.
        The end time is recorded as the current time and the experiment ID is reset.
        """
        assert self.experiment_id is not None
        self.start_time = None
        with self.Session() as sess:
            exp = sess.get(Experiment, self.experiment_id)
            exp.end = datetime.now()
            sess.commit()
        self.experiment_id = None

    def write_reading(self, val) -> None:
        """Writes a new reading to the database.

        Creates a new `PmtReading` object with the given value and the current timestamp,
        associates it with the current experiment, and writes it to the database.

        Args:
            val (float): The reading to be written to the database.

        Raises:
            sqlalchemy.exc.SQLAlchemyError: If any error occurs while adding the reading to the session
            or committing the session.
        """
        with self.Session() as sess:
            sess.add(PmtReading(
                experiment=self.experiment_id,
                value=val, ts=datetime.now()))
            sess.commit()

    def latest_readings(self, experiment_id, since=None):
        """Fetches the latest readings from the database.
        On experiment ID provided, fetches readings for that experiment.
        The timestamps are returned as integer seconds relative to the start time of the experiment.

        Args:
            experiment (int): The ID of the experiment to fetch readings for.
            since (datetime, optional): The earliest timestamp to fetch readings from.

        Returns:
            DataFrame or None: A DataFrame containing the readings and their timestamps,
            or None if no readings were found.

        TODO: If we're continuing with the web-app for charting, cache the DB queries
        with Memcached or similar, query only the latest values.
        """
        with self.Session() as sess:
            expt = sess.query(Experiment).filter(Experiment.id == experiment_id).first()

            if since is None:
                query = sess.query(PmtReading.ts, PmtReading.value).filter(
                    PmtReading.experiment == experiment_id)
            else:
                query = sess.query(PmtReading.ts, PmtReading.value).filter(
                    PmtReading.experiment == experiment_id, PmtReading.ts > since)

            df = pd.DataFrame(query)
            if df.empty:
                self.logger.warning("No readings found for experiment %s", experiment_id)
                return None

            df['ts'] = (df.ts - expt.start).dt.total_seconds()

        return df

    def export_data(self) -> None:
        """Exports the data of all experiments to a CSV file.
        """
        # Query the database and get data
        data = self.query_database()

        # Convert data into a DataFrame
        df = pd.DataFrame(data)

        # Save DataFrame as a CSV file
        df.to_csv('export.csv')

    def export_data_single(self, experiment_id, folder_path) -> None:
        """Exports the data of a single experiment to a CSV file in the specified directory.
        The CSV file is named with the experiment's name and start time.

        Args:
            experiment_id (int): The ID of the experiment to export.
            folder_path (str): The path of the directory to save the CSV file in.
        """
        try:
            # create dataframe for "experiment_id"
            df = self.latest_readings(experiment_id)
            if df is None:
                self.logger.critical(
                    "Cannot export data for experiment %s because there are no readings.",
                    experiment_id)
                return

            # Attempt to retrieve the experiment's start date
            with self.Session() as sess:
                exp = sess.get(Experiment, experiment_id)
                if exp is not None:
                    stamp = exp.start.strftime("%Y%m%d-%H%M")
                    name = exp.name
                else:
                    self.logger.error("No experiment found with id %s", experiment_id)
                    return

            # create filename string and save to file
            filename = sanitize_filename(f"{name}-{stamp}.csv")
            full_path = os.path.join(folder_path, filename)
            df.to_csv(full_path, index=False)

        except (ValueError, AttributeError, OSError) as err:
            self.logger.debug("Export failed due to: %s", err)

        else:
            # only run if `try:` is successful. set exported status to "True"
            self.mark_exported(experiment_id)
            self.logger.debug("export_data_single complete")

    def delete_experiment(self, experiment_id) -> None:
        """Deletes an experiment and its readings from the database.

        Args:
            experiment_id (int): The ID of the experiment to delete.
        """
        try:
            with self.Session() as sess:
                # Query for the experiment to delete
                experiment = sess.query(Experiment).filter(Experiment.id == experiment_id).first()

                if experiment is None:
                    self.logger.critical(
                        "Cannot delete data for experiment %s because there are no readings.", experiment_id)
                    return

            # Delete the experiment and commit the changes
            sess.delete(experiment)
            sess.commit()
            self.logger.debug("Experiment %s deleted successfully.", experiment_id)

        except exc.NoResultFound:
            self.logger.critical("No experiment found with ID %s", experiment_id)
        except exc.IntegrityError as err:
            self.logger.critical("IntegrityError while deleting experiment: %s", err)
        except exc.OperationalError as err:
            self.logger.critical("OperationalError while deleting experiment: %s", err)

    def query_database(self):
        """Queries the database and returns a DataFrame of all readings,
        with the timestamps as integer seconds relative to the start time of each experiment.

        Returns:
            DataFrame: A DataFrame containing all readings from the database.
        """
        with self.Session() as sess:
            # Get a list of all experiments
            experiments = sess.query(Experiment).all()

            # Initialize an empty list to hold the data from all experiments
            data = []

            for expt in experiments:
                # Query the readings for the current experiment
                query = sess.query(PmtReading.ts, PmtReading.value).filter(PmtReading.experiment == expt.id)

                df = pd.DataFrame(query)

                df['ts'] = (df.ts - expt.start).dt.total_seconds()

                # Add the experiment data to the overall data
                data.append(df)

        # Concatenate all data into a single DataFrame
        all_data = pd.concat(data)

        return all_data

    def get_experiments(self):
        """Fetches all experiments from the database.

        Returns:
            list: A list of tuples, each containing the ID, name, start time, end time,
            and exported status of an experiment.
        """
        with self.Session() as sess:
            experiments = sess.query(Experiment).all()
            # Create a list of tuples, each containing the id, name, start time, end time of each experiment
            return [(expt.id, expt.name, expt.start, expt.end, expt.exported) for expt in experiments]

    def mark_exported(self, experiment_id):
        """Marks an experiment as exported in the database.

        Args:
            experiment_id (int): The ID of the experiment to mark as exported.

        Returns:
            bool: True if the experiment was successfully marked as exported, False otherwise.
        """
        try:
            with self.Session() as sess:
                if experiment_id is not None:
                    # Attempt to retrieve the experiment
                    exp = sess.get(Experiment, experiment_id)
                    if exp is not None:
                        # Mark the experiment as exported and commit the changes
                        exp.exported = True
                        sess.commit()
                        return True

                    self.logger.critical("No experiment found with ID %s", experiment_id)
                else:
                    self.logger.debug("Experiment ID is None")

        except exc.SQLAlchemyError as err:
            self.logger.debug("Failed to mark experiment as exported due to: %s", err)

        # Return False if the function did not return True earlier
        return False


class DevCapture:
    """Class that simulates a data capture device.
    The class provides a method to take a reading, which generates a simulated PMT reading and writes it to the database.

    TODO: How can we tell if we're running on a real Pi?
    """
    def __init__(self, db) -> None:
        self.db = db
        self.logger = setup_logger()

        self.omega = 2.0 * math.pi / 60

    def take_reading(self):
        """Simulates taking a PMT reading.
        The reading is a sine wave with some noise, and it is written to the database.

        Returns:
            int: The simulated PMT reading.
        """
        noise = (0.08 * random.random()) - 0.04
        signal = 0.92 * math.sin(self.omega * (datetime.now() - self.db.start_time).seconds)
        reading = 32768 + int(32768 * (signal + noise))
        self.db.write_reading(reading)
        self.logger.debug(reading)
        return reading
