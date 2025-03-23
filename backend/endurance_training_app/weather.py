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

    # get summaries
    min_temp_24_hrs = min(
        [hour["temperature"] for hour in forecast_data["properties"]["periods"][:24]]
    )
    max_temp_24_hrs = max(
        [hour["temperature"] for hour in forecast_data["properties"]["periods"][:24]]
    )
    min_temp_3_hrs = min(
        [hour["temperature"] for hour in forecast_data["properties"]["periods"][:3]]
    )
    max_temp_3_hrs = max(
        [hour["temperature"] for hour in forecast_data["properties"]["periods"][:3]]
    )

    max_chance_rain_24_hrs = max(
        [
            hour["probabilityOfPrecipitation"]["value"]
            for hour in forecast_data["properties"]["periods"][:24]
        ]
    )
    max_chance_rain_3_hrs = max(
        [
            hour["probabilityOfPrecipitation"]["value"]
            for hour in forecast_data["properties"]["periods"][:3]
        ]
    )

    weather = {
        "min_temp_24_hrs": min_temp_24_hrs,
        "max_temp_24_hrs": max_temp_24_hrs,
        "max_chance_rain_24_hrs": max_chance_rain_24_hrs,
        "max_chance_rain_3_hrs": max_chance_rain_3_hrs,
        "min_temp_3_hrs": min_temp_3_hrs,
        "max_temp_3_hrs": max_temp_3_hrs,
        "description": forecast_data["properties"]["periods"][0]["shortForecast"]
        .lower()
        .capitalize(),
    }
    return weather
