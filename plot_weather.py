import matplotlib
matplotlib.use('Agg')
import datetime
import logging
import os




def plot_temps(times, temps):
    """Plots hourly temperature forecast and returns image filepath"""

    return plot_common(times, temps, "Hourly Temperature Forecast", "Hour", "Temperature (F)")


def plot_precip(times, precip):
    """Plots hourly precipitation forecast and returns image filepath"""

    return plot_common(times, precip, "Hourly Precipitation Forecast", "Hour", "% Chance of Precip", ymax = 100, ymin = 0)


def plot_common(x, y, title, xlabel, ylabel, xmax = None, xmin = None, ymax = None, ymin = None):
    logging.debug("Y-Axis Values: {}".format(y))

    ax = matplotlib.pyplot.gca()
    ax.set_xticks(x)

    # Determine if axes are automatically scaled. Temp plots will be, but precipitation plots won't
    if xmax or xmin:
        matplotlib.pyplot.xlim(xmin, xmax)
    if ymax or ymin:
        matplotlib.pyplot.ylim(ymin, ymax)
    if not (ymax or ymin or xmax or xmin):
        matplotlib.pyplot.autoscale(True)

    matplotlib.pyplot.gcf().autofmt_xdate()
    matplotlib.pyplot.title(title)
    matplotlib.pyplot.xlabel(xlabel)
    matplotlib.pyplot.ylabel(ylabel)

    xfmt = matplotlib.dates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(xfmt)
    matplotlib.pyplot.plot(x, y, "o-")
    matplotlib.pyplot.minorticks_off()

    # Create an appropriate filename
    fig_filename = os.path.join(os.getcwd(),"tmp","{}_{}".format(title,datetime.datetime.now().strftime("%m-%d_%H")))
    logging.info("Filepath: {}".format(fig_filename))
    # Save the figure locally. This will be deleted when the image is uploaded to Groupme hosting
    matplotlib.pyplot.savefig(fig_filename)

    # This is necesary to prevent from layering your data on one plot, even across separate calls to the function.
    matplotlib.pyplot.close()

    return fig_filename