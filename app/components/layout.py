"""Encapsulates all Dash layout logic and methods"""
from dash import Dash, html, dcc

from app.components import slider_interval


def create_layout(app: Dash) -> html.Div:
    """Create and return the layout for a Dash app.

    Args:
        app (Dash): The Dash app instance.

    Returns:
        html.Div: The layout wrapped in an HTML Div.
    """
    return html.Div(
        className="app-div",
        children=[
            html.H3(app.title),
            html.Hr(),
            slider_interval.render(app),
            dcc.Location(
                id='url',
                refresh=False),
            dcc.Graph(id='dynamic-graph'),
            dcc.Interval(
                id='interval-component',
                interval=2000,
                n_intervals=0
            ),
            dcc.Store(id='stored-layout')
        ],
    )
