"""
This module encapsulates all functionality related to controlling the Dash app process
and the charting functionality.
"""
CONTROL_FILE: str = "app/control.txt"
START_SIGNAL: str = "1"
STOP_SIGNAL: str = "0"


def start_chart_process(logger) -> None:
    """Resumes the running of "chart.py" by writing '1' into the control file. This signifies
    that the chart callback should run.
    """
    try:
        with open(CONTROL_FILE, "w", encoding="utf-8") as file:
            file.write(START_SIGNAL)
        logger.debug("Sent start/resume signal to chart control file...")
    except OSError as err:
        logger.error("Failed to send start/resume signal to chart control file: %s", err)


def stop_chart_process(logger) -> None:
    """Stops the running of "chart.py" by writing '0' into the control file. This signifies
    that the chart callback should stop.
    """
    try:
        with open(CONTROL_FILE, "w", encoding="utf-8") as file:
            file.write(STOP_SIGNAL)
        logger.debug("Sent stop signal to chart control file...")
    except OSError as err:
        logger.error("Failed to send stop signal to chart control file: %s", err)
