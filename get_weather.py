import datetime
import json
import logging

import requests


def dt_from_timestamp(timestamp):
    """Returns datetime object from timestamp"""
    return datetime.datetime.fromtimestamp(timestamp)


def gethour(timestamp):
    """Returns integer hour given by timestamp"""
    return datetime.datetime.fromtimestamp(timestamp).hour


def getdate(timestamp):
    """Returns string in Month/Date/Year format from """
    return datetime.datetime.fromtimestamp(timestamp).strftime('%m/%d/%Y')


def call_weather_api(url):
    """
    Makes a call to the DarkSky Weather API
    :param url: URL includes all necessary data to make API call
    :return:
    """
    res = requests.get(url)
    res.raise_for_status()

    # Retreive JSON data from API and return it
    data = json.loads(res.content)

    # Stores the number of hours left in the day, or defaults to 12 if less than 12 hours left
    hours_left = max(24 - datetime.datetime.now().hour, 12)

    return data, hours_left


def get_forecast(weather_data, hours_left, search_term):
    """
    Returns forecast based on search_term input. Currently Temp or Precipiation Chance

    :param weather_data: JSON weather data from API
    :param hours_left: Number of hours left in day or 12, whichever is higher
    :param search_term:
    :return: Return two lists.
    times is list of hours in the "hours_left" period
    forecast is list of temperatures/precipitations corresponding to those hours
    """

    # hourly_block holds datablocks for each hour, this will be iterated on below
    hourly_block = weather_data['hourly']['data']
    times, forecast = [], []

    # Converting to string with strftime wraps back to zero. Need to send matplotlib a datetime obj, but only show hours
    # Seems like the best way to do this is pass full datetime object, then use matplotlib.dates.DateFormatter()
    for hour in range(hours_left):
        times.append((dt_from_timestamp(hourly_block[hour]['time'])))
        forecast.append(hourly_block[hour][search_term])

    logging.debug("Times from weather_data: {}\nForecast from weather_data: {}".format(times, forecast))

    return times, forecast
