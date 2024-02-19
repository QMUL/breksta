"""This module contains unit tests for the PmtDb class from the breksta module.

Each public method of PmtDb is tested to ensure that changes in the code do not unintentionally
break the application.
"""
import unittest
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, Experiment, PmtDb


class TestPmtDb(unittest.TestCase):
    """Defines the test cases for the PmtDb class.

    The setUp method is called before executing each test method.
    Here, it sets up a mock database in memory and creates instances of the PmtDb class. The PmtDb instance is
    initialized with the mock database session.

    The tearDown method is called after each test method. It closes the database session and
    drops the mock database to ensure isolation between tests.
    """

    def setUp(self) -> None:
        # Create an SQLite database in memory
        self.engine = create_engine("sqlite:///:memory:", echo=False)
        session = sessionmaker(bind=self.engine)
        self.session = session()  # save the session instance
        Base.metadata.create_all(self.engine)  # Creates the database structure
        self.mock_id = id(self.session)

        self.mock_logger = MagicMock()
        self.mock_db = PmtDb(session, self.mock_logger)
        self.name = "test_experiment"

    def tearDown(self) -> None:
        self.session.close()
        self.engine.dispose()

    def test_start_experiment_raises_exception_if_experiment_id_not_none(self) -> None:
        """Test that start_experiment can handle being passed a non-None
        experiment_id and gracefully handles it
        """
        self.mock_db.experiment_id = 1  # set a non-None value
        # Assertion
        with self.assertRaises(ValueError):
            self.mock_db.start_experiment(self.name)

    def test_start_experiment_creates_new_experiment(self) -> None:
        """Test that start_experiment creates a new experiment_id when called.
        Also when called successively, the IDs are also successive.
        """
        # Setup: Call start_experiment
        self.mock_db.start_experiment(self.name)
        # Assertion #1
        self.assertIsNotNone(self.mock_db.experiment_id)
        # Keep track of value
        old_experiment_id: int = self.mock_db.experiment_id if self.mock_db.experiment_id is not None else -1
        # Setup #2: Stop and re-start
        self.mock_db.stop_experiment()
        self.mock_db.experiment_id = self.mock_db.start_experiment(self.name)
        # Assertion #2
        self.assertIsNotNone(self.mock_db.experiment_id)
        self.assertEqual(self.mock_db.experiment_id, old_experiment_id + 1)

    def test_start_experiment_creates_new_experiment_chain(self) -> None:
        """Test that start_experiment creates a new experiment_id when called,
        and when called successively, the IDs are also successive."""

        # Setup: Call start_experiment
        self.mock_db.start_experiment(self.name)

        # Assertion #1: Check experiment ID is set and record exists in DB
        self.assertIsNotNone(self.mock_db.experiment_id)
        first_experiment = self.session.get(Experiment, self.mock_db.experiment_id)
        self.assertIsNotNone(first_experiment)

        # Keep track of the experiment ID
        if self.mock_db.experiment_id is None:
            raise ValueError
        old_experiment_id: int = self.mock_db.experiment_id

        # Setup #2: Stop and re-start
        self.mock_db.stop_experiment()
        self.mock_db.start_experiment(self.name)

        # Assertion #2: Check new experiment ID is incremented
        self.assertIsNotNone(self.mock_db.experiment_id)
        self.assertEqual(self.mock_db.experiment_id, old_experiment_id + 1)

        # Assertion #3: Verify the new experiment record exists and is correct
        new_experiment = self.session.get(Experiment, self.mock_db.experiment_id)
        self.assertIsNotNone(new_experiment)
        self.assertNotEqual(first_experiment, new_experiment)
        self.assertEqual(new_experiment.id, old_experiment_id + 1)

    def test_start_experiment_with_existing_id_raises_value_error(self) -> None:
        """Tests that an error is raised when starting an experiment encounters a experiment id of NOT None"""
        # Setup: Start an experiment to set the experiment_id
        self.mock_db.start_experiment(self.name)
        # Attempt to start another experiment and expect a ValueError
        with self.assertRaises(ValueError):
            self.mock_db.start_experiment(self.name)

    def test_stop_experiment_without_active_raises_value_error(self) -> None:
        """Tests that an error is raised when stopping an experiment encounters a experiment id of None"""
        # Setup: Ensure there's no active experiment
        self.mock_db.experiment_id = None
        # Attempt to stop an experiment and expect a ValueError
        with self.assertRaises(ValueError):
            self.mock_db.stop_experiment()
