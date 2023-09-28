"""Cache sub-system for the web process and Dash app"""
from datetime import datetime

import pandas as pd  # For creating an empty DataFrame

from app.capture import PmtDb
from app.logger_config import setup_logger


class CacheWebProcess:
    """Handles the in-memory cache and the database connection.
    Initializes the state and provides the methods."""
    def __init__(self) -> None:
        # Establish connection to the database
        self.database = PmtDb()
        self.logger = setup_logger()
        # Create empty dataframe to store the data
        self.cached_data = self.initialize_empty_cache()
        self.logger.debug("Database connected to chart process. Starting caching.")

        # Initialize datetimes for precise fetching
        self.last_datetime = None
        self.current_datetime = None

    def initialize_empty_cache(self) -> pd.DataFrame:
        """Initializes the cache to match expected requirements.
        TODO: Change to accommodate multiple keys like experiment_id values.
        # Args:
        #     cached_data (None)
        Returns:
            cache_initial (pd.DataFrame): The fully specced cache dataframe."""
        cache_empty = pd.DataFrame(columns=['ts', 'value'])
        return cache_empty

    def update_cache(self, cached_data: pd.DataFrame, experiment_id, last_timestamp=None) -> pd.DataFrame:
        """Fetches the new data based on last_timestamp and updates the cache accordingly.
        Args:
            cached_data (pd.DataFrame): The cached Dataframe until the current timestamp
            last_timestamp (datetime): The timestamp of the last update, used by the database fetch
        Returns:
            updated_cache (pd.DataFrame): The updated DataFrame
        """
        new_data = self.database.latest_readings(experiment=experiment_id, since=last_timestamp)

        if new_data is None:
            self.logger.warning("DataFrame requested is empty. No cache update.")
            return cached_data

        updated_cache: pd.DataFrame = pd.concat([cached_data, new_data])
        return updated_cache

    def handle_data_update(self, experiment_id) -> pd.DataFrame:
        """A "Facade" to wrap all functionality within the class and expose it.
        Args:
            experiment_id (int): The experiment_id key
        Returns:
            cached_data (pd.DataFrame): The global dataframe to be plotted
        """
        self.save_datetime()

        self.cached_data = self.update_cache(self.cached_data, experiment_id, self.last_datetime)

        return self.cached_data

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
