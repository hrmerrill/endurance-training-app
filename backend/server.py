import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional

from endurance_training_app import get_aqi_data, get_purpleair_data, get_weather_data


def get_all_data(lat: Optional[float] = None, lon: Optional[float] = None) -> Dict[str, Any]:
    """
    Get all data from the current location for the web app.

    Parameters
    ----------
    lat: float
        latitude in degrees
    lon: float
        longitude in degrees

    Returns
    -------
    Dict[str, Any]
        The AirNow, PurpleAir, and weather forecast data for the current location.
    """
    data = {}
    data["aqi"] = get_aqi_data(lon=lon, lat=lat)
    data["purpleair"] = get_purpleair_data(lon=lon, lat=lat)
    data["weather"] = get_weather_data(lon=lon, lat=lat)
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

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        data = get_all_data(lon=lon, lat=lat)
        self.wfile.write(json.dumps(data).encode("utf-8"))


def run(handler_class: BaseHTTPRequestHandler = RequestHandler, port: int = 8000) -> None:
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
    run()
