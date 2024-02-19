"""Test cache module"""
from unittest import TestCase
from unittest.mock import MagicMock

import pandas as pd

from app.cache_module import CacheWebProcess


class TestCacheWebProcess(TestCase):
    """Implements sanity checks for the cache class.
    Tests follow try to follow AAA: "Arrange, Act, Assert"."""

    def setUp(self) -> None:
        self.mock_logger = MagicMock()
        self.mock_db = MagicMock()
        # Initialize database behaviour to return a filled Dataframe.
        self.mock_db.latest_readings.return_value = pd.DataFrame({"data": [1, 2, 3]})
        self.cache_instance = CacheWebProcess(database=self.mock_db, logger=self.mock_logger)

    def test_handle_data_update(self) -> None:
        """Tests that the cache is updated correctly, when given a valid experiment_id"""
        experiment_id = 1

        self.cache_instance.handle_data_update(experiment_id)
        result = self.cache_instance.get_cached_data(experiment_id)

        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)

    def test_cache_handles_none_data(self) -> None:
        """Tests that no data fetched leads to an empty DataFrame being returned"""
        # Mocking the database to return None
        self.mock_db.latest_readings.return_value = None
        experiment_id = 123

        self.cache_instance.handle_data_update(experiment_id)

        # The cache should handle this gracefully and return an empty DataFrame
        returned_df = self.cache_instance.get_cached_data(experiment_id)
        self.assertIsInstance(returned_df, pd.DataFrame)
        self.assertTrue(returned_df.empty)

    def test_cache_handles_empty_data(self) -> None:
        """Tests that an empty DataFrame update leads to empty cache"""
        # Mocking the database to return an empty DataFrame
        self.mock_db.latest_readings.return_value = pd.DataFrame()
        experiment_id = 1

        self.cache_instance.handle_data_update(experiment_id)

        # Check that the cache returns an empty DataFrame
        assert self.cache_instance.get_cached_data(experiment_id).empty
