from geopy.geocoders import LiveAddress, GoogleV3, ArcGIS
from geopy.geocoders import get_geocoder_for_service
import logging

def pick_geocoder(service):
    print(get_geocoder_for_service(service))

def decipher_location(location = "Austin Texas"):
    """
    Receives text describing location, returns geographical coordinates lat and lng
    :param location: String giving user location, defaults to Austin Tx
    :return: latitude and longitude
    """

    # If location provided is empty string, then set dafault to Austin
    if not location:
        location = "Austin Texas"

    # geolocator = GoogleV3()
    geolocator = ArcGIS()
    geo_loc = geolocator.geocode(location)

    # If no matching location found, geo_loc == None
    # If this happens, print no location found, defaulting to Austin Tx
    if not geo_loc:
        logging.warning("Location not found, defaulting to Austin Tx")
        geo_loc = geolocator.geocode("Austin Texas")
    logging.info("Input location was {}, found location is {}".format(location, geo_loc.address))
    logging.info("Location Latitude: {}, Longitude: {}".format(geo_loc.latitude, geo_loc.longitude))
    return geo_loc.latitude, geo_loc.longitude, geo_loc.address

