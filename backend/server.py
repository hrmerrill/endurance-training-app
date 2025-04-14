import argparse
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional

import numpy as np
from endurance_training_app import (
    calculate_tipping_point,
    get_aqi_data,
    get_purpleair_data,
    get_weather_data,
)


def get_all_data(
    lat: Optional[float] = None, lon: Optional[float] = None, subset: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all data from the current location for the web app.

    Parameters
    ----------
    lat: float
        latitude in degrees
    lon: float
        longitude in degrees
    subset: str
        subset of data to return

    Returns
    -------
    Dict[str, Any]
        The AirNow, PurpleAir, and weather forecast data for the current location.
    """
    data = {}
    if subset == "aqi":
        data["aqi"] = get_aqi_data(lon=lon, lat=lat)
        data["purpleair"] = get_purpleair_data(lon=lon, lat=lat)
    elif subset == "weather":
        data["weather"] = get_weather_data(lon=lon, lat=lat)
    else:
        data["aqi"] = get_aqi_data(lon=lon, lat=lat)
        data["purpleair"] = get_purpleair_data(lon=lon, lat=lat)
        data["weather"] = get_weather_data(lon=lon, lat=lat)

    if subset is None or subset == "aqi":
        # use the maximum of the AirNow forecast and the average purpleair data to find tipping points
        purpleair_avg_aqi = np.mean(
            [np.mean([x["y"] for x in d["data"]]) for d in data["purpleair"]]
        )
        aqi = max([data["aqi"]["AQI"], purpleair_avg_aqi])
        data["tipping_points"] = {}
        for activity in ["cycling", "walking", "running"]:
            tipping_point_hrs = calculate_tipping_point(aqi, activity)
            if tipping_point_hrs < 1:
                data["tipping_points"][activity] = f"{tipping_point_hrs*60:.0f} mins"
            else:
                data["tipping_points"][activity] = f"{tipping_point_hrs:.1f} hrs"
    return data


class RequestHandler(BaseHTTPRequestHandler):
    """Class for handling requests."""

    def do_GET(self) -> None:
        lon, lat = None, None
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        if "lon" in query_params and "lat" in query_params:
            lon = float(query_params["lon"][0])
            lat = float(query_params["lat"][0])
        if "subset" in query_params:
            subset = query_params["subset"][0]
        else:
            subset = None

        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-type", "application/json")
        self.end_headers()
        data = get_all_data(lon=lon, lat=lat, subset=subset)
        self.wfile.write(json.dumps(data).encode("utf-8"))


def run(handler_class: BaseHTTPRequestHandler = RequestHandler, port: int = 8081) -> None:
    """
    Run the server.

    Parameters
    ----------
    handler_class: BaseHTTPRequestHandler
        handler class
    port: int
        port
    """
    server_address = ("", port)
    httpd = HTTPServer(server_address, handler_class)
    print(f"Starting server on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the server.")
    parser.add_argument(
        "--port",
        type=int,
        default=8081,
        help="Port on which to run the server (default: 8081)",
    )
    args = parser.parse_args()
    run(port=args.port)
