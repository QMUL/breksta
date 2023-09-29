"""Encapsulates all Dash layout logic and methods"""
from dash import Dash, html, dcc

from app.components import slider_interval


def create_layout(app: Dash) -> html.Div:
    """Create and return the layout for a Dash app.

    This function sets up the primary user interface for the Dash app.
    It includes elements like the slider for interval control, URL location for routing,
    and the main graph display, facilitating both user interaction and data visualization.

    Args:
        app (Dash): The Dash app instance.

    Returns:
        html.Div: The layout wrapped in an HTML Div, ready to be rendered by the Dash app.
    """

    # Create a top-level HTML Div to hold all elements
    return html.Div(
        className="app-div",
        children=[
            # Display the app title for context
            html.H3(app.title),
            # Add a horizontal rule for visual separation
            html.Hr(),
            # Include the interval slider component for user control over refresh rate
            slider_interval.render(),
            # Capture the current URL for dynamic routing and content rendering
            dcc.Location(
                id='url',
                refresh=False),
            # Main graph display for data visualization
            dcc.Graph(id='dynamic-graph'),
            # Interval component to trigger periodic data updates
            dcc.Interval(
                id='interval-component',
                interval=2000,
                n_intervals=0
            ),
            # Store component to hold and manage the graph's layout settings
            dcc.Store(id='stored-layout')
        ],
    )
