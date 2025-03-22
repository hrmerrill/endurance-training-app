"""
Author: Hunter R. Merrill

Description: This script contains functions for getting weather forecasts from the
weather.gov API.
"""

from typing import Any, Dict, Optional

import requests
from endurance_training_app.location_utils import get_location_from_ip


def get_weather_data(lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
    """
    Get weather forecasts from the weather.gov API for the user's location.

    Parameters
    ----------
    lat: float
        latitude in degrees
    lon: float
        longitude in degrees

    Returns
    -------
    Dict[str, Any]
        The json containing the hourly weather forecast.
    """
    if lat is None or lon is None:
        # get the latitude and longitude from IP address
        ip_data = get_location_from_ip()
        lat, lon = ip_data["loc"].split(",")

    # look up the weather forecast endpoint for the given location
    points_response = requests.get(f"https://api.weather.gov/points/{lat},{lon}")
    points_endpoint = points_response.json()["properties"]["forecastHourly"]

    # now collect the weather forecast
    forecast_response = requests.get(points_endpoint)
    forecast_data = forecast_response.json()

    # next three hours
    next_3_hours = forecast_data["properties"]["periods"][:3]
    next_3_hours = [
        {
            "temperature": hour["temperature"],
            "rainfall_chance": hour["probabilityOfPrecipitation"]["value"],
            "description": hour["shortForecast"],
            "icon": hour["icon"],
        }
        for hour in next_3_hours
    ]
    return next_3_hours
