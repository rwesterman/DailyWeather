#! python3

# Todo: Add 3-day forecast feature(maybe more days?) and overlay precipitation chance on temp plot

import json
import logging.config
import os

from flask import Flask, request

from get_weather import call_weather_api, get_forecast
from plot_weather import plot_temps, plot_precip, plot_compare
from set_location import decipher_location
from weather_bot import send_message, retrieve_imageurl

app = Flask(__name__)


# For the fantasy football chat
@app.route('/FF', methods=['POST'])
def ff_webhook():
    # data received at GroupMe callback URL
    gm_data = request.get_json()
    app_log.info("Received {}".format(gm_data))

    WEATHER_KEY = os.getenv('WEATHER_KEY')
    bot_id = os.getenv('FF_BOT_ID')  # This is debug Bot

    if not "bot" in gm_data['name'].lower():
        bot_respond(gm_data, WEATHER_KEY, bot_id)

    # This prevents a ValueError raised by Flask
    return "OK"


# For personal debug chat
@app.route('/debug', methods=['POST'])
def debug_webhook():
    # data received at GroupMe callback URL
    gm_data = request.get_json()
    # gm_data = test_data
    app_log.info("Received {}".format(gm_data))

    WEATHER_KEY = os.getenv('WEATHER_KEY')
    bot_id = os.getenv('DEBUG_BOT_ID')  # This is debug Bot

    if not "bot" in gm_data['name'].lower():
        bot_respond(gm_data, WEATHER_KEY, bot_id)

    # This prevents a ValueError raised by Flask
    return "OK"


# For the weather chat
@app.route('/weather', methods=['POST'])
def weather_webhook():
    # data received at GroupMe callback URL
    gm_data = request.get_json()
    app_log.info("Received {}".format(gm_data))

    WEATHER_KEY = os.getenv('WEATHER_KEY')
    bot_id = os.getenv('WEATHER_BOT_ID')

    if not "bot" in gm_data['name'].lower():
        bot_respond(gm_data, WEATHER_KEY, bot_id)

    # This prevents a ValueError raised by Flask
    return "OK"


def bot_respond(gm_data, WEATHER_KEY, bot_id):
    """
    Parse JSON data from GroupMe to determine if a call is being made. If so, execute the appropriate call function
    :param gm_data: JSON data sent in GroupMe POST when user sends message to group
    :param WEATHER_KEY: User specific weather key for Dark Sky API
    :param bot_id: GroupMe bot ID for specific group
    :return: Return "OK" to prevent Flask error
    """

    # Dictionary mapping of possible commands
    call_options = {
        "temp": temp_call,
        "precip": precip_call,
        "weather": weather_call,
        "temperature": temp_call,
        "rain": precip_call,

        # This is added so we can still check for commands, but will not be called by dictionary calling
        "compare": compare_call
    }

    # force all words to lowercase then split on whitespace
    gm_words = gm_data['text'].lower().split()
    try:
        # if this doesn't throw an error, then the first word of text is in call_options
        call_options[gm_words[0]]

        # Branch if calling for comparison so weather call can be run twice, this will all be done in compare_call method
        if gm_words[0] == "compare":
            compare_call(WEATHER_KEY, bot_id, gm_words)
        else:
            # get location from text, pass to decipher_location()
            # taking every word after the first and joining as a location string
            location = []
            for i in range(1, len(gm_words)):
                location.append(gm_words[i])
            location = " ".join(location)

            # Get latitude, longitude, and the location's address
            lat, lng, address = decipher_location(location)

            # Call the weather API for this location
            weather_url = "https://api.forecast.io/forecast/{}/{},{}".format(WEATHER_KEY, lat, lng)

            # Make call to API to receive weather data
            weather_data, hours_left = call_weather_api(weather_url)

            # Use dictionary call_options to determine what method to call here
            call_options[gm_words[0]](weather_data, hours_left, bot_id, address)
            app_log.debug("FORMATTED PARAMETERS:\n"
                          "Current Hour: {}\nFirst Data Hour: {}\n")
    except KeyError as e:
        app_log.warning("Text does not contain command call.")

    # This prevents a ValueError raised by Flask
    return 'OK'


def precip_call(weather_data, hours_left, bot_id, address):
    """
    Controller for Precipitation requests. Gets forecast data, plots it, then sends message via GroupME bot
    :param weather_data:
    :param hours_left:
    :param bot_id:
    :param address:
    :return:
    """
    p_times, precip = get_forecast(weather_data, hours_left, search_term='precipProbability')
    try:
        precip_filepath = plot_precip(p_times, precip)
        precip_img = retrieve_imageurl(precip_filepath)
        send_message(bot_id, txt="Hourly Precipitation for {}".format(address), img_url=precip_img)
    except FileNotFoundError as e:
        app_log.error("Local file not found: {}".format(e))


def temp_call(weather_data, hours_left, bot_id, address):
    t_times, temps = get_forecast(weather_data, hours_left, search_term='temperature')
    try:
        temp_filepath = plot_temps(t_times, temps)
        temp_img = retrieve_imageurl(temp_filepath)
        send_message(bot_id, txt="Hourly Temperature for {}".format(address), img_url=temp_img)
    except FileNotFoundError as e:
        app_log.error("Local file not found: {}".format(e))


def weather_call(weather_data, hours_left, bot_id, address):
    temp_call(weather_data, hours_left, bot_id, address)
    precip_call(weather_data, hours_left, bot_id, address)


def compare_call(WEATHER_KEY, bot_id, gm_words):
    """
    Compares the weather at two locations by plotting against each other
    :param weather_data: Dictionary of weather data from Dark Sky API
    :param hours_left: Num hours remaining in the day
    :param bot_id: GroupME bot ID
    :param addr1: First location
    :param addr2: Second Location
    ;kwargs: Expecting list gm_words,
    :return:
    """
    # Todo: Make this robust. Look below for edge cases to consider
    # User sends "Compare vs City", with no first location
    # User sends "Compare City vs" with no second location
    # User sends no "vs" statement - should error out


    # This method assumes that the first word of a message was "compare"
    # From there, it will determine the two addresses being compared by finding the strings on either side of 'vs'
    # Then it will gather weather data for each of these addresses, and call plot_compare() to obtain a figure.
    try:
        vs_index = gm_words.index("vs")

        # Check if 'vs' comes right after "Compare", meaning no first city entered
        if vs_index == 1:
            raise ValueError("Invalid comparison call, must provide two locations")

        # Next, check if 'vs' is the last word, meaning no second city entered
        elif vs_index == len(gm_words) - 1:
            raise ValueError("Invalid comparison call, must provide two locations")

        else:
            addr1 = " ".join(gm_words[1:vs_index])
            addr2 = " ".join(gm_words[vs_index + 1:])
            test_logger.debug("Address1: {}, Address2: {}".format(addr1, addr2))

            # Obtain the lat, lng, and found address for each of the prompted locations
            lat1, lng1, address1 = decipher_location(addr1)
            lat2, lng2, address2 = decipher_location(addr2)

            # Call the weather API for each location
            weather_url1 = "https://api.forecast.io/forecast/{}/{},{}".format(WEATHER_KEY, lat1, lng1)
            weather_url2 = "https://api.forecast.io/forecast/{}/{},{}".format(WEATHER_KEY, lat2, lng2)

            # Parse API weather data for each location
            weather_data1, hours_left = call_weather_api(weather_url1)
            weather_data2, hours_left = call_weather_api(weather_url2)

            times, temps1 = get_forecast(weather_data1, hours_left, search_term='temperature')
            times, temps2 = get_forecast(weather_data2, hours_left, search_term='temperature')

            try:
                temp_filepath = plot_compare(times, temps1, temps2, address1, address2)
                temp_img = retrieve_imageurl(temp_filepath)
                send_message(bot_id, txt="Temperature compare between {} and {}".format(address1, address2),
                             img_url=temp_img)
            except FileNotFoundError as e:
                app_log.error("Local file not found: {}".format(e))

    except IndexError as e:
        app_log.warning("No use of 'vs' in the call, therefore no command was processed")
    except ValueError as e:
        app_log.error("Invalid comparison call, must provide two locations")


def setup_logging(
        default_path=os.path.join(os.getcwd(), "logging", "config.json"),
        default_level=logging.INFO,
        env_key='LOG_CFG'):
    """
    Set up logging configuration from json file
    :param default_path:
    :param default_level:
    :param env_key:
    :return:
    """
    path = default_path
    value = os.getenv(env_key, None)
    print("The path given to the logger config file is {}".format(path))
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
        logging.error("Wasn't able to configure loggers from file!")
        raise Exception("Logging config failed, raising exception for debug!")


setup_logging()
app_log = logging.getLogger("app")
test_logger = logging.getLogger("test")