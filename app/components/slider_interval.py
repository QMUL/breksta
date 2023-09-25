from dataclasses import dataclass
from dash import Dash, dcc, html


@dataclass
class SliderValues:
    """Encapsulate the Slider values to remove from global namespace
    Yes, may be overengineering or overkill. Serves as much needed training
    in dataclasses and their use..
    """
    MIN = 2.0
    MAX = 10.0
    STEP = 2
    VALUE = 2


def render(app: Dash) -> html.Div:
    """Create and deploy the Interval slider.
    Any time a new value is chosen the update_refresh_rate callback is triggered.
    """
    return html.Div(
        [
            html.H6("Refresh Rate"),
            dcc.Slider(
                id='interval-refresh',  # Hook to update_refresh_rate@chart
                min=SliderValues.MIN,
                max=SliderValues.MAX,
                step=SliderValues.STEP,
                value=SliderValues.VALUE,
                marks={i: f"{i}s" for i in range(
                    int(SliderValues.MIN),
                    int(SliderValues.MAX) + 1,
                    SliderValues.STEP
                )}
            )
        ],
        style={'width': '20%'}
    )
