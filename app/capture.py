
'''
While data is being captured it could be simultaenously being read by the local chart plotter,
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
'''

from datetime import datetime
import math
import random, os
from typing import Optional
from pathvalidate import sanitize_filename

import pandas as pd
from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from app.logger_config import setup_logger

class Base(DeclarativeBase):
    pass

class Experiment(Base):
    '''Metadata for each experiment run.
    Add whatever else we need.
    '''
    __tablename__ = "experiment"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    start: Mapped[datetime]
    end: Mapped[Optional[datetime]]
    exported: Mapped[bool] = mapped_column(default=False)

class PmtReading(Base):
    '''Store the readings against each experiment here.
    Might as well have wall-clock time as the time-stamp so
    it can be a unique primary key.

    '''
    __tablename__ = "reading"

    experiment: Mapped[int] = mapped_column(ForeignKey("experiment.id"))
    value: Mapped[int]
    ts: Mapped[datetime] = mapped_column(primary_key=True)

class PmtDb(object):

    def __init__(self):

        # set up logger
        self.logger = setup_logger()

        engine = create_engine('sqlite:///pmt.db')
        Base.metadata.create_all(engine)
        self.Session = sessionmaker(engine)
        self.experiment_id = None
        self.start_time = None

    def start_experiment(self, name):
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

    def stop_experiment(self):
        assert not self.experiment_id is None
        self.start_time = None
        with self.Session() as sess:
            exp = sess.get(Experiment, self.experiment_id)
            exp.end = datetime.now()
            sess.commit()
        self.experiment_id = None

    def write_reading(self, val):
        with self.Session() as sess:
            sess.add(PmtReading(experiment=self.experiment_id,
                value=val, ts=datetime.now()))
            sess.commit()

    def latest_readings(self, experiment=None, since=None):
        '''Return a DataFrame of readings for an experiment, (default current)
        with the timestamps as integer seconds relative to the start time.

        TODO: If we're continuing with the web-app for charting, cache the DB queries
        with Memcached or similar, query only the latest values.
        '''
        with self.Session() as sess:
            if experiment is None:
                expt = sess.query(Experiment).order_by(
                    Experiment.id.desc()).first()
                experiment = expt.id
            else:
                expt = sess.query(Experiment).filter(Experiment.id==experiment).first()

            if since is None:
                query = sess.query(PmtReading.ts, PmtReading.value).filter(
                    PmtReading.experiment==experiment)
            else:
                query = sess.query(PmtReading.ts, PmtReading.value).filter(
                    PmtReading.experiment==experiment, PmtReading.ts > since)

            df = pd.DataFrame(query)
            if df.empty:
                self.logger.warning(f"No readings found for experiment {experiment}")
                return None

            df['ts'] = (df.ts - expt.start).dt.total_seconds()

        return df

    def export_data(self):
        """
        Exports the data of all experiments to a CSV file.
        """
        # Query the database and get data
        data = self.query_database()

        # Convert data into a DataFrame
        df = pd.DataFrame(data)

        # Save DataFrame as a CSV file
        df.to_csv('export.csv')

    def export_data_single(self, experiment_id, folder_path):
        """
        Exports the data of a single experiment to a CSV file.
        Args:
            experiment_id (int): The id of the experiment to export.
        Returns:
            None
        """
        try:
            # create dataframe for "experiment_id"
            df = self.latest_readings(experiment_id)
            if df is None:
                    self.logger.critical(f"Cannot export data for experiment {experiment_id} because there are no readings.")
                    return

            # Attempt to retrieve the experiment's start date
            with self.Session() as sess:
                exp = sess.get(Experiment, experiment_id)
                stamp = exp.start.strftime("%Y%m%d-%H%M")
                name = exp.name

            # create filename string and save to file
            filename = sanitize_filename(f"{name}-{stamp}.csv")
            full_path = os.path.join(folder_path, filename)
            df.to_csv(full_path)

        except (ValueError, AttributeError, OSError) as e:
            self.logger.debug(f"Export failed due to: {e}")

        else:
            # only run if `try:` is successful. set exported status to "True"
            self.mark_exported(experiment_id)
            self.logger.debug("`export_data_single` complete")

    def delete_experiment(self, experiment_id):
        '''
        Deletes the data of a single experiment from the database
        Args:
            experiment_id (int): The id of the experiment to export.
        Returns:
            None
        '''
        try:
            with self.Session() as sess:
                # Query for the experiment to delete
                experiment = sess.query(Experiment).filter(Experiment.id==experiment_id).first()

                if experiment is None:
                    self.logger.critical(f"Cannot delete data for experiment {experiment_id} because there are no readings.")
                    return

            # Delete the experiment and commit the changes
            sess.delete(experiment)
            sess.commit()
            self.logger.debug(f"Experiment {experiment_id} deleted successfully.")

        except Exception as e:
            self.logger.critical("Deleting experiment failed {e}")

    def query_database(self):
        '''
        Query the database and return a DataFrame of all readings,
        with the timestamps as integer seconds relative to the start time of each experiment.

        Returns:
            all_data (DataFrame): DataFrame containing all readings from the database.
        '''
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
        with self.Session() as sess:
            experiments = sess.query(Experiment).all()
            # Create a list of tuples, each containing the id, name, start time, end time of each experiment
            return [(expt.id, expt.name, expt.start, expt.end, expt.exported) for expt in experiments]

    def mark_exported(self, experiment_id):
        """
        Marks an experiment as exported in the database.

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
                    else:
                        self.logger.critical(f"No experiment found with ID {experiment_id}")
                else:
                    self.logger.debug("Experiment ID is None")

        except Exception as e:
            self.logger.debug(f"Failed to mark experiment as exported due to: {e}")

        # Return False if the function did not return True earlier
        return False

class DevCapture(PmtDb):
    '''Subclass PmtDb again to read from the Pi ADC.
    TODO: How can we tell if we're running on a real Pi?
    '''
    def __init__(self):
        PmtDb.__init__(self)

        self.logger = setup_logger()

        self.omega = 2.0 * math.pi / 60

    def take_reading(self):
        noise = (0.08 * random.random()) - 0.04
        signal = 0.92 * math.sin(self.omega * (datetime.now() - self.start_time).seconds)
        reading = 32768 + int(32768 * (signal + noise))
        self.write_reading(reading)
        self.logger.debug(reading)
        return reading
