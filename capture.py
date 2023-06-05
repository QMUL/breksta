
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
import random
from typing import Optional

import pandas as pd
from sqlalchemy import create_engine, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

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

            df['ts'] = (df.ts - expt.start).dt.total_seconds()

        return df

    def export_data(self):
        # Query the database and get data
        data = self.query_database()

        # Convert data into a DataFrame
        df = pd.DataFrame(data)

        # Save DataFrame as a CSV file
        df.to_csv('export.csv')

    def export_data_single(self, experiment_id):

        # create dataframe for "experiment_id"
        df = self.latest_readings(experiment_id)

        # create filename string and save to file
        filename = f"experiment_{experiment_id}.csv"
        df.to_csv(filename)

    def query_database(self):
        '''Return a DataFrame of all readings in the database,
        with the timestamps as integer seconds relative to the start time of each experiment.'''
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


class DevCapture(PmtDb):
    '''Subclass PmtDb again to read from the Pi ADC.
    TODO: How can we tell if we're running on a real Pi?
    '''
    def __init__(self):
        PmtDb.__init__(self)

        self.omega = 2.0 * math.pi / 60

    def take_reading(self):
        noise = (0.08 * random.random()) - 0.04
        signal = 0.92 * math.sin(self.omega * (datetime.now() - self.start_time).seconds)
        reading = 32768 + int(32768 * (signal + noise))
        self.write_reading(reading)
        print(reading)
        return reading
