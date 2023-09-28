"""A Dash application instance.
This app has a layout that consists of a location component for URL handling,
a graph for chart content, and an interval component for periodic updates.

Dash example of a periodically updated chart:
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
import dash
from dash import Dash, State
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc  # BOOTSTRAP, CYBORG,SUPERHERO
import pandas as pd  # For creating an empty DataFrame

from app.logger_config import setup_logger
from app.cache_module import CacheWebProcess
from app.components.figure import initialize_figure
from app.components.layout import create_layout

logger = setup_logger()

# Control signals
GO_SIGNAL = '1'
STOP_SIGNAL = '0'

app = Dash(
    __name__,
    meta_tags=[{
        "name": "viewport",
        "content": "width=device-width, initial-scale=1",
    }],
    external_stylesheets=[dbc.themes.SUPERHERO]
)
app.title = "Breksta - Data Acquisition App"
app.config["suppress_callback_exceptions"] = True

# Attach the cache object to the app
app.cache = CacheWebProcess()

app.layout = create_layout(app)
app.figure = initialize_figure()


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
    fig: go.Figure = plot_data(app.figure, df, stored_layout)

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
    """Fetch data based on experiment_id and control signal.

    Args:
        experiment_id (str): ID of the experiment to fetch data for.
        control (str): Control signal to determine the action.

    Returns:
        dataframe (pd.DataFrame): Data fetched or retrieved from cache.
    """
    if control == STOP_SIGNAL:
        # Retrieve the last update from the cache
        dataframe = app.cache.get_cached_data(experiment_id)

        if dataframe is None:
            logger.warning("No data in cache for this experiment.")
            return pd.DataFrame()

        return dataframe

    if control == GO_SIGNAL:
        # Update the cache
        logger.debug("Fetch data from cache for experiment ID: %s", experiment_id)
        app.cache.handle_data_update(experiment_id)

        # Retrieve updated data from the cache
        dataframe = app.cache.get_cached_data(experiment_id)
        # Logger print causes dataframe gore in the file. Enable with caution
        # logger.debug("Updating cache: \n%s", dataframe)

        if dataframe is None:
            logger.warning("No new data found.")
            return pd.DataFrame()

        return dataframe

    logger.error("Control file contains an invalid value.")
    raise ValueError("Invalid control signal.")


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
    [
        Output(component_id='interval-component', component_property='interval'),
        Output(component_id='interval-component', component_property='disabled')
    ],
    [Input('interval-refresh', 'value')])
def update_refresh_rate(value):
    """Callback function to update the refresh rate of the chart based on user input and control signal.

    This function updates two properties of the 'interval-component':
    1. The 'interval' property, which specifies the refresh rate in milliseconds.
    2. The 'disabled' property, which determines whether the interval is active.

    If the control file value is STOP_SIGNAL, the interval is disabled.
    Otherwise, the interval is set based on the user's input from 'interval-refresh' slider.

    Args:
        value (float): The user-selected refresh rate in seconds.

    Returns:
        tuple: A tuple containing:
            - New interval rate in milliseconds (int)
            - Whether the interval should be disabled (bool)
    """
    control: str = read_control_file()

    if control == STOP_SIGNAL:
        return dash.no_update, True  # Disable the interval

    return value * 1000, False


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

    app.run(debug=True, dev_tools_hot_reload=False)
