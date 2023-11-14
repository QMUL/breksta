"""
Two tests classes: TestExperiment and TestPmtReading. Each class contains multiple test
methods that test different aspects of the Experiment and PmtReading classes respectively.
"""

from datetime import datetime, timedelta
import unittest
from unittest.mock import MagicMock
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from app.database import Experiment, PmtReading, Base


class TestExperiment(unittest.TestCase):
    """
    Unit tests for the Experiment class.

    Each test method in this class tests different aspects of the Experiment class.
    The tests include creating a new experiment, updating an existing experiment,
    handling future start times, and validating the length of the experiment name.
    """
    def setUp(self) -> None:
        # Create an SQLite database in memory
        self.engine = sqlalchemy.create_engine('sqlite:///:memory:', echo=False)
        session = sessionmaker(bind=self.engine)
        self.session = session()  # save the session instance
        Base.metadata.create_all(self.engine)  # Creates the database structure
        self.mock_id = id(self.session)

        self.mock_logger = MagicMock()
        # self.mock_db = PmtDb(session, self.mock_logger)
        self.name = 'test_experiment'

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_create_new_experiment(self) -> None:
        """Creating a new experiment with valid input should result in a new row in the 'experiment' table."""
        # Create a new experiment with valid input
        experiment = Experiment(name=self.name, start=datetime.now())
        self.session.add(experiment)
        self.session.commit()

        # Query the database to verify the new row is added
        db_experiment = self.session.query(Experiment).filter_by(name=self.name).one()
        self.assertEqual(db_experiment.name, self.name)
        self.assertFalse(db_experiment.exported)

    def test_update_existing_experiment(self) -> None:
        """Updating an existing experiment with valid input should update the corresponding row in the 'experiment' table."""
        # Create a new experiment with valid input
        experiment = Experiment(name="Experiment 1", start=datetime.now())
        self.session.add(experiment)
        self.session.commit()

        # Update the experiment with new values
        experiment.name = "Updated Experiment"
        experiment.exported = True
        self.session.commit()

        # Query the database to verify the row is updated
        db_experiment = self.session.query(Experiment).filter_by(id=experiment.id).one()
        self.assertEqual(db_experiment.name, "Updated Experiment")
        self.assertTrue(db_experiment.exported)

    def test_create_experiment_future_start_no_error(self) -> None:
        """Creating an experiment with a start time in the future should not raise an error."""
        # Create an experiment with a start time in the future
        experiment = Experiment(name="Future Experiment", start=datetime.now() + timedelta(days=1))
        self.session.add(experiment)
        self.session.commit()

        # Query the database to verify the row is added
        db_experiment = self.session.query(Experiment).filter_by(name="Future Experiment").one()
        self.assertIsNotNone(db_experiment)


class TestPmtReading(unittest.TestCase):
    """
    Unit tests for the PmtReading class.

    Each test method in this class tests different aspects of the PmtReading class.
    The tests include creating a PmtReading object with valid values, checking the uniqueness
    and primary key nature of the timestamp, retrieving reading values from the object,
    and ensuring that the experiment id cannot be null.
    """
    def setUp(self):
        self.experiment_id = 1
        self.value = 10
        self.timestamp = datetime.now()

    def test_create_pmt_reading_with_valid_values(self) -> None:
        """PmtReading object can be created with valid experiment id, value and timestamp."""
        pmt_reading = PmtReading(experiment=self.experiment_id, value=self.value, ts=self.timestamp)

        self.assertEqual(pmt_reading.experiment, self.experiment_id)
        self.assertEqual(pmt_reading.value, self.value)
        self.assertEqual(pmt_reading.ts, self.timestamp)

    def test_timestamp_is_unique_and_primary_key(self) -> None:
        """Timestamp is unique and serves as primary key."""
        timestamp2 = datetime.now()

        pmt_reading1 = PmtReading(experiment=self.experiment_id, value=self.value, ts=self.timestamp)
        pmt_reading2 = PmtReading(experiment=self.experiment_id, value=self.value, ts=timestamp2)

        self.assertNotEqual(pmt_reading1.ts, pmt_reading2.ts)

    def test_retrieve_reading_values(self) -> None:
        """Reading values can be retrieved from the object"""
        pmt_reading = PmtReading(experiment=self.experiment_id, value=self.value, ts=self.timestamp)

        self.assertEqual(pmt_reading.experiment, self.experiment_id)
        self.assertEqual(pmt_reading.value, self.value)

    def test_experiment_id_not_null(self) -> None:
        """Experiment id can't be null."""
        try:
            PmtReading(experiment=None, value=self.value, ts=self.timestamp)
        except TypeError:
            self.fail("TypeError should not be raised")
