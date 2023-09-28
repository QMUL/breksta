"""go.Figure-related helper functions"""
from typing import Optional
import plotly.graph_objects as go
import pandas as pd

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
