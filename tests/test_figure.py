"""
Tests figure components and helpers:

- Test initialize_figure function
- Test plot_data function
- Test layout changing through manual manipulation of the graph
"""

import unittest
from unittest import mock
from unittest.mock import MagicMock, patch

import pandas as pd
import plotly.graph_objects as go

from app.components import figure


class TestInitializeFigure(unittest.TestCase):
    """Test initialize_figure function"""

    def setUp(self) -> None:
        # Create a mock logger
        self.mock_logger = MagicMock()

        # Mock the logger within components
        self.logger_patch = patch(
            "app.components.figure.logger", return_value=self.mock_logger)

        self.logger_patch.start()

        self.original_logger = figure.logger
        figure.logger = self.mock_logger

    def tearDown(self) -> None:
        figure.logger = self.original_logger
        self.logger_patch.stop()
        return super().tearDown()

    def test_initialize_figure(self) -> None:
        """Test function call.
        Creates figure object, adds one trace, trace mode is lines,
        axes ranges are automatic, axes titles are set,
        log is emitted.
        """
        fig = figure.initialize_figure()

        self.assertIsInstance(fig, go.Figure)
        self.assertEqual(len(fig.data), 1)

        # Check the mode of the trace
        self.assertEqual(fig.data[0].mode, 'lines')

        # Check the axes ranges are set for automatic
        self.assertIsNone(fig.layout.xaxis.range)
        self.assertIsNone(fig.layout.yaxis.range)

        # Check axes' titles
        self.assertEqual(fig.layout.xaxis.title.text, 'Time (s)')
        self.assertEqual(fig.layout.yaxis.title.text, 'Voltage (V)')

        # Verify that the logger was called with the expected debug message
        self.mock_logger.debug.assert_called_with(
            "Plotly figure created and initialized.")


class TestPlotData(unittest.TestCase):
    """Test plot_data function"""

    def setUp(self) -> None:
        # Create a mock logger
        self.mock_logger = MagicMock()

        # Mock the logger within chart module
        self.logger_patch = patch(
            "app.components.figure.logger", return_value=self.mock_logger)

        self.logger_patch.start()

        self.original_logger = figure.logger
        figure.logger = self.mock_logger
        self.init_fig = figure.initialize_figure()

    def tearDown(self) -> None:
        figure.logger = self.original_logger
        self.init_fig = None
        self.logger_patch.stop()
        return super().tearDown()

    def test_plot_data_empty_df(self) -> None:
        """Test with an empty DataFrame, figure should return early"""

        empty_df = pd.DataFrame()
        fig = figure.plot_data(self.init_fig, empty_df)

        # Verify that the logger was called with the expected debug message
        self.mock_logger.error.assert_called_with(
            "DataFrame empty, or keys missing from columns. Returning empty...")

        # Verify that an empty figure is returned
        self.assertEqual(fig.data, self.init_fig.data)

    def test_invalid_dataframe_columns(self) -> None:
        """Test that an invalid DataFrame returns early with a debug message."""
        # Create an invalid DataFrame that does not contain 'ts' and 'value' columns
        df = pd.DataFrame({'timestamp': [1, 2], 'val': [3, 4]})

        fig = figure.plot_data(self.init_fig, df)

        # Verify that the logger was called with the expected debug message
        self.mock_logger.error.assert_called_with(
            "DataFrame empty, or keys missing from columns. Returning empty...")

        # Verify that an empty figure is returned
        self.assertEqual(fig.data, self.init_fig.data)

    def test_plot_data_valid_df(self) -> None:
        """Test with a valid DataFrame."""
        df = pd.DataFrame({
            'ts': [1, 2, 3],
            'value': [10, 20, 30]})

        fig = figure.plot_data(self.init_fig, df)

        self.assertListEqual(list(fig.data[0]['x']), [1, 2, 3])
        self.assertListEqual(list(fig.data[0]['y']), [10, 20, 30])

    def test_plot_data_when_int_string_df(self) -> None:
        """Test with an invalid DataFrame that contains integer strings."""
        df = pd.DataFrame({
            'ts': ['1', '2', '3'],
            'value': ['10', '20', '30']})

        fig = figure.plot_data(self.init_fig, df)

        self.assertListEqual(list(fig.data[0]['x']), [1, 2, 3])
        self.assertListEqual(list(fig.data[0]['y']), [10, 20, 30])

    def test_plot_data_when_float_string_df(self) -> None:
        """Test with an invalid DataFrame that contains float strings."""
        df = pd.DataFrame({
            'ts': ['1.0', '2.0', '3.0'],
            'value': ['10.0', '20.0', '30.0']})

        fig = figure.plot_data(self.init_fig, df)

        self.assertListEqual(list(fig.data[0]['x']), [1.0, 2.0, 3.0])
        self.assertListEqual(list(fig.data[0]['y']), [10.0, 20.0, 30.0])

    def test_plot_data_when_string_df(self) -> None:
        """Test with an invalid DataFrame that contains non-numerical strings."""
        df = pd.DataFrame({
            'ts': ['a', 'b', '4124'],
            'value': ['gg', 'lol', 'wat']})

        fig = figure.plot_data(self.init_fig, df)

        # Verify that an empty figure is returned
        self.assertEqual(fig.data, self.init_fig.data)

        # Verify that the logger was called with the expected debug message
        self.mock_logger.error.assert_called_with(
            "Data type conversion error. Returning existing figure...")


class TestFigureLayout(unittest.TestCase):
    """Test layout changing through manual manipulation of the graph"""

    def setUp(self) -> None:
        # Create a mock logger
        self.mock_logger = MagicMock()

        # Mock the logger within figure module
        self.logger_patch = patch(
            "app.components.figure.logger", return_value=self.mock_logger)

        self.logger_patch.start()

        self.original_logger = figure.logger
        figure.logger = self.mock_logger

        self.figure = figure.initialize_figure()

    def tearDown(self) -> None:
        figure.logger = self.original_logger
        self.logger_patch.stop()
        self.figure = None
        return super().tearDown()

    def test_initial_layout_state(self) -> None:
        """Tests the initial layout state is that of an empty dictionary"""
        fig_mock = mock.MagicMock()  # Mock the go.Figure object
        stored_layout: dict = {}  # Initial empty state

        figure.update_axes_layout(fig_mock, stored_layout)

        # Assertions
        fig_mock.update_xaxes.assert_not_called()  # The x-axes should not be updated
        fig_mock.update_yaxes.assert_not_called()  # The y-axes should not be updated

    def test_manual_change_layout_state(self) -> None:
        """Tests the resulting layout state when the layout is changed manually"""
        # Manually set axis ranges
        stored_layout = {
            'xaxis.range[0]': 0, 'xaxis.range[1]': 10, 'yaxis.range[0]': -5, 'yaxis.range[1]': 5}

        figure.update_axes_layout(self.figure, stored_layout)

        # Assertions based on final state of figure layout
        self.assertEqual(self.figure['layout']['xaxis']['range'], (0, 10))
        self.assertEqual(self.figure['layout']['xaxis']['autorange'], False)
        self.assertEqual(self.figure['layout']['yaxis']['range'], (-5, 5))
        self.assertEqual(self.figure['layout']['yaxis']['autorange'], False)

    def test_manual_reset_layout_state(self) -> None:
        """Tests the layout state after a manual reset (double-click on Dash graph) resets the layout to autoscale"""
        fig_mock = mock.MagicMock()  # Mock the go.Figure object
        fig_mock.update_xaxes.autorange = False  # Simulate that autorange is initially set to False
        fig_mock.update_yaxes.autorange = False  # Simulate that autorange is initially set to False

        stored_layout = {'autosize': True}  # Simulate a manual reset

        figure.update_axes_layout(fig_mock, stored_layout)

        # Assertions
        fig_mock.update_xaxes.assert_called_once_with(autorange=True)  # The x-axis should be set to autorange
        fig_mock.update_yaxes.assert_called_once_with(autorange=True)  # The y-axis should be set to autorange

    def test_manual_change_repeated_layout_state(self) -> None:
        """Integration-like test for sequence of manual changes and reset"""
        # Step 1: Initial manual set
        stored_layout_initial = {'xaxis.range[0]': -10, 'xaxis.range[1]': 10}
        figure.update_axes_layout(self.figure, stored_layout_initial)
        self.assertEqual(self.figure['layout']['xaxis']['range'], (-10, 10))
        self.assertEqual(self.figure['layout']['xaxis']['autorange'], False)

        # Step 2: Reset layout
        stored_layout_reset = {'autosize': True}
        figure.update_axes_layout(self.figure, stored_layout_reset)
        self.assertEqual(self.figure['layout']['xaxis']['autorange'], True)

        # Step 3: Manual set again
        stored_layout_new = {'xaxis.range[0]': 0, 'xaxis.range[1]': 20}
        figure.update_axes_layout(self.figure, stored_layout_new)
        self.assertEqual(self.figure['layout']['xaxis']['range'], (0, 20))
        self.assertEqual(self.figure['layout']['xaxis']['autorange'], False)
