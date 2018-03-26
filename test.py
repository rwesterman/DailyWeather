import datetime, time
from get_weather import call_weather_api, get_forecast, gethour, dt_from_timestamp
from plot_weather import plot_temps, plot_precip
from weather_bot import send_message, retrieve_imageurl
from app import compare_call, setup_logging
from set_location import decipher_location
import logging.config
import os
import unittest
import requests
import json
import pytest

# Todo: Trace where multiple "get_dt_from_timestamp" calls are coming from.
# Todo: Continue writing unit tests

os.environ['GM_TOKEN'] = "6WsJo3y1pnS9k78J92NSCblGMwckw2PZ1V5Hv8AO"
os.environ['WEATHER_KEY'] = "74f7ed842e191e137f01b3d90428f8e5"
os.environ['GROUPME_BOT_ID'] = "d6b7111ac8a3b7da98aed334ed"


class weather_test_case(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(weather_test_case, self).__init__(*args, **kwargs)

        # self.import_logger()
        self.test_logger = logging.getLogger("test")

        self.times = [datetime.datetime(2018, 3, 20, 23, 33, 00), datetime.datetime(2018, 3, 20, 23, 34, 00)]
        self.temps = [75, 85]
        self.precips = [0.01, 0.10]

        self.weather_key = "74f7ed842e191e137f01b3d90428f8e5"
        self.debug_bot_id = "d6b7111ac8a3b7da98aed334ed"
        self.groupme_token = "6WsJo3y1pnS9k78J92NSCblGMwckw2PZ1V5Hv8AO"

        # self.test_logger = logging.getLogger('test')

        self.baseurl = "https://api.forecast.io/forecast/"

        self.build_location_file()

        # Set default path, if no file there, log weather data.
        self.wdata_filepath = r"C:\Users\Ryan\PycharmProjects\DailyWeather\weather_data.txt"
        if not os.path.exists(self.wdata_filepath):
            self.wdata_filepath = self.log_weather_data()
        self.weather_data = self.read_weather_data()
        # path to tmp folder on current OS
        self.tmp_path = os.path.join(os.path.abspath(os.sep), "tmp")
        self.create_tmp_folder()

    def import_logger(self):
        self.test_logger = logging.getLogger('test')

    def create_tmp_folder(self):
        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)

    def test_plot_weather(self):
        # Test that plot_temps returns file name in base case
        self.assertIsNotNone(plot_temps(self.times, self.temps))

        # Write a test case for assertLogs() to see why things aren't being logged

    def test_dt_from_timestamp(self):
        tzlist = ["US/Hawaii", "America/Los_Angeles", "America/Denver", "America/Chicago", "America/New_York",
                  "Asia/Shanghai", "Asia/Tokyo"]

        expected_dt = [datetime.datetime(2018, 1, 1, 2, 0, 0), datetime.datetime(2018, 1, 1, 4, 0, 0),
                       datetime.datetime(2018, 1, 1, 5, 0, 0), datetime.datetime(2018, 1, 1, 6, 0, 0),
                       datetime.datetime(2018, 1, 1, 7, 0, 0), datetime.datetime(2018, 1, 1, 20, 0, 0),
                       datetime.datetime(2018, 1, 1, 21, 0, 0)]

        # Unix Timestamp for 1/1/2018 12:00:00 GMT time
        timestamp = 1514808000

        # Test across timezones
        for index in range(len(tzlist)):
            self.assertEqual(dt_from_timestamp(timestamp, tzlist[index]), expected_dt[index])

    def test_call_weather_api(self):
        no_response_url = self.baseurl + "{}/{},{}".format("TestCase", "None", "None")

        # Test bad url call to show HTTP error
        with self.assertRaises(requests.exceptions.HTTPError):
            call_weather_api(no_response_url)

    def read_weather_data(self):
        try:
            with open(self.wdata_filepath, 'r') as f:
                weather_data = json.loads(f.read())
                # self.test_logger.info(weather_data)
                return weather_data
        except TypeError as e:
            self.test_logger.error("Error in read_weather_data, {}".format(e))

    def log_weather_data(self):
        with open(os.path.join(os.getcwd(), "weather_data.txt"), "w") as f:
            data = call_weather_api(self.baseurl + "{}/{},{}".format(self.weather_key, "30.3071", "-97.7559"))[0]
            if not data:
                raise AttributeError("No data present from API")
            # self.test_logger.info(data)
            f.write(json.dumps(data))
            self.wdata_filepath = os.path.join(os.getcwd(), "weather_data.txt")

    def test_get_forecast(self):
        times, temps = get_forecast(self.weather_data, 12, "temperature")

        # Test that times returns are the same
        self.assertEqual(get_forecast(self.weather_data, 12, "temperature")[0],
                         get_forecast(self.weather_data, 12, "precipProbability")[0])

    def build_location_file(self):
        self.loclist_filepath = os.path.join(os.getcwd(), "LocationList.txt")
        if not os.path.exists(self.loclist_filepath):
            cities = ["Honolulu", "Oakland California", "Provo Utah", "Austin Tx", "New York City", "Hong Kong",
                      "Tokyo Japan"]
            location_list = []
            for city in cities:
                lat, lng, addr = decipher_location(city)

                # avoid timeout from geocoder
                time.sleep(1)
                # Store each lat, lng, and addr in one string to write to file. On read, use split to separate values
                loc_str = "{} {} {}\n".format(lat, lng, addr)
                location_list.append(loc_str)

            with open(self.loclist_filepath, 'w') as f:
                f.writelines(location_list)

        return self.loclist_filepath

    # Todo: decide what to return from this method
    def read_location_file(self):
        with open(self.loclist_filepath, 'r') as f:
            loclist = (f.readlines())

        self.test_logger.debug("Received list of locations: {}".format(loclist))
        for location in loclist:
            location = location.split()

            # assign values to lat,lng,addr
            lat, lng, addr = location[0:3]

    def test_compare_call(self):
        self.test_logger.info("Testing compare_call method in app.py")
        compare_call(self.weather_key, self.debug_bot_id, gm_words=["Compare", "Austin", "vs", "Los", "Angeles"])


if __name__ == '__main__':
    setup_logging()
    unittest.main()
