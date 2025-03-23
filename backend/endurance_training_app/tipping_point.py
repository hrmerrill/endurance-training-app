"""
Author: Hunter R. Merrill

Description: This script contains functions for computing the "tipping point" amount of time
spend exercising outdoors in the presence of air pollution. The "tipping point" is the point
at which the adverse health effects of air pollution outweigh the benefits of exercise.

Most of this script is adapted from the supplementary data of the following paper:
"Can air pollution negate the health benefits of cycling and walking?"
https://www.sciencedirect.com/science/article/pii/S0091743516000402#s0055
"""

import numpy as np

# metabolic equivalent of tasks. From "The Compendium of Physical Activities"
# https://cdn-links.lww.com/permalink/mss/a/mss_43_8_2011_06_13_ainsworth_202093_sdc1.pdf
MET = {
    "cycling": 6.8,  # 10 to 11.9 mph, leisure, slow, light effort
    "walking": 3.5,  # 2.8 to 3.2 mph, level, moderate pace, firm surface
    "running": 8.3,  # 5 mph (12min/mi)
}

# ventilation rates. Cycling, walking and resting I pulled from the spreadsheet; for running,
# I used my own data from Garmin. My breaths per minute are roughly 23 for cycling and 30
# for running, so I multiplied the cycling VR from the spreadsheet by 30/23. The units are
# m^3/hr.
VR = {
    "cycling": 2.55,
    "walking": 1.37,
    "running": 3.32,
    "resting": 0.609,
    "sleeping": 0.27,
}

# Relative risks. Under 1 for beneficial effects, over 1 for adverse effects.
# Cycling, walking, and PM2.5 I pulled from the spreadsheet. Running, I got from here:
# https://jamanetwork.com/journals/jamanetworkopen/fullarticle/2795598
RR = {
    "cycling": 0.87,
    "walking": 0.90,
    "running": 0.85,
    "pm2.5": 1.07,
}

# Pollution exposure ratios. Cycling and walking are from the spreadsheet. Running I took
# an average of the two.
PER = {
    "cycling": 2.0,
    "walking": 1.1,
    "running": 1.6,
}

# Standardized dose of MET-hours per week (i.e., "background contrast")
BC = 11.25

# Dose response: relative risk per 1 MET-hour per week
DOSE_RESPONSE = {k: v ** (1 / BC**0.5) for k, v in RR.items() if k != "pm2.5"}

# other constants
SLEEP_HRS_PER_NIGHT = 8
DAYS_PER_WEEK = 7
HRS_PER_DAY = 24


def calculate_no_exercise_concentration(aqi: float) -> float:
    """
    Calculate the concentration of PM2.5 inhaled per week with no exercise.

    Parameters
    ----------
    aqi: float
        The air quality index for PM2.5 (µg/m^3).

    Returns
    -------
    float
        The concentration of PM2.5 inhaled per week with no exercise (µg/week).
    """
    sleep_concentration = aqi * VR["sleeping"] * SLEEP_HRS_PER_NIGHT * DAYS_PER_WEEK
    resting_concentration = (
        aqi * VR["resting"] * (HRS_PER_DAY - SLEEP_HRS_PER_NIGHT) * DAYS_PER_WEEK
    )
    return sleep_concentration + resting_concentration


def calculate_inhaled_dose_per_week(
    aqi: float, activity: str, activity_hrs_per_day: np.ndarray
) -> np.ndarray:
    """
    Calculate the concentration of PM2.5 inhaled per week with exercise.

    Parameters
    ----------
    aqi: float
        The air quality index for PM2.5 (µg/m^3).
    activity: str
        The type of activity (cycling, walking, or running).
    activity_hrs_per_day: np.ndarray
        The hours per day spent doing the activity.

    Returns
    -------
    np.ndarray
        The concentration of PM2.5 inhaled per week with exercise (µg/week).
    """
    sleep_concentration = aqi * VR["sleeping"] * SLEEP_HRS_PER_NIGHT * DAYS_PER_WEEK
    resting_concentration = (
        aqi
        * VR["resting"]
        * (HRS_PER_DAY - SLEEP_HRS_PER_NIGHT - activity_hrs_per_day)
        * DAYS_PER_WEEK
    )
    active_concentration = aqi * VR[activity] * PER[activity] * activity_hrs_per_day * DAYS_PER_WEEK
    return sleep_concentration + resting_concentration + active_concentration


def calculate_increase_in_exposure(
    aqi: float, activity: str, activity_hrs_per_day: np.ndarray
) -> np.ndarray:
    """
    Calculate the increase in PM2.5 exposure due to exercise.

    Parameters
    ----------
    aqi: float
        The air quality index for PM2.5 (µg/m^3).
    activity: str
        The type of activity (cycling, walking, or running).
    activity_hrs_per_day: np.ndarray
        The hours per day spent doing the activity.

    Returns
    -------
    np.ndarray
        The increase in PM2.5 exposure due to exercise (µg/m^3).
    """
    no_exercise_concentration = calculate_no_exercise_concentration(aqi)
    exercise_concentration = calculate_inhaled_dose_per_week(aqi, activity, activity_hrs_per_day)
    return aqi * ((exercise_concentration / no_exercise_concentration) - 1.0)


def calculate_additional_relative_risk(
    aqi: float, activity: str, activity_hrs_per_day: np.ndarray
) -> np.ndarray:
    """
    Calculate the increase in relative risk of PM2.5 due to exercise.

    Parameters
    ----------
    aqi: float
        The air quality index for PM2.5 (µg/m^3).
    activity: str
        The type of activity (cycling, walking, or running).
    activity_hrs_per_day: np.ndarray
        The hours per day spent doing the activity.

    Returns
    -------
    np.ndarray
        The increase in relative risk of PM2.5 exposure due to exercise.
    """
    increase_in_exposure = calculate_increase_in_exposure(aqi, activity, activity_hrs_per_day)
    return np.exp(np.log(RR["pm2.5"]) * increase_in_exposure / 10)


def calculate_exercise_relative_risk(activity: str, activity_hrs_per_day: np.ndarray) -> np.ndarray:
    """
    Calculate the relative risk of exercise by duration.

    Parameters
    ----------
    activity: str
        The type of activity (cycling, walking, or running).
    activity_hrs_per_day: np.ndarray
        The hours per day spent doing the activity.

    Returns
    -------
    np.ndarray
        The relative risk of exercising for the given duration.
    """
    return DOSE_RESPONSE[activity] ** (
        (MET[activity] * activity_hrs_per_day * DAYS_PER_WEEK) ** 0.5
    )


def calculate_overall_relative_risk(
    aqi: float, activity: str, activity_hrs_per_day: np.ndarray
) -> np.ndarray:
    """
    Calculate the overall relative risk of exercise and PM2.5 due to exercise.

    Parameters
    ----------
    aqi: float
        The air quality index for PM2.5 (µg/m^3).
    activity: str
        The type of activity (cycling, walking, or running).
    activity_hrs_per_day: np.ndarray
        The hours per day spent doing the activity.

    Returns
    -------
    np.ndarray
        The overall relative risk of exercise and PM2.5 exposure due to exercise.
    """
    exercise_relative_risk = calculate_exercise_relative_risk(activity, activity_hrs_per_day)
    exposure_relative_risk = calculate_additional_relative_risk(aqi, activity, activity_hrs_per_day)
    return exercise_relative_risk * exposure_relative_risk


def calculate_tipping_point(aqi: float, activity: str) -> float:
    """
    Calculate the tipping point for the given activity and air quality index.

    Parameters
    ----------
    aqi: float
        The air quality index for PM2.5 (µg/m^3).
    activity: str
        The type of activity (cycling, walking, or running).

    Returns
    -------
    float
        The tipping point in hours per day.
    """
    activity_hrs_per_day = np.linspace(0, HRS_PER_DAY, 1000)
    overall_relative_risk = calculate_overall_relative_risk(aqi, activity, activity_hrs_per_day)
    return activity_hrs_per_day[np.argmin(overall_relative_risk)]
