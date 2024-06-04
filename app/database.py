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

import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from pathvalidate import sanitize_filename
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, create_engine, exc
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.logger_config import setup_logger
from app.utils import get_db_path

pmt_db_path: Path = get_db_path()


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
    name: Mapped[str] = mapped_column(String(64), index=True)
    start: Mapped[datetime] = mapped_column(DateTime)
    end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    exported: Mapped[bool] = mapped_column(Boolean, default=False)


class PmtReading(Base):
    """Store the readings against each experiment here.
    Might as well have wall-clock time as the time-stamp so
    it can be a unique primary key.
    """

    __tablename__ = "reading"

    experiment: Mapped[int] = mapped_column(Integer, ForeignKey("experiment.id"))
    value: Mapped[float] = mapped_column(Float)
    ts: Mapped[datetime] = mapped_column(DateTime, primary_key=True)


def setup_session(db_path: Path) -> sessionmaker:
    """Create the Session if it doesn't exist, using the given database path.

    Args:
        db_path (Path): The path to the database file.

    Returns:
        sessionmaker: A sessionmaker instance bound to the engine.
    """
    # Convert Path object to a string and prepend with sqlite URI scheme
    engine = create_engine(f"sqlite:///{str(db_path)}")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    return session


class PmtDb:
    """Handles interactions with the database which contains experiments and PMT readings.
    The class provides functionalities to start and stop experiments, write readings to the database,
    fetch the latest readings, export data, delete experiments, and mark experiments as exported.
    """

    def __init__(self, session, logger) -> None:
        self.logger = logger if logger else setup_logger()

        self.session = session if session else setup_session(pmt_db_path)

        self.experiment_id: int | None = None
        self.start_time: datetime | None = None

    def start_experiment(self, name) -> int:
        """Starts a new experiment and writes it to the database.
        The start time is recorded as the current time.

        Args:
            name (str): The name of the experiment.

        Returns:
            int: The ID of the started experiment.
        """
        if self.experiment_id is not None:
            error_msg = "Attempted to start a new experiment while another is active."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        with self.session() as sess:
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
        if self.experiment_id is None:
            error_msg = "Attempted to stop an experiment when no experiment is active."
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.start_time = None
        with self.session() as sess:
            exp = sess.get(Experiment, self.experiment_id)
            if exp is None:
                error_msg = f"No experiment found with ID {self.experiment_id}."
                self.logger.error(error_msg)
                raise ValueError(error_msg)

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
        with self.session() as sess:
            sess.add(PmtReading(experiment=self.experiment_id, value=val, ts=datetime.now()))
            sess.commit()

    def latest_readings(self, experiment_id, since=None) -> pd.DataFrame | None:
        """Fetches the latest readings from the database.
        On experiment ID provided, fetches readings for that experiment.
        The timestamps are returned as integer seconds relative to the start time of the experiment.

        Args:
            experiment (int): The ID of the experiment to fetch readings for.
            since (datetime, optional): The earliest timestamp to fetch readings from.

        Returns:
            DataFrame or None: A DataFrame containing the readings and their timestamps,
            or None if no readings were found.
        """
        with self.session() as sess:
            expt = sess.query(Experiment).filter(Experiment.id == experiment_id).first()

            # Check if the experiment exists
            if expt is None:
                self.logger.warning("Experiment %s not found", experiment_id)
                return None

            if since is None:
                query = sess.query(PmtReading.ts, PmtReading.value).filter(PmtReading.experiment == experiment_id)
            else:
                query = sess.query(PmtReading.ts, PmtReading.value).filter(
                    PmtReading.experiment == experiment_id, PmtReading.ts > since
                )

            readings = query.all()

            # Check if readings were found
            if not readings:
                self.logger.warning("No readings found for experiment %s", experiment_id)
                return None

            # Convert query results to a DataFrame
            df = pd.DataFrame(readings, columns=["ts", "value"])

            # Calculate timestamps relative to the experiment's start time
            df["ts"] = df["ts"].apply(lambda ts: (ts - expt.start).total_seconds())

        return df

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
                self.logger.critical("Cannot export data for experiment %s because there are no readings.", experiment_id)
                return

            # Attempt to retrieve the experiment's start date
            with self.session() as sess:
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
            with self.session() as sess:
                # Query for the experiment to delete
                experiment = sess.query(Experiment).filter(Experiment.id == experiment_id).first()

                if experiment is None:
                    self.logger.critical(
                        "Cannot delete data for experiment %s because there are no readings.", experiment_id
                    )
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

    def get_experiments(self):
        """Fetches all experiments from the database.

        Returns:
            list: A list of tuples, each containing the ID, name, start time, end time,
            and exported status of an experiment.
        """
        with self.session() as sess:
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
            with self.session() as sess:
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
