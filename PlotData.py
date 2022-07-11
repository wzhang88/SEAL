"""
User can change the parameter at the top to customize their plots
"""

import plotly.express as px
import plotly.graph_objects as go
from DataProcessing import *

DATA_PATH = 'data/'
START_TIME = '2022-04-22 16:00:00'
END_TIME = '2022-04-22 16:15:00'
COL_NAME = 'Dp>0.3'
IS_REMOVE_EXTREME = True
SHOW_MEAN = True
CONF_LEVEL = 99
ROUND_TIME = '5'


def plot_line_chart(data, x, y, title, addMean: bool):
    line_plot = px.line(data,
                        x=x,
                        y=y,
                        color='Device',
                        title=title,
                        labels={'Datetime_round': 'Time'})
    # labels at the bottom as note - NOT YET ADDED

    # add mean line to the graph
    if addMean:
        mean = data[y].mean()
        line_plot.add_trace(
            go.Scatter(
                x=[START_TIME, END_TIME],
                y=[mean, mean],
                mode="lines",
                name='Mean=' + "{:.3f}".format(mean),
                text="Mean",
                line=go.scatter.Line(color="gray", dash='dash')
            )
        )
    return line_plot


if __name__ == "__main__":
    # get data from file
    df = read_data_combine(DATA_PATH)

    # round time
    df = round_time_and_linear_interpolate(df, ROUND_TIME)

    # only keep data in range
    df = get_data_in_range(df, START_TIME, END_TIME)

    # remove extreme
    if IS_REMOVE_EXTREME:
        df = drop_numerical_outliers(df.copy(), CONF_LEVEL)

    plot = plot_line_chart(df, 'Datetime_round', COL_NAME, COL_NAME + ' Collected by Device with Extreme Removed',
                           SHOW_MEAN)
    plot.write_html('measured_type_plot.html')
