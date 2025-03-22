"""
Author: Hunter R. Merrill

Description: This script contains functions for getting weather forecasts from the
weather.gov API.
"""

from typing import Any, Dict

import requests
from endurance_training_app.location_utils import get_fips_from_location, get_location_from_ip


def get_weather_data() -> Dict[str, Any]:
    """
    Get weather forecasts from the weather.gov API for the user's location.

    Returns
    -------
    Dict[str, Any]
        The json containing the hourly weather forecast.
    """

    # get the latitude and longitude from IP address
    ip_data = get_location_from_ip()

    # get FIPS code from location
    lat, lon = ip_data["loc"].split(",")
    fips = get_fips_from_location(lat=float(lat), lon=float(lon))

    # look up the weather forecast endpoint for the given location
    points_response = requests.get(f"https://api.weather.gov/points/{ip_data['loc']}")
    points_endpoint = points_response.json()["properties"]["forecastHourly"]

    # now collect the weather forecast
    forecast_response = requests.get(points_endpoint)
    forecast_data = forecast_response.json()
    return forecast_data
