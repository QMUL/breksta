
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

    logger.debug(f"draw_chart called with pathname={pathname}, n={n}")

    parsed = urllib.parse.urlparse(pathname)

    # We can pass in the ID of the experiment as a GET parameter
    parsed_dict = urllib.parse.parse_qs(parsed.query)
    experiment = parsed_dict.get('experiment')

    db = PmtDb(logger)

    df = db.latest_readings(experiment=experiment)

    logger.debug('ping...')

    return px.line(df, x='ts', y='value')

if __name__ == '__main__':
    app.run_server(debug=True)
