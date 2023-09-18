"""Dash example of a periodically updated chart:
    https://dash.plotly.com/live-updates
If the chart is to be accessed remotely, should cache previous data-points
to reduce network traffic:
    https://dash.plotly.com/persistence
TODO: Add components only visible remotely to faciliate remote .csv download.
"""

import urllib.parse
import os

from typing import Optional
# Import plotly before dash due to dependency issues
import plotly.graph_objects as go
from dash import Dash, html, dcc, State
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import pandas as pd  # For creating an empty DataFrame

from app.capture import PmtDb
from app.logger_config import setup_logger

logger = setup_logger()

# Set refresh rate literals. Normal operations is 2s, freeze is 10 minutes
NORMAL_REFRESH = 2
FREEZE_REFRESH = 600
GO_SIGNAL = '1'
STOP_SIGNAL = '0'

app = Dash(__name__)
"""A Dash application instance.
This app has a layout that consists of a location component for URL handling,
a graph for chart content, and an interval component for periodic updates.
"""

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Graph(id='dynamic-graph'),
    dcc.Interval(id='interval-component', interval=2000, n_intervals=0),
    dcc.Store(id='stored-layout')])  # Store component to hold the graph's layout state


@app.callback(Output('dynamic-graph', 'figure'),
              [Input('url', 'pathname'),
              Input('interval-component', 'n_intervals')],
              [State('stored-layout', 'data')])
def draw_chart(pathname: str, n_intervals: int, stored_layout: dict) -> go.Figure:
    """Callback function to draw the chart.
    The chart content is updated based on the pathname and the number of intervals passed.
    The experiment ID is extracted from the GET parameters of the URL,
    and the corresponding data is fetched from the database.
    The control file value determines whether to fetch new data or return the last figure.
    If an invalid control file value is encountered, an empty line chart is returned.

    Args:
        pathname (str): The pathname part of the URL.
        n_intervals (int): The number of intervals passed.
        stored_layout (dict, optional): contains the layout details for the chart. Expected keys include
        'xaxis.range[0]' and 'yaxis.range[0]' for the axis ranges, their values numeric.

    Returns:
        fig (go.Figure): A Plotly figure representing the chart to be drawn.
    """
    # Extract the experiment ID from the URL
    experiment_id = extract_experiment_id_from_url(pathname)

    # Read the control file
    control: str = read_control_file()

    # Fetch dataframe from database
    df: pd.DataFrame = fetch_data(experiment_id, control)

    # Generate the figure
    fig: go.Figure = plot_data(figure, df, stored_layout)

    return fig


def plot_data(fig: go.Figure, df: pd.DataFrame, stored_layout: Optional[dict] = None) -> go.Figure:
    """Create and update a Plotly graph object figure,
    based on the provided DataFrame and layout.

    Parameters:
        df (pd.DataFrame): The data to plot.
        stored_layout (dict, optional): The layout to apply to the figure.

    Returns:
        fig (go.Figure): The updated figure.
    """

    if df.empty or 'ts' not in df.columns or 'value' not in df.columns:
        logger.error("DataFrame empty, or keys missing from columns. Returning empty...")
        return fig

    # Check for new layout and apply if changed
    update_axes_layout(fig, stored_layout)

    try:
        # Attempt to convert columns to numeric
        x_data = pd.to_numeric(df['ts'])
        y_data = pd.to_numeric(df['value'])
    except ValueError:
        logger.error("Columns have non-numeric data and can't change them. Returning empty...")
        return fig
    else:
        # Update existing trace with new data (runs only if the above try block succeeds)
        fig.data[0].x = x_data
        fig.data[0].y = y_data

    return fig


def update_axes_layout(fig: go.Figure, stored_layout: Optional[dict]) -> go.Figure:
    """Track and apply changes to the figure layout."""
    if not stored_layout:
        logger.debug("Stored layout is empty. Returning early.")
        return fig

    logger.debug("Stored layout: %s", stored_layout)

    # If the layout has an autosize key, turn on autorange
    if stored_layout.get('autosize', False):
        fig.update_xaxes(autorange=True)
        fig.update_yaxes(autorange=True)
    else:
        try:
            if all(key in stored_layout for key in ['xaxis.range[0]', 'xaxis.range[1]']):
                fig.update_xaxes(range=[stored_layout['xaxis.range[0]'], stored_layout['xaxis.range[1]']], autorange=False)

            if all(key in stored_layout for key in ['yaxis.range[0]', 'yaxis.range[1]']):
                fig.update_yaxes(range=[stored_layout['yaxis.range[0]'], stored_layout['yaxis.range[1]']], autorange=False)

        except KeyError as error:
            logger.error("KeyError in layout: %s", error)
        except TypeError as error:
            logger.error("TypeError in layout: %s", error)

    return fig


def initialize_figure() -> go.Figure:
    """Create and initialize a Plotly graph object figure
    Returns
        fig (go.Figure): The default settings of the figure.
    """
    fig = go.Figure()
    # Initialize with an empty line trace
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines'))
    # Titles
    fig.update_xaxes(title_text='Time (s)')
    fig.update_yaxes(title_text='Value (u)')

    # Add a margin and a legend, also dark <3
    fig.update_layout(
        margin={'l': 30, 'r': 10, 'b': 30, 't': 10},
        legend={'x': 0, 'y': 1, 'xanchor': 'left'},
        template='plotly_dark')

    logger.debug("Plotly figure created and initialized.")
    return fig


def extract_experiment_id_from_url(url):
    """Extract experiment_id from a given URL.
    The default selection is "experiment_id is None", which forces the database
    to fetch the running experiment.
    TODO: When "experiment_id is not None" we will be attempting to fetch
    a previous experiment.

    Parameters:
        url (str): The URL from which to extract the experiment ID.
        Default value: "/"

    Returns:
        experiment_id (str or None):
        The extracted experiment ID, or None for the latest update.
    """

    parsed = urllib.parse.urlparse(url)
    parsed_dict = urllib.parse.parse_qs(parsed.query)

    experiment_id = parsed_dict.get('experiment')

    if experiment_id is not None:
        logger.debug("experiment_id found in URL %s.", url)

    return experiment_id


def fetch_data(experiment_id, control) -> pd.DataFrame:
    """Fetch data from the PmtDb database based on experiment_id and control.

    Parameters:
        experiment_id (str):
        The ID of the experiment for which to fetch data.
        control (str):
        The control value indicating whether to fetch new data or use existing data.

    Returns:
        df (pd.DataFrame):
        The data fetched from the database, or an empty DataFrame if no data is to be fetched.
    """

    if control == STOP_SIGNAL:
        if not hasattr(fetch_data, "last_df"):
            # This is the first run after the server was started,
            # fetch_data.last_df is not defined, so draw nothing
            df = pd.DataFrame()
            return df

        df = fetch_data.last_df

    elif control == GO_SIGNAL:
        # fetch the new data and update the plot
        database = PmtDb()
        # Default value is "experiment_id is None" which fetches running experiment
        df: pd.DataFrame = database.latest_readings(experiment=experiment_id)
        fetch_data.last_df = df  # store the current dataframe as the last dataframe

    else:
        logger.error("Control file contains an invalid value")
        df = pd.DataFrame()

    return df


# Callback to store the graph's layout
@app.callback(
    Output('stored-layout', 'data'),
    [Input('dynamic-graph', 'relayoutData')],
    [State('stored-layout', 'data')])
def store_layout(relayout_data, stored_layout):
    """Store the layout configuration of the Dash graph.

    This function is a callback that gets triggered when the user interacts
    with the graph (e.g., zooming, panning). It stores the new layout configuration
    in a Dash dcc.Store component for future use.

    Args:
        relayoutData (dict): A dictionary containing the graph's layout configuration.

    Returns:
        dict: The same layout configuration dictionary is returned to be stored in dcc.Store.
    """
    if relayout_data is None:
        raise PreventUpdate

    if stored_layout is None:
        stored_layout = {}

    if relayout_data.get('xaxis.autorange', False) and relayout_data.get('yaxis.autorange', False):
        stored_layout = {'autosize': True}
    else:
        stored_layout.update(relayout_data)
        if 'autosize' in stored_layout:
            del stored_layout['autosize']  # Remove autosize if specific ranges are applied

    logger.debug("relayoutdata: %s", stored_layout)

    return stored_layout


@app.callback(
    [Output(component_id='interval-component', component_property='interval')],
    [Input('interval-component', 'n_intervals')])
def update_refresh_rate(n_intervals):
    """Callback function to update the refresh rate of the chart.
    The control file value determines the new interval rate.
    If the control file value is STOP_SIGNAL, the interval is set to a large number, effectively pausing the updates.
    If the control is GO_SIGNAL, the interval is set to the normal refresh rate.
    If an invalid control file value is encountered, the interval is kept at the default rate.

    Args:
        n_intervals (int): The number of intervals passed.

    Returns:
        list: A list containing the new interval rate (in milliseconds).
    """
    control: str = read_control_file()

    # Refresh values are in seconds. 2s or 10m.
    default_value = NORMAL_REFRESH
    large_value = FREEZE_REFRESH

    # Check the control file for the new interval. Return values are in milliseconds
    if control == STOP_SIGNAL:
        # Freeze refresh: set the interval to a very large number
        return [large_value * 1000]
    elif control == GO_SIGNAL:
        # Normal refresh: set the interval to the normal refresh rate
        return [default_value * 1000]
    else:
        # If the control file contains an invalid value, keep the current interval
        logger.error("Control file contains invalid value.. Refresh rate set to 2s.")
        return [default_value * 1000]


def read_control_file(file_path: str = 'app/control.txt', default_value: str = "1") -> str:
    """Reads the control file "app/control.txt".
    If the control file is successfully read, the stripped content of the file is returned.

    Returns:
        control (str): The binary control parameter, or default if an error occurs.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            control = file.read().strip()
    except (IOError, PermissionError) as err:
        logger.error("Failed to read control file: %s", err)
        control = default_value

    return control


def get_script_level_logs() -> None:
    """Wraps script-level logs to avoid side-effects during testing."""
    logger.debug("Child process ID: %s", os.getpid())
    logger.debug("Parent process ID: %s", os.getppid())


if __name__ == '__main__':
    # Entry point for the script.
    # Starts the Dash server with debugging enabled if the script is run directly.
    # Autoupdate is True by default. Debug=True creates two chart.py processes
    get_script_level_logs()
    figure = initialize_figure()
    app.run(debug=True, dev_tools_hot_reload=False)
