"""Dash example of a periodically updated chart:
    https://dash.plotly.com/live-updates
If the chart is to be accessed remotely, should cache previous data-points
to reduce network traffic:
    https://dash.plotly.com/persistence
TODO: Add components only visible remotely to faciliate remote .csv download.
"""

import urllib.parse

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

from app.capture import PmtDb
from app.logger_config import setup_logger

app = Dash(__name__)
"""A Dash application instance.
This app has a layout that consists of a location component for URL handling,
a graph for chart content, and an interval component for periodic updates.
"""

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Graph(id='chart-content'),
    dcc.Interval(id='interval-component', interval=2000, n_intervals=0)
])


@app.callback(Output('chart-content', 'figure'),
              [Input('url', 'pathname'),
              Input('interval-component', 'n_intervals')])
def draw_chart(pathname, n_intervals):
    """Callback function to draw the chart.
    The chart content is updated based on the pathname and the number of intervals passed.
    The experiment ID is extracted from the GET parameters of the URL,
    and the corresponding data is fetched from the database.
    The control file value determines whether to fetch new data or return the last figure.
    If an invalid control file value is encountered, an empty line chart is returned.

    Args:
        pathname (str): The pathname part of the URL.
        n (int): The number of intervals passed.

    Returns:
        plotly.graph_objs._figure.Figure: A Plotly figure representing the chart to be drawn.
    """
    logger = setup_logger()

    parsed = urllib.parse.urlparse(pathname)

    # We can pass in the ID of the experiment as a GET parameter
    parsed_dict = urllib.parse.parse_qs(parsed.query)
    experiment = parsed_dict.get('experiment')

    # Read the control file
    control = read_control_file()

    # If the control file contains '0', return the last figure without updating the data
    if control == '0':
        if not hasattr(draw_chart, "last_df"):
            # This is the first run after the server was started,
            # draw_chart.last_df is not defined, so draw nothing
            return px.line()

        df = draw_chart.last_df
    elif control == '1':
        # If the control file contains '1', fetch the new data and update the plot
        db = PmtDb()
        df = db.latest_readings(experiment=experiment)
        draw_chart.last_df = df  # store the current dataframe as the last dataframe
    else:
        logger.error("Control file contains an invalid value")
        return px.line()

    return px.line(df, x='ts', y='value')


# Callback to store the graph's layout
@app.callback(
    Output('stored-layout', 'data'),
    [Input('dynamic-graph', 'relayoutData')]
)
def store_layout(relayoutData):
    """Store the layout configuration of the Dash graph.

    This function is a callback that gets triggered when the user interacts
    with the graph (e.g., zooming, panning). It stores the new layout configuration
    in a Dash dcc.Store component for future use.

    Args:
        relayoutData (dict): A dictionary containing the graph's layout configuration.

    Returns:
        dict: The same layout configuration dictionary is returned to be stored in dcc.Store.
    """
    return relayoutData


@app.callback(
    [Output(component_id='interval-component', component_property='interval')],
    [Input('interval-component', 'n_intervals')])
def update_refresh_rate(n_intervals):
    """Callback function to update the refresh rate of the chart.
    The control file value determines the new interval rate.
    If the control file value is '0', the interval is set to a large number, effectively pausing the updates.
    If the control file value is '1', the interval is set to the normal refresh rate.
    If an invalid control file value is encountered, the interval is kept at the default rate.

    Args:
        n_intervals (int): The number of intervals passed.

    Returns:
        list: A list containing the new interval rate (in milliseconds).
    """
    control = read_control_file()

    # Refresh values are in seconds. 2s or 10m.
    default_value = 2
    large_value = 600

    # Check the control file for the new interval. Return values are in milliseconds
    if control == '0':
        # the control file says to stop, set the interval to a very large number
        return [large_value * 1000]
    elif control == '1':
        # the control file says to resume, set the interval to the normal refresh rate
        return [default_value * 1000]
    else:
        # If the control file contains an invalid value, keep the current interval
        return [default_value * 1000]


def read_control_file():
    """Reads the control file "app/control.txt".
    If the control file is successfully read, the stripped content of the file is returned.

    Returns:
        str or None: The content of the control file, or None if an IOError occurs.
    """
    logger = setup_logger()
    try:
        with open('app/control.txt', 'r', encoding='utf-8') as file:
            return file.read().strip()
    except IOError as err:
        logger.error("Failed to read control file: %s", err)
        return None


if __name__ == '__main__':
    # Entry point for the script.
    # Starts the Dash server with debugging enabled if the script is run directly.
    # Autoupdate is True by default.
    app.run_server(debug=True)
