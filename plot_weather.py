import datetime
import logging
import os
from matplotlib import pyplot as plt, dates as md


def plot_temps(times, temps):
    """Plots hourly temperature forecast and returns image filepath"""

    return plot_common(times, temps, "Hourly Temperature Forecast", "Hour", "Temperature (F)")


def plot_precip(times, precip):
    """Plots hourly precipitation forecast and returns image filepath"""

    return plot_common(times, precip, "Hourly Precipitation Forecast", "Hour", "% Chance of Precip", ymax = 100, ymin = 0)


def plot_common(x, y, title, xlabel, ylabel, xmax = None, xmin = None, ymax = None, ymin = None):
    logging.debug("Y-Axis Values: {}".format(y))

    # plt.subplots_adjust(bottom=0.2)
    # plt.xticks(rotation=25)

    ax = plt.gca()
    ax.set_xticks(x)

    # Determine if axes are automatically scaled. Temp plots will be, but precipitation plots won't
    if xmax or xmin:
        plt.xlim(xmin, xmax)
#         plt.autoscale(False)
    if ymax or ymin:
        plt.ylim(ymin, ymax)
#         plt.autoscale(False)
    if not (ymax or ymin or xmax or xmin):
        plt.autoscale(True)

    plt.gcf().autofmt_xdate()
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    xfmt = md.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(xfmt)
    plt.plot(x, y, "o-")
    plt.minorticks_off()

    # Create an appropriate filename
    fig_filename = os.path.join(os.getcwd(),"tmp","{}_{}".format(title,datetime.datetime.now().strftime("%m-%d_%H")))
    logging.info("Filepath: {}".format(fig_filename))
    # Save the figure locally. This will be deleted when the image is uploaded to Groupme hosting
    plt.savefig(fig_filename)

    # This is necesary to prevent from layering your data on one plot, even across separate calls to the function.
    plt.close()

    return fig_filename