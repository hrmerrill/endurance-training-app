"""
Author: Hunter R. Merrill

Description: This script contains functions for getting AQI forecasts from the
AirNow API.
"""

import os
from datetime import datetime
from typing import Any, Dict

import requests
from endurance_training_app.location_utils import get_location_from_ip


def get_aqi_data() -> Dict[str, Any]:
    """
    Get AQI data from the AirNow API.

    Returns
    -------
    Dict[str, Any]
        The AQI data from the AirNow API.
    """
    # get AirNow API key
    api_key = os.environ.get("AIRNOW_API_KEY")

    # get the latitude and longitude from IP address
    ip_data = get_location_from_ip()

    # get FIPS code from location
    lat, lon = ip_data["loc"].split(",")

    url = "https://www.airnowapi.org/aq/forecast/latLong/?format=application/json&"
    params = [f"latitude={lat}", f"longitude={lon}", f"API_KEY={api_key}"]
    param_string = "&".join(params)
    response = requests.get(url + param_string)

    # the response is a list of dictionairies by pollutant and date
    aqi_summaries = response.json()

    # get today's forecast
    today = datetime.today().strftime("%Y-%m-%d")
    aqi_today = [summary for summary in aqi_summaries if summary["DateForecast"] == today]
    results = {}
    results["o3_aqi"] = [
        summary["AQI"] for summary in aqi_today if summary["ParameterName"] == "O3"
    ][0]
    results["pm_aqi"] = [
        summary["AQI"] for summary in aqi_today if summary["ParameterName"] == "PM2.5"
    ][0]
    results["discussion"] = aqi_today[0]["Discussion"]
    return results
