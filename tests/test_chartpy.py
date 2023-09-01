"""Test of chart.py"""

import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
import plotly.graph_objects as go

import app.chart


class TestPlotData(unittest.TestCase):
    """Test plot_data function"""

    def setUp(self) -> None:
        # Create a mock logger
        self.mock_logger = MagicMock()

        # Mock the logger within chart module
        self.logger_patch = patch(
            "app.chart.logger", return_value=self.mock_logger)

        self.logger_patch.start()

        self.original_logger = app.chart.logger
        app.chart.logger = self.mock_logger
        self.init_fig = app.chart.initialize_figure()

    def tearDown(self) -> None:
        app.chart.logger = self.original_logger
        self.init_fig = None
        self.logger_patch.stop()
        return super().tearDown()

    def test_plot_data_empty_df(self) -> None:
        """Test with an empty DataFrame, figure should return early"""

        empty_df = pd.DataFrame()
        fig = app.chart.plot_data(self.init_fig, empty_df)

        # Verify that the logger was called with the expected debug message
        self.mock_logger.debug.assert_called_with(
            "DataFrame empty, or keys missing from columns. Returning empty...")

        # Verify that an empty figure is returned
        self.assertEqual(fig.data, self.init_fig.data)

    def test_invalid_dataframe_columns(self) -> None:
        """Test that an invalid DataFrame returns early with a debug message."""
        # Create an invalid DataFrame that does not contain 'ts' and 'value' columns
        df = pd.DataFrame({'timestamp': [1, 2], 'val': [3, 4]})

        fig = app.chart.plot_data(self.init_fig, df)

        # Verify that the logger was called with the expected debug message
        self.mock_logger.debug.assert_called_with(
            "DataFrame empty, or keys missing from columns. Returning empty...")

        # Verify that an empty figure is returned
        self.assertEqual(fig.data, self.init_fig.data)

    def test_plot_data_valid_df(self) -> None:
        """Test with a valid DataFrame."""
        df = pd.DataFrame({
            'ts': [1, 2, 3],
            'value': [10, 20, 30]})

        fig = app.chart.plot_data(self.init_fig, df)

        self.assertListEqual(list(fig.data[0]['x']), [1, 2, 3])
        self.assertListEqual(list(fig.data[0]['y']), [10, 20, 30])


class TestInitializeFigure(unittest.TestCase):
    """Test initialize_figure function"""

    def setUp(self) -> None:
        # Create a mock logger
        self.mock_logger = MagicMock()

        # Mock the logger within chart module
        self.logger_patch = patch(
            "app.chart.logger", return_value=self.mock_logger)

        self.logger_patch.start()

        self.original_logger = app.chart.logger
        app.chart.logger = self.mock_logger

    def tearDown(self) -> None:
        app.chart.logger = self.original_logger
        self.logger_patch.stop()
        return super().tearDown()

    def test_initialize_figure(self) -> None:
        """Test function call.
        Creates figure object, adds one trace, trace mode is lines,
        axes ranges are automatic, axes titles are set,
        log is emitted.
        """
        fig = app.chart.initialize_figure()

        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)

        # Check the mode of the trace
        self.assertEqual(fig.data[0].mode, 'lines')

        # Check the axes ranges are set for automatic
        self.assertIsNone(fig.layout.xaxis.range)
        self.assertIsNone(fig.layout.yaxis.range)

        # Check axes' titles
        self.assertEqual(fig.layout.xaxis.title.text, 'Time (s)')
        self.assertEqual(fig.layout.yaxis.title.text, 'Value (u)')

        # Verify that the logger was called with the expected debug message
        self.mock_logger.debug.assert_called_with(
            "Plotly figure created and initialized.")
