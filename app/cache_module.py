"""Cache subsystem for the web process and Dash application."""

from datetime import datetime

import pandas as pd


class CacheWebProcess:
    """Manages in-memory data cache and database interactions.

    Attributes:
        database: An object for database interactions, defaults to PmtDb if not provided.
        cached_data: Dictionary holding cached DataFrames, keyed by experiment_id.
        last_datetime: Timestamp of the last cache update.
        current_datetime: Timestamp of the current cache state.
    """

    def __init__(self, database, logger) -> None:
        """Initializes CacheWebProcess with optional database object.

        Args:
            database: Optional database object for custom database interactions.
        """
        self.database = database

        self.logger = logger

        # Create empty Dictionary to hold DataFrames keyed by experiment_id
        self.cached_data: dict[int, pd.DataFrame] = {}

        # Initialize datetimes for precise fetching
        self.last_datetime: datetime | None = None
        self.current_datetime: datetime | None = None

    def get_cached_data(self, experiment_id) -> pd.DataFrame:
        """Retrieves cached data for a given experiment ID.

        Args:
            experiment_id: Identifier for the experiment.

        Returns:
            pd.DataFrame: The cached data, or an empty DataFrame if no data is cached for the given ID.
        """
        return self.cached_data.get(experiment_id, pd.DataFrame())

    def initialize_empty_cache(self) -> pd.DataFrame:
        """Initializes an empty cache DataFrame with predefined columns.

        The cache DataFrame is structured to match the expected database schema.

        Returns:
            pd.DataFrame: An empty DataFrame with columns 'ts' and 'value'.
        """
        empty_cache = pd.DataFrame(columns=["ts", "value"], dtype=float)
        return empty_cache

    def fetch_latest_data(self, experiment_id, last_timestamp=None) -> pd.DataFrame | None:
        """Fetches new data since the last update for a given experiment.

        Args:
            experiment_id: The ID of the experiment for which to fetch data.
            last_timestamp: Optional timestamp to fetch data from this point forward.

        Returns:
            pd.DataFrame: The latest data fetched from the database, or None if no new data.
        """
        dataframe: pd.DataFrame | None = self.database.latest_readings(experiment_id=experiment_id, since=last_timestamp)
        return dataframe

    def update_cache(self, experiment_id, last_timestamp=None) -> pd.DataFrame:
        """Updates the cache with new data based on the last timestamp and experiment ID.

        Args:
            experiment_id: The ID of the experiment for which to update the cache.
            last_timestamp: Optional timestamp used as a starting point for fetching new data.

        Returns:
            pd.DataFrame: The updated cached data for the given experiment ID, or None if no update.
        """
        # Search for existing cache based on the experiment id, if not found create one
        if experiment_id not in self.cached_data:
            self.cached_data[experiment_id] = self.initialize_empty_cache()
            self.logger.debug("Initializing cache for ID: %s", experiment_id)

        # Check for new data entries
        new_data = self.fetch_latest_data(experiment_id, last_timestamp)

        if new_data is None or new_data.empty:
            self.logger.debug("DataFrame requested is empty. No cache update.")
            return self.cached_data.get(experiment_id, pd.DataFrame())

        # Append new data to the existing cached dataframe
        self.cached_data[experiment_id] = pd.concat([self.cached_data[experiment_id], new_data])
        return self.cached_data[experiment_id]

    def handle_data_update(self, experiment_id) -> None:
        """Facade method to update the cache for a specific experiment.

        This method should be called to trigger side effects that update the cache.
        It does not return a value; use `get_cached_data` to retrieve the updated cache.

        Args:
            experiment_id (int): The ID of the experiment to update.

        Side Effects:
            - Updates `self.last_datetime` to the current datetime.
            - Calls `update_cache` to update the cache for the specified experiment.
        """
        self.save_datetime()
        self.update_cache(experiment_id, self.last_datetime)

    def save_datetime(self) -> None:
        """Updates the timestamp tracking mechanism.

        Rolls over the last recorded datetime to make room for a new current datetime.

        Side Effects:
            - Updates `self.last_datetime` to the value of `self.current_datetime`.
            - Updates `self.current_datetime` to the current system datetime.
        """
        self.last_datetime = self.current_datetime
        self.current_datetime = datetime.now()

    def handle_completed_experiment(self, experiment_id) -> None:
        """Facade method to update the cache for a completed experiment.

        This method should be called to trigger side effects that finalize the cache for a completed experiment.
        It does not return a value; use `get_cached_data` to retrieve the updated cache.

        Args:
            experiment_id (int): The ID of the completed experiment to update.

        Side Effects:
            - Finalizes the cache for the specified completed experiment.
        """
        self.update_cache(experiment_id)

    def cache_size(self) -> int:
        """Returns the size of the cache.

        Returns:
            int: The number of rows in the cache.
        """
        return sum(len(df) for df in self.cached_data.values())

    def clear_cache(self, key) -> pd.DataFrame:
        """Clears the cache for a specific experiment.

        Args:
            key: The experiment ID to clear the cache for.

        Returns:
            pd.DataFrame: An empty DataFrame.
        """
        self.cached_data.pop(key, None)
        return self.initialize_empty_cache()
