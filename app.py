#! python3

import logging, os

from flask import Flask, request

from get_weather import call_weather_api, get_forecast, get_precip
from plot_weather import plot_temps, plot_precip
from weather_bot import send_message, retrieve_imageurl
from set_location import decipher_location

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)


# @app.route('/', methods = ['POST'])
def webhook(test_data):
    # data received at GroupMe callback URL
    # gm_data = request.get_json()
    gm_data = test_data
    logging.info("Received {}".format(gm_data))

    WEATHER_KEY = os.getenv('WEATHER_KEY')
    bot_id = os.getenv('GROUPME_BOT_ID')  # This is debug Bot

    if not "bot" in gm_data['name'].lower():
        bot_respond(gm_data, WEATHER_KEY, bot_id)

    # This prevents a ValueError raised by Flask
    return "OK"

def bot_respond(gm_data, WEATHER_KEY, bot_id):

    # Dictionary mapping of possible commands
    call_options = {
        "temp": temp_call,
        "precip": precip_call,
        "weather": weather_call
    }

    # force all words to lowecase then split on whitespace
    gm_words = gm_data['text'].lower().split()
    try:
        logging.debug("SPLIT WORDS: {}".format(gm_words))

        # if this doesn't throw an error, then the first word of text is in call_options
        call_options[gm_words[0]]

        # get location from text, pass to decipher_location()
        # taking every word after the first and joining as a location string
        location = []
        for i in range(1,len(gm_words)):
            location.append(gm_words[i])
        location = " ".join(location)

        logging.debug("location result: {}".format(location))

        # Get latitude, longitude, and the location's address
        lat, lng, address = decipher_location(location)

        # Call the weather API for this location
        weather_url = "https://api.forecast.io/forecast/{}/{},{}".format(WEATHER_KEY, lat, lng)

        logging.debug("Weather URL: {}".format(weather_url))

        weather_data, hours_left = call_weather_api(weather_url)
        call_options[gm_words[0]](weather_data, hours_left, bot_id, address)
    except KeyError as e:
        logging.warning("Text does not contain command call.")

    # This prevents a ValueError raised by Flask
    return 'OK'


def precip_call(weather_data, hours_left, bot_id, address):
    p_times, precip = get_precip(weather_data, hours_left)
    try:
        precip_filepath = plot_precip(p_times, precip)
    except FileNotFoundError as e:
        logging.error("Local file not found: {}".format(e))
    precip_img = retrieve_imageurl(precip_filepath)
    send_message(bot_id, txt="Hourly Precipitation for {}".format(address), img_url=precip_img)

def temp_call(weather_data, hours_left, bot_id, address):
    t_times, temps = get_forecast(weather_data, hours_left)
    try:
        temp_filepath = plot_temps(t_times, temps)
    except FileNotFoundError as e:
        logging.error("Local file not found: {}".format(e))
    temp_img = retrieve_imageurl(temp_filepath)
    send_message(bot_id, txt ="Hourly Temperature for {}".format(address), img_url=temp_img)

def weather_call(weather_data, hours_left, bot_id, address):

    temp_call(weather_data, hours_left, bot_id, address)
    precip_call(weather_data, hours_left, bot_id, address)


