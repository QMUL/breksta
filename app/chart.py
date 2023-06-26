
import urllib.parse

from dash import Dash, html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

from app.capture import PmtDb
from app.logger_config import setup_logger

app = Dash(__name__)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Graph(id='chart-content'),
    dcc.Interval(id='interval-component', interval=2000, n_intervals=0)
])

'''Dash example of a periodically updated chart:
    https://dash.plotly.com/live-updates
If the chart is to be accessed remotely, should cache previous data-points
to reduce network traffic:
    https://dash.plotly.com/persistence
TODO: Add components only visible remotely to faciliate remote .csv download.
'''
@app.callback(Output('chart-content', 'figure'), [Input('url', 'pathname'),
    Input('interval-component', 'n_intervals')])
def draw_chart(pathname, n):

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
        else:
            df = draw_chart.last_df
    elif control == '1':
        # If the control file contains '1', fetch the new data and update the plot
        db = PmtDb()
        df = db.latest_readings(experiment=experiment)
        draw_chart.last_df = df  # store the current dataframe as the last dataframe
    else:
        logger.error("Control file contains an invalid value")
        return px.line()

    # logger.debug(f"draw_chart called with pathname={pathname}, n={n}")

    return px.line(df, x='ts', y='value')

@app.callback(
    [Output(component_id='interval-component', component_property='interval')],
    [Input('interval-component', 'n_intervals')])
def update_refresh_rate(n_intervals):
    # Read the control file
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
    '''Reads in "app/control.txt".
        Returns: str'''
    logger = setup_logger()
    try:
        with open('app/control.txt', 'r') as f:
            return f.read().strip()
    except IOError as e:
        logger.error("Failed to read control file: %s", e)
        return None

if __name__ == '__main__':
    app.run_server(debug=True)
