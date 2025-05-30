"""
Author: Hunter R. Merrill

Description: This script contains functions for getting AQI forecasts from the
AirNow API.
"""

import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import requests
from endurance_training_app.display_utils import get_color_from_aqi
from endurance_training_app.location_utils import get_location_from_ip


def get_aqi_data(lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
    """
    Get AQI data from the AirNow API.

    Parameters
    ----------
    lat: float
        latitude in degrees
    lon: float
        longitude in degrees

    Returns
    -------
    Dict[str, Any]
        The AQI data from the AirNow API.
    """
    # get AirNow API key
    api_key = os.environ.get("AIRNOW_API_KEY")

    if lat is None or lon is None:
        # get the latitude and longitude from IP address
        ip_data = get_location_from_ip()
        lat, lon = ip_data["loc"].split(",")

    url = "https://www.airnowapi.org/aq/forecast/latLong/?format=application/json&"
    params = [f"latitude={lat}", f"longitude={lon}", f"API_KEY={api_key}"]
    param_string = "&".join(params)
    response = requests.get(url + param_string)

    # the response is a list of dictionairies by pollutant and date
    aqi_summaries = response.json()

    # get today's forecast. Use the pollutant with the highest AQI
    today = datetime.today().strftime("%Y-%m-%d")
    aqi_today = [summary for summary in aqi_summaries if summary["DateForecast"] == today]

    # sometimes all we get is tomorrow's.
    if not aqi_today:
        tomorrow = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        aqi_today = [summary for summary in aqi_summaries if summary["DateForecast"] == tomorrow]

    # in case a report is missing.
    try:
        o3_today = [summary for summary in aqi_today if summary["ParameterName"] == "O3"][0]
    except IndexError:
        o3_today = {"AQI": -1, "Category": {"Name": "Unavailable"}}

    try:
        pm_today = [summary for summary in aqi_today if summary["ParameterName"] == "PM2.5"][0]
    except IndexError:
        pm_today = {"AQI": -1, "Category": {"Name": "Unavailable"}}

    results = o3_today if o3_today["AQI"] > pm_today["AQI"] else pm_today
    results["pill_color_hex"] = "#" + get_color_from_aqi(results["AQI"])
    results["text_color_hex"] = "black" if results["AQI"] <= 100 else "white"

    # too much text in the discussion-- strip out two days' worth.
    results["Discussion"] = "\r\n\r\n".join(results["Discussion"].split("\r\n\r\n")[:2])
    return results
