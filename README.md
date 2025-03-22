# Endurance Training App

**Author**: Hunter R. Merrill

## Description
This repo contains code for a web app that assists with endurance training. A user will typically view this app daily to obtain information and recommendations to assist with planning the day's exercises. The target hardware for this web app is either a smartphone or a wall-mounted touchscreen.

The home page displays three clickable widgets:
1. Recommended workout: displays the recommended workout for today.
2. Weather: displays the forecasted weather for the day.
3. AQI: displays the current and forecasted air quality index.

On the homepage, the widgets display a short summary of information, and clicking each widget will take the user to a new view containing more details. Code for the frontend is in the `frontend` subdirectory.

The backend Python server retrieves weather forecasts from the weather.gov API, AQI information from the PurpleAir API, and recommended workout information from a local file. Code for the backend is in the `backend` subdirectory.

## Files
* `backend` contains Python scripts that run the backend of the app.
  - `server.py` contains a server to serve up the data to the frontend.
  - `endurance_training_app` contains a python package with the modules required to run the server. The package and dependencies are managed by Poetry through the `pyproject.toml` file (which auto-generates the `poetry.lock` file).
* `frontend` contains Javascript and CSS to create the web app.
  - `styles.css` contains style definitions for objects in the web app.
  - `index.html` contains the static contents and layout of the page.
  - `app.js` contains the dynamic contents, loading data from the backend server.