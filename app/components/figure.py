"""Helper Functions for Manipulating and Customizing Plotly Figures.

This module provides a set of utility functions designed to simplify and standardize the creation,
initialization, and customization of Plotly figure objects within the application.

Functions:
- `initialize_figure`: Sets up a default Plotly figure with options for custom axis titles.
- `plot_data`: Adds the data to the plotting dataframe.
- `update_axes_layout`: Updates the axis layout of a given Plotly figure based on stored user preferences.
"""

import pandas as pd
import plotly.graph_objects as go

from app.logger_config import setup_logger

logger = setup_logger()


def initialize_figure(x_title: str = 'Time (s)', y_title: str = 'Voltage (V)') -> go.Figure:
    """Create and initialize a Plotly graph object figure with customizable settings.

    This function sets up a default Plotly figure to provide a consistent starting point for all subsequent plots.
    It includes an empty trace, parameterized axis titles, and a default layout to enhance user experience.

    Args:
        x_title (str, optional): Title for the x-axis. Default is 'Time (s)'.
        y_title (str, optional): Title for the y-axis. Default is 'Value (u)'.

    Returns:
        go.Figure: A Plotly figure object with default or customized settings.
    """
    fig = go.Figure()

    # Start with an empty line trace to provide a visual placeholder before actual data is plotted
    fig.add_trace(go.Scatter(x=[], y=[], mode='lines'))

    # Set axis titles based on the arguments for better data interpretation
    fig.update_xaxes(title_text=x_title)
    fig.update_yaxes(title_text=y_title)

    # Establish a default layout including margins and legends for a polished, readable plot
    # also, dark mode for visual comfort
    fig.update_layout(
        margin={'l': 30, 'r': 10, 'b': 30, 't': 10},
        legend={'x': 0, 'y': 1, 'xanchor': 'left'},
        template='plotly_dark')

    logger.debug("Plotly figure created and initialized.")
    return fig


def plot_data(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    """Update the figure's existing trace with new data. The data is assumed numerical.

    Args:
        df (pd.DataFrame): The data to plot.

    Returns:
        fig (go.Figure): The updated figure.
    """
    if df.empty or 'ts' not in df.columns or 'value' not in df.columns:
        logger.error("DataFrame empty, or keys missing from columns. Returning empty...")
        return fig

    # Ensure 'ts' and 'value' are of numeric type
    try:
        df['ts'] = pd.to_numeric(df['ts'])
        df['value'] = pd.to_numeric(df['value'])
    except ValueError:
        logger.error("Data type conversion error. Returning existing figure...")
        return fig

    fig.data[0].x = df['ts']
    fig.data[0].y = df['value']

    return fig


def update_axes_layout(fig: go.Figure, stored_layout: dict | None) -> go.Figure:
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


def display_placeholder_graph(width):
    """Displays a placeholder text before an experiment is selected.
    """
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode='markers',
        marker={"size": [0, 0]}))  # invisible points

    fig.update_layout(
        annotations=[
            go.layout.Annotation(
                x=0.5, y=0.5, text="GRAPH", showarrow=False,
                font={"size": 84})],
        xaxis={"showgrid": False, "zeroline": False, "visible": False},
        yaxis={"showgrid": False, "zeroline": False, "visible": False},
        autosize=False, width=width / 2, height=width / 4)

    # Convert the Plotly figure to HTML and load it
    raw_html = fig.to_html(full_html=False, include_plotlyjs='cdn')
    return raw_html


def downsample_data(df: pd.DataFrame, step=10, max_points=10**5) -> pd.DataFrame:
    """Trim down the dataframe to 1/step data points."""
    points: int = len(df)
    if points <= max_points:
        return df

    return df.iloc[::step]
