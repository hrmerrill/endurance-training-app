import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from endurance_training_app import get_aqi_data, get_purpleair_data, get_weather_data


def get_all_data() -> Dict[str, Any]:
    """
    Get all data from the current location for the web app.

    Returns
    -------
    Dict[str, Any]
        The AirNow, PurpleAir, and weather forecast data for the current location.
    """
    data = {}
    data["aqi"] = get_aqi_data()
    data["purpleair"] = get_purpleair_data()
    data["weather"] = get_weather_data()
    return data


class RequestHandler(BaseHTTPRequestHandler):
    """Class for handling requests."""

    def do_GET(self) -> None:
        """do_GET method."""
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        data = get_all_data()
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
