import os
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests
from endurance_training_app.location_utils import create_bounding_box


def get_purpleair_sensor_data_in_box(lon: float, lat: float) -> List[Any]:
    """
    Get outdoor PurpleAir sensor IDs within a 5km bounding box with recent high confidence.

    Parameters
    ----------
    lon: float
        longitude in degrees
    lat: float
        latitude in degrees

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
        sensor[0] for sensor in purpleair_response.json()["data"] if sensor[1] > 90
    ]
    return confident_sensors


def get_purpleair_sensor_history(sensor_ids: List[Any]) -> List[Dict[str, Any]]:
    """
    Get PurpleAir sensor history for the last 24 hours from a given set of sensor IDs.

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
    yesterday = now - timedelta(days=1)
    url = "https://api.purpleair.com/v1/sensors/:sensor_index/history"
    headers = {"X-API-Key": os.environ.get("PURPLEAIR_API_KEY")}
    params = {
        "fields": "pm2.5_atm",
        "start_timestamp": int(yesterday.timestamp()),
        "end_timestamp": int(now.timestamp()),
        "average": 10,  # seconds
    }
    results = []
    for sensor_id in sensor_ids:
        params.update({"sensor_index": int(sensor_id)})
        purpleair_response = requests.get(url=url, params=params, headers=headers)
        result = purpleair_response.json()
        result.update({"sensor_index": int(sensor_id)})
        results.append(result)
    return results
