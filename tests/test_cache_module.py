"""Test cache module"""
from unittest import TestCase
from unittest.mock import MagicMock, patch
import pandas as pd

from app.cache_module import CacheWebProcess


class TestCacheWebProcess(TestCase):
    """Implements sanity checks for the cache class.
    Tests follow try to follow AAA: "Arrange, Act, Assert"."""

    def setUp(self) -> None:
        self.mock_logger = MagicMock()
        # Mock the logger within CacheWebProcess module
        self.logger_patch = patch("app.cache_module.setup_logger", return_value=self.mock_logger)
        self.logger_patch.start()

        self.mock_db = MagicMock()
        # Initialize database behaviour to return a filled Dataframe.
        # Reset as needed on each test.
        self.mock_db.latest_readings.return_value = pd.DataFrame({'data': [1, 2, 3]})
        self.cache_instance = CacheWebProcess(database=self.mock_db)

    def tearDown(self) -> None:
        self.mock_db = None
        self.cache_instance = None
        self.logger_patch.stop()
        return super().tearDown()

    def test_handle_data_update(self) -> None:
        """Tests that the cache is updated correctly, when given a valid experiment_id"""
        experiment_id = 1

        self.cache_instance.handle_data_update(experiment_id)
        result = self.cache_instance.get_cached_data(experiment_id)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)

    def test_cache_handles_none_data(self) -> None:
        """Tests that no data fetched leads to no cache being returned"""
        # Mocking the database to return None
        self.mock_db.latest_readings.return_value = None
        experiment_id = 123

        self.cache_instance.handle_data_update(experiment_id)

        # The cache should handle this gracefully and return None
        self.assertIsNone(self.cache_instance.get_cached_data(experiment_id))

    def test_cache_handles_empty_data(self) -> None:
        """Tests that an empty DataFrame update leads to empty cache"""
        # Mocking the database to return an empty DataFrame
        self.mock_db.latest_readings.return_value = pd.DataFrame()
        experiment_id = 1

        self.cache_instance.handle_data_update(experiment_id)

        # Check that the cache returns an empty DataFrame
        assert self.cache_instance.get_cached_data(experiment_id).empty
