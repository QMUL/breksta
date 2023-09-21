"""Cache sub-system for the web process and Dash app"""
from datetime import datetime

import pandas as pd

from app.capture import PmtDb
from app.logger_config import setup_logger


class CacheWebProcess:
    """Handles the in-memory cache and the database connection.
    Initializes the state and provides the methods."""
    def __init__(self) -> None:
        # Establish connection to the database
        self.database = PmtDb()
        self.logger = setup_logger()

        # Create empty Dictionary to hold DataFrames keyed by experiment_id
        self.cached_data = {}
        self.logger.debug("Database connected to chart process. Starting caching.")

        # Initialize datetimes for precise fetching
        self.last_datetime = None
        self.current_datetime = None

    def get_cached_data(self, experiment_id) -> pd.DataFrame:
        """Getter function. Use this to access the updated DataFrame"""
        return self.cached_data.get(experiment_id, None)

    def initialize_empty_cache(self) -> pd.DataFrame:
        """Initializes the cache to match expected requirements.
        TODO: Change to accommodate multiple keys like experiment_id values.
        # Args:
        #     cached_data (None)
        Returns:
            cache_initial (pd.DataFrame): The fully specced cache dataframe."""
        cache_empty = pd.DataFrame(columns=['ts', 'value'])
        return cache_empty

    def fetch_latest_data(self, experiment_id, last_timestamp=None) -> pd.DataFrame:
        """Fetches new data since last update, in a Dataframe"""
        return self.database.latest_readings(experiment=experiment_id, since=last_timestamp)

    def update_cache(self, experiment_id, last_timestamp=None) -> pd.DataFrame:
        """Fetches the new data based on last_timestamp and updates the cache accordingly.
        Args:
            cached_data (pd.DataFrame): The cached Dataframe until the current timestamp
            last_timestamp (datetime): The timestamp of the last update, used by the database fetch
        Returns:
            updated_cache (pd.DataFrame): The updated DataFrame
        """
        new_data = self.fetch_latest_data(experiment_id, last_timestamp)

        if new_data is None:
            self.logger.warning("DataFrame requested is empty. No cache update.")
            return self.cached_data.get(experiment_id, None)

        # Search for existing cache based on the experiment id, if not found create one
        if experiment_id not in self.cached_data:
            self.cached_data[experiment_id] = self.initialize_empty_cache()

        # Append new data to the existing cached dataframe
        self.cached_data[experiment_id] = pd.concat([self.cached_data[experiment_id], new_data])
        return self.cached_data[experiment_id]

    def handle_data_update(self, experiment_id) -> None:
        """Facade method to encapsulate cache update logic.

        This is an action method that triggers side effects to update the cache's internal state.
        It does not return any value; use the getter method `get_cached_data` to retrieve cached data.

        Args:
            experiment_id (int): Identifier for the experiment whose data needs to be cached.

        Side Effects:
            - Updates `self.last_datetime` to store the latest datetime.
            - Calls `update_cache` to modify the cache's internal state.
        """
        self.save_datetime()
        _ = self.update_cache(experiment_id, self.last_datetime)

    def save_datetime(self) -> None:
        """Rollover last interval's datetime, and then take note of current datetime."""
        self.last_datetime = self.current_datetime  # Move current to last
        self.current_datetime = datetime.now()  # Update current

    def cache_size(self):
        """TODO: The function should return the size of the cache.
        size/number of rows?
        actual size in MBs?
        Args:
            cached_data (pd.DataFrame): The cached Dataframe which resides in memory.
        Returns:
            size?
            boolean checked vs threshold?
        """

    def clear_cache(self, key) -> pd.DataFrame:
        """TODO: Clears the cache if conditions met.
        Args:
            Cache key (experiment_id-specific?)
        Returns:
            dataframe (pd.DataFrame): An empty
            """
        empty_cache = self.initialize_empty_cache()
        return empty_cache
