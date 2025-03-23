"""
Author: Hunter R. Merrill

Description: This script contains functions for getting recent AQI data from the
PurpleAir API.
"""

import os
from datetime import datetime, timedelta
from time import sleep
from typing import Any, Dict, List, Optional

import requests
from endurance_training_app.display_utils import get_color_from_aqi
from endurance_training_app.location_utils import create_bounding_box, get_location_from_ip


def get_purpleair_sensor_data_in_box(lon: float, lat: float, limit: int = 5) -> List[Any]:
    """
    Get outdoor PurpleAir sensor IDs within a 5km bounding box with recent high confidence.

    Parameters
    ----------
    lon: float
        longitude in degrees
    lat: float
        latitude in degrees
    limit: int
        The maximum number of sensors to return.

    Returns
    -------
    List
        The sensor IDs outdoors within the bounding box with recent high confidence values.
    """
    min_lat, min_lon, max_lat, max_lon = create_bounding_box(lon, lat, distance_km=5)
    url = "https://api.purpleair.com/v1/sensors"
    headers = {"X-API-Key": os.environ.get("PURPLEAIR_API_KEY")}
    params = {
        "fields": "confidence",
        "location_type": 0,  # outside only
        "max_age": 7200,  # last two hours
        "nwlat": max_lat,
        "nwlng": min_lon,
        "selat": min_lat,
        "selng": max_lon,
    }
    purpleair_response = requests.get(url=url, params=params, headers=headers)
    confident_sensors = [
        sensor[0] for sensor in purpleair_response.json()["data"] if sensor[1] >= 95
    ]
    if len(confident_sensors) > limit:
        return confident_sensors[:limit]
    return confident_sensors


def get_purpleair_sensor_history(sensor_ids: List[Any]) -> List[Dict[str, Any]]:
    """
    Get PurpleAir sensor history for the last 3 hours from a given set of sensor IDs.

    Parameters
    ----------
    sensor_ids: List
        List of sensor IDs

    Returns
    -------
    List[Dict[str, Any]]
        A list of dictionaries containing sensor history.
    """
    now = datetime.now()
    three_hours_ago = now - timedelta(hours=3)
    url = "https://api.purpleair.com/v1/sensors/"
    headers = {"X-API-Key": os.environ.get("PURPLEAIR_API_KEY")}
    params = {
        "fields": "pm2.5_atm",
        "start_timestamp": int(three_hours_ago.timestamp()),
        "end_timestamp": int(now.timestamp()),
        "average": 10,  # seconds
    }
    results = []
    for sensor_id in sensor_ids:
        params.update({"sensor_index": int(sensor_id)})
        purpleair_response = requests.get(
            url=f"{url}{sensor_id}/history", params=params, headers=headers
        )
        result = purpleair_response.json()
        results.append(result)
        sleep(1)

    return results


def prepare_purpleair_history_for_chartjs(aqi_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Prepare PurpleAir sensor history data for Chart.js plotting.

    Parameters
    ----------
    aqi_data: List[Dict[str, Any]]
        The AQI data from the PurpleAir API (output of get_purpleair_sensor_history)

    Returns
    -------
    List[Dict[str, Any]]
        The prepared data for Chart.js.
    """
    prepared_data = []
    for sensor_data in aqi_data:
        if "error" in sensor_data.keys():
            pass
        else:
            sorted_data = sorted(sensor_data["data"], key=lambda x: x[0])
            plot_data = [
                {"x": datetime.fromtimestamp(item[0]).strftime("%Y-%m-%d %H:%M:%S"), "y": item[1]}
                for item in sorted_data
            ]
            chart_color_hex = get_color_from_aqi(max([d["y"] for d in plot_data]))
            chartjs_data = {
                "label": sensor_data["sensor_index"],
                "data": plot_data,
                "borderColor": f"#{chart_color_hex}",
            }
            prepared_data.append(chartjs_data)
    return prepared_data


def get_purpleair_data(lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
    """
    Get recent AQI data from the PurpleAir API.

    Parameters
    ----------
    lat: float
        latitude in degrees
    lon: float
        longitude in degrees

    Returns
    -------
    Dict[str, Any]
        The AQI data from the PurpleAir API.
    """
    if lat is None or lon is None:
        # get the latitude and longitude from IP address
        ip_data = get_location_from_ip()
        lat, lon = ip_data["loc"].split(",")

    sensor_ids = get_purpleair_sensor_data_in_box(lon=float(lon), lat=float(lat))

    # get the sensor history for the last 24 hours
    sensor_history = get_purpleair_sensor_history(sensor_ids=sensor_ids)
    return prepare_purpleair_history_for_chartjs(sensor_history)
