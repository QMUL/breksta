"""go.Figure-related helper functions"""
import plotly.graph_objects as go

from app.logger_config import setup_logger

logger = setup_logger()


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
