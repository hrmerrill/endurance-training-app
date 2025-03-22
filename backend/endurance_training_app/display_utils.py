COLOR_MAPPING = {
    1: "00e400",
    2: "ffff00",
    3: "ff7e00",
    4: "ff0000",
    5: "8f3f97",
    6: "7e0023",
}


def get_color_from_aqi(aqi: float) -> str:
    """
    Get the color from the AQI.

    Parameters
    ----------
    aqi: float
        AQI

    Returns
    -------
    str
        The color in hex format.
    """
    if aqi <= 50:
        return COLOR_MAPPING[1]
    elif aqi <= 100:
        return COLOR_MAPPING[2]
    elif aqi <= 150:
        return COLOR_MAPPING[3]
    elif aqi <= 200:
        return COLOR_MAPPING[4]
    elif aqi <= 300:
        return COLOR_MAPPING[5]
    else:
        return COLOR_MAPPING[6]
