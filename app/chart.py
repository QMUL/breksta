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

from app.logger_config import setup_logger
from app.cache_module import CacheWebProcess

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

# Attach the cache object to the app
app.cache = CacheWebProcess()

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

    Args:
        df (pd.DataFrame): The data to plot.
        stored_layout (dict, optional): The layout to apply to the figure.

    Returns:
        fig (go.Figure): The updated figure.
    """

    if df.empty or 'ts' not in df.columns or 'value' not in df.columns:
        logger.error("DataFrame empty, or keys missing from columns. Returning empty...")
        return fig

    # Update the layout to preserve user customizations between sessions
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
    """Update the figure layout based on stored settings.

    This function applies the layout settings stored in 'stored_layout' to the given figure.
    Makes the graph user-friendly by applying layout customizations.

    Args:
        fig (go.Figure): The plotly figure object whose layout needs to be updated.
        stored_layout (Optional[dict]): The stored layout settings.

    Returns:
        go.Figure: The updated plotly figure object.
    """

    # If stored_layout is empty, no user customizations are available to restore
    if not stored_layout:
        logger.debug("Stored layout is empty. Returning early.")
        return fig

    # Turn on autorange when 'autosize' is set to adjust the graph to optimal dimensions
    if stored_layout.get('autosize', False):
        fig.update_xaxes(autorange=True)
        fig.update_yaxes(autorange=True)
        return fig  # Return early as no further layout customization is needed

    # Update x- and y-axis range only if both lower and upper bounds are available
    # This ensures a complete and meaningful update of the axis range. All 'autorange' keys persist; turn OFF
    try:
        if all(key in stored_layout for key in ['xaxis.range[0]', 'xaxis.range[1]']):
            fig.update_xaxes(range=[stored_layout['xaxis.range[0]'], stored_layout['xaxis.range[1]']], autorange=False)

        if all(key in stored_layout for key in ['yaxis.range[0]', 'yaxis.range[1]']):
            fig.update_yaxes(range=[stored_layout['yaxis.range[0]'], stored_layout['yaxis.range[1]']], autorange=False)

    # Log errors to trace missing keys or identify incorrect types that could break the layout update
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

    Args:
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

    Args:
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
        # Fetch the new data and update the plot
        df = app.cache.database.latest_readings(experiment=experiment_id)

        # Fetch data and append it to the cache
        dataframe = app.cache.handle_data_update(experiment_id)
        logger.debug("Updating cache: \n%s", dataframe)

        if df is not None:
            fetch_data.last_df = df  # Store the current DataFrame as the last DataFrame

        else:
            logger.warning("No new data found.")
    else:
        logger.error("Control file contains an invalid value")
        df = pd.DataFrame()

    return df


# Callback to persist the graph's layout for user-defined settings
@app.callback(
    Output('stored-layout', 'data'),
    [Input('dynamic-graph', 'relayoutData')],
    [State('stored-layout', 'data')])
def store_layout(relayout_data, stored_layout):
    """Store and update the layout configuration of the Dash graph.

    This function is a callback triggered by user interactions like zooming, panning, or resizing.
    It stores the new layout configuration in a Dash dcc.Store component, which can be retrieved
    for rendering the graph with user-defined settings.

    Args:
        relayoutData (dict): A dictionary containing the graph's changed layout configuration.
        stored_layout (dict): A dictionary containing the graph's previously stored layout configuration.

    Returns:
        dict: The updated layout configuration dictionary to be stored in dcc.Store.
    """
    # Prevent any updates if no user interactions have altered the layout
    if relayout_data is None:
        raise PreventUpdate

    # Ensure stored_layout is mutable for subsequent updates
    stored_layout = stored_layout or {}

    # If the layout has not changed, return early to avoid redundant operations
    if stored_layout == relayout_data:
        raise PreventUpdate

    if relayout_data.get('xaxis.autorange', False) and relayout_data.get('yaxis.autorange', False):
        # Set to autosize to ensure the graph adjusts to optimal dimensions
        stored_layout = {'autosize': True}
    else:
        # Roll over user-customized layout changes into stored_layout for ongoing persistence
        stored_layout.update(relayout_data)

        # Remove 'autosize' to prevent conflict with user-defined axis ranges
        if 'autosize' in stored_layout:
            del stored_layout['autosize']

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
