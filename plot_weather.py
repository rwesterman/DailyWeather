import matplotlib

matplotlib.use('Agg')
from matplotlib import pyplot as plt
from matplotlib import dates
import datetime
import logging
import os


def plot_temps(times, temps):
    """Plots hourly temperature forecast and returns image filepath"""

    return plot_common(times, temps, "Hourly Temperature Forecast", "Hour", "Temperature (F)")


def plot_precip(times, precip):
    """Plots hourly precipitation forecast and returns image filepath"""

    # Set ymax to 1 because precip chance is value between 0 and 1
    return plot_common(times, precip, "Hourly Precipitation Forecast", "Hour", "% Chance of Precip", ymax=1, ymin=0)


def plot_compare(times, temps1, temps2, address1, address2):
    """Plots comparison of hourly temperature forecast between two locations"""

    # kwargs will be used to enter legend logic in plot_common(), then to set the labels for each plotted line
    kwargs = {"legend": True, "plot_title": [address1, address2]}

    # Plot the first location's temperature forecast, but don't close the figure
    # Only send kwargs on second call to plot_common() so that it can label both existing lines
    plot_common(times, temps1, "Hourly Temp Comparison", "Hour", "Temperature", close=False)

    # Plot the second location's temperature forecast, close the plot, and return the filename
    return plot_common(times, temps2, "Hourly Temp Comparison", "Hour", "Temperature", **kwargs)


def plot_common(x, y, title, xlabel, ylabel, xmax=None, xmin=None, ymax=None, ymin=None, close=True, **kwargs):
    """
    Function that handles the plotting of gathered data. This can be called for temp or precipitation currently

    :param x: X axis values, typically time
    :param y: Y axis values, either time or precipitation
    :param title: Title to give to the graph
    :param xlabel: X axis label
    :param ylabel: Y axis label
    :param xmax: optional, used to directly scale x axis
    :param xmin: optional, used to directly scale x axis
    :param ymax: optional, used to directly scale y axis
    :param ymin: optional, used to directly scale y axis
    :param close: optional, determines if plot is closed between calls. Setting to False allows layering plots
    :return:
    """

    weather_logger.debug("plot_weather x-axis values: {}".format(x))

    ax = plt.gca()
    ax.set_xticks(x)

    # Determine if axes are automatically scaled. Temp plots will be, but precipitation plots won't
    if xmax or xmin:
        plt.xlim(xmin, xmax)
    if ymax or ymin:
        plt.ylim(ymin, ymax)
    if not (ymax or ymin or xmax or xmin):
        plt.autoscale(True)

    plt.gcf().autofmt_xdate()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    xfmt = dates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(x, y, "o-")

    # Check to see if label data was sent
    # Will return value of kwargs['legend'] if it exists, otherwise will return False and if statement will not execute
    if kwargs.get("legend", False):
        plt.legend(kwargs.get("plot_title"))

    plt.minorticks_off()

    root_path = os.path.abspath(os.sep)
    local_path = os.path.join(root_path, "tmp")

    if not os.path.exists(local_path):
        # os.mkdir("/app/tmp/")
        os.mkdir(local_path)
    # Create an appropriate filename
    fig_filename = os.path.join(local_path, "{}_{}.png".format(title, datetime.datetime.now().strftime("%m-%d_%H")))
    weather_logger.info("Filepath: {}".format(fig_filename))
    # Save the figure locally. This will be deleted when the image is uploaded to Groupme hosting
    plt.savefig(fig_filename)

    # This is necesary to prevent from layering your data on one plot, even across separate calls to the function.
    if close:
        plt.close()

    return fig_filename


weather_logger = logging.getLogger("weather")
