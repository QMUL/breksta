"""Module that houses the export button in the dash app and layout

Entry point be the layout module
"""

from dash import html


def render() -> html.Div:
    """Create the export button
    """
    return html.Div(
        id="button-div",
        children=[
            html.Button(
                id="export-button",
                children="Export Data",
                n_clicks=0
            )
        ]
    )
