"""
Tests dash components:

- figure.py: Handles initialization of the go.Figure object
"""

import unittest
from unittest.mock import MagicMock, patch

import plotly.graph_objects as go

import app.components as app


class TestInitializeFigure(unittest.TestCase):
    """Test initialize_figure function"""

    def setUp(self) -> None:
        # Create a mock logger
        self.mock_logger = MagicMock()

        # Mock the logger within components
        self.logger_patch = patch(
            "app.components.figure.logger", return_value=self.mock_logger)

        self.logger_patch.start()

        self.original_logger = app.figure.logger
        app.figure.logger = self.mock_logger

    def tearDown(self) -> None:
        app.figure.logger = self.original_logger
        self.logger_patch.stop()
        return super().tearDown()

    def test_initialize_figure(self) -> None:
        """Test function call.
        Creates figure object, adds one trace, trace mode is lines,
        axes ranges are automatic, axes titles are set,
        log is emitted.
        """
        fig = app.figure.initialize_figure()

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
