"""Encapsulates the logic and components for the interval control slider.

This module provides utility functions and data classes to create, initialize, and manage
the slider that controls the refresh rate of the main graph in the Dash app.
"""

from dataclasses import dataclass

from dash import dcc, html


@dataclass
class SliderValues:
    """Encapsulates the Slider values to improve code maintainability and readability.

    This data class serves to remove magic numbers from the global namespace.
    It may seem like overengineering, but it sets the stage for easier adjustments and testing.
    Also, it offers a much needed example in dataclasses, which the author needed at the time.
    """
    MIN: int = 2
    MAX: int = 60
    STEP: int = 1
    VALUE: int = 2


def render() -> html.Div:
    """Create and deploy the Interval slider.

    This function sets up a slider for controlling the refresh rate of the main graph.
    Any time a new value is chosen, the `update_refresh_rate` callback in the main app is triggered,
    allowing for dynamic control over data fetching intervals.
    """

    # Create a slider with predefined minimum, maximum, step, and initial values.
    return html.Div(
        [
            # Label for the slider to indicate its purpose
            html.H6("Refresh Rate"),
            # Slider component for controlling the refresh rate
            dcc.Slider(
                id='interval-refresh',  # Hook to update_refresh_rate@chart
                min=SliderValues.MIN,
                max=SliderValues.MAX,
                step=None,
                value=SliderValues.VALUE,
                marks={
                    2: "2s",
                    10: "10s",
                    30: "30s",
                    60: "60s"
                }
            )
        ],
        style={'width': '20%'}
    )
