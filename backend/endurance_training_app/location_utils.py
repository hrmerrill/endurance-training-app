"""
Author: Hunter R. Merrill

Description: This script contains utility functions for obtaining location data.
"""

from typing import Any, Dict, Tuple

import numpy as np
import requests


def create_bounding_box(
    lon: float, lat: float, distance_km: float = 5
) -> Tuple[float, float, float, float]:
    """
    Create a bounding box around a given latitude and longitude.

    Parameters
    ----------
    lon: float
        The longitude in decimal degrees.
    lat: float
        The latitude in decimal degrees.
    distance_km: float
        The distance in kilometers to extend the bounding box in each direction.

    Returns
    -------
    Tuple[float, float, float, float]
        A tuple of (min_lat, min_lon, max_lat, max_lon) representing the bounding box.
    """
    earth_radius_km = 6378
    distance_rad = distance_km / earth_radius_km

    min_lat = lat - distance_rad * (180 / np.pi)
    max_lat = lat + distance_rad * (180 / np.pi)
    min_lon = lon - distance_rad * (180 / np.pi) / np.cos(lat * np.pi / 180)
    max_lon = lon + distance_rad * (180 / np.pi) / np.cos(lat * np.pi / 180)

    return min_lat, min_lon, max_lat, max_lon


def get_location_from_ip() -> Dict[str, Any]:
    """
    Get location information from IP address.

    Returns
    -------
    Dict[str, Any]
    """
    ip_response = requests.get("https://ipinfo.io/json")
    return ip_response.json()


def get_fips_from_location(lon: float, lat: float) -> str:
    """
    Get 5-digit FIPS code from latitude and longitude.

    Parameters
    ----------
    lon: float
        longitude in degrees
    lat: float
        latitude in degrees

    Returns
    -------
    str
        5-digit FIPS code; e.g., "01001".
    """
    base_url = "https://geocoding.geo.census.gov/geocoder/geographies/coordinates"
    params = f"?x={lon}&y={lat}&benchmark=4&vintage=423&format=json"
    fips_response = requests.get(base_url + params).json()
    county_data = fips_response["result"]["geographies"]["Counties"][0]
    fips_code = str(county_data["STATE"]) + str(county_data["COUNTY"])
    return fips_code
