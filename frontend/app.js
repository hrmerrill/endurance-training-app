// Three increasing weeks and one decreasing week, increasing overall for 12 weeks
const weeklyDistanceKm = {
    1: 28,
    2: 32,
    3: 36,
    4: 20,
    5: 40,
    6: 43,
    7: 48,
    8: 29,
    9: 51,
    10: 55,
    11: 60,
    12: 32,
}

// Modulate intensity and percentage of weekly volume
const dailyPercentages = {
    "Monday": 0.0,
    "Tuesday": 0.1,
    "Wednesday": 0.25, 
    "Thursday": 0.1,
    "Friday": 0.1,
    "Saturday": 0.15,
    "Sunday": 0.3,
}
const dailyZone = {
    "Monday": "Rest",
    "Tuesday": "Z2",
    "Wednesday": "Z1", 
    "Thursday": "Recovery",
    "Friday": "Z2",
    "Saturday": "Z1",
    "Sunday": "Z2",
}

// Choose a starting date
const startDate = new Date("2025-03-24");

// Get today's date
const today = new Date();
dayName = today.toLocaleDateString("en-US", { weekday: 'long' });

// Find out what week it is
const timeDelta = today.getTime() - startDate.getTime();
const week = Math.ceil(timeDelta / 1000 / 60 / 60 / 24 / 7);

// Populate workout widget with today's workout
distance = Math.round(weeklyDistanceKm[week] * dailyPercentages[dayName] / 1.609 * 10) / 10;
distancePill = document.getElementById("workout-distance");
distancePill.innerText = `${distance} miles`;

zone = document.getElementById("workout-zone");
zone.innerText = dailyZone[dayName];
if (dailyZone[dayName] == "Rest"){
    zone.style.background="rgb(255, 255, 255)";
    zone.style.border="1px solid black";
}
if (dailyZone[dayName] == "Z2"){
    zone.style.background="rgb(0, 128, 255)";
    zone.style.color="rgb(255, 255, 255)"
}

// Show the PM strength widget on Tuesdays and Fridays
if ((dayName == "Tuesday") || (dayName == "Friday")){
    strengthPill = document.getElementById("strength");
    strengthPill.style.display="inline-block";
    strengthPill.style.background="rgb(0, 0, 0)";
    strengthPill.style.color="rgb(255, 255, 255)";
}

// If rest day, don't show distance
if (dayName == "Monday"){
    document.getElementById("workout-distance").style.display="none";
}

// create a helper function to get the dates and distances for the program
function getDistanceData(startDate) {
    let currentDate = new Date(startDate);
    const twelveWeeksInMs = 12 * 7 * 24 * 60 * 60 * 1000;
    const endDate = new Date(currentDate.getTime() + twelveWeeksInMs);
    const dates = [];
    const distances = [];
    const fillColors = [];
    
    while (currentDate <= endDate) {
      // Find out what week it is
      let currentDelta = currentDate.getTime() - startDate.getTime();
      let currentWeek = Math.ceil(currentDelta / 1000 / 60 / 60 / 24 / 7);
      let currentDayName = currentDate.toLocaleDateString("en-US", { weekday: 'long' });
      let distance = weeklyDistanceKm[currentWeek] * dailyPercentages[currentDayName] / 1.609;
      distances.push(distance);

      let color;
      if (currentDate >= today) {
        color = "rgb(0, 128, 255)";
      } else {
        color = "rgb(200, 200, 200)";
      }
      
      fillColors.push(color);

      dates.push(new Date(currentDate));
      currentDate.setDate(currentDate.getDate() + 1);
    }
    return [dates, distances, fillColors];
  }

// now create a chart that shows the daily distance for the duration of the program
const distanceCanvas = document.getElementById("distance-chart");
let distanceChart;
let label;
let yValues;
var chartType = "none";
const minutePerMile = 12.5;
const [dates, distances, fillColors] = getDistanceData(startDate);

// display the chart if clicked
const distancePills = document.querySelectorAll("#workout-distance, #workout-zone");
distancePills.forEach(distancePill => {
    distancePill.addEventListener('click', function() {
        // destroy chart if it currently exists
        if (distanceChart) {
            distanceChart.destroy();
        }

        // cycle through distance, time, and no chart for each click
        if (chartType == "none") {
            chartType = "distance";
        } else if (chartType == "distance") {
            chartType = "time";
        } else {
            chartType = "none";
        }

        // depending on chart type, edit the data and labels
        if (chartType == "distance") {
            label = "Distance (miles)";
            yValues = distances;
        } else if (chartType == "time") {
            label = "Time (minutes)";
            yValues = distances.map(x => x * minutePerMile);
        }

        // show it if it should be showed
        if (chartType == "none") {
            distanceCanvas.style.display = "none";
        } else {
            distanceCanvas.style.display = "block";
            distanceChart = new Chart(distanceCanvas.getContext('2d'), {
                type: "bar",
                data: {
                    labels: dates,
                    datasets: [{
                        label: label,
                        data: yValues,
                        borderColor: "none",
                        backgroundColor: fillColors,
                    }],
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            title: {
                                display: true,
                                text: label,
                            },
                        },
                        x: {
                            title: {
                                display: false,
                            },
                            ticks: {
                                callback: function(val, index) {
                                    return dates[index].toLocaleDateString("en-US", { month: '2-digit', day: '2-digit' });
                                },
                            }
                        }
                    }
                }
            });
        }
    });
});

function loadWeather(latitude, longitude){
    fetch(`https://api.weather.gov/points/${latitude},${longitude}`)
        .then(response => response.json())
        .then(enpoint_data => {
            return fetch(enpoint_data.properties.forecastHourly);
        })
        .then(response => response.json())
        .then(forecastData => {

            let minTemp24Hours = forecastData.properties.periods.slice(0, 24).map(period => period.temperature).reduce((a, b) => Math.min(a, b));
            let maxTemp24Hours = forecastData.properties.periods.slice(0, 24).map(period => period.temperature).reduce((a, b) => Math.max(a, b));
            let minTemp3Hours = forecastData.properties.periods.slice(0, 3).map(period => period.temperature).reduce((a, b) => Math.min(a, b));
            let maxTemp3Hours = forecastData.properties.periods.slice(0, 3).map(period => period.temperature).reduce((a, b) => Math.max(a, b));
            let maxChanceRain24Hours = forecastData.properties.periods.slice(0, 24).map(period => period.probabilityOfPrecipitation.value).reduce((a, b) => Math.max(a, b));
            let maxChanceRain3Hours = forecastData.properties.periods.slice(0, 3).map(period => period.probabilityOfPrecipitation.value).reduce((a, b) => Math.max(a, b));

            // Creating space for visualization
            if (minTemp3Hours == maxTemp3Hours){
                maxTemp3Hours = minTemp3Hours + 0.1 * (maxTemp24Hours - minTemp24Hours);
            }
            if (maxChanceRain3Hours == 0){
                maxChanceRain3Hours = 1.0;
            }
            if (maxChanceRain24Hours == maxChanceRain3Hours){
                maxChanceRain24Hours = Math.min(maxChanceRain3Hours + 1.0, 100);
            }

            const data = {
                weather: {
                    min_temp_24_hrs: minTemp24Hours,
                    max_temp_24_hrs: maxTemp24Hours,
                    min_temp_3_hrs: minTemp3Hours,
                    max_temp_3_hrs: maxTemp3Hours,
                    max_chance_rain_24_hrs: maxChanceRain24Hours,
                    max_chance_rain_3_hrs: maxChanceRain3Hours,
                    current_temperature: forecastData.properties.periods[0].temperature,
                    description: forecastData.properties.periods[0].shortForecast
                }
            };

            Chart.defaults.font.family = "Arial";

            // Populate weather widget
            document.getElementById("weather-summary").innerText = `${data.weather.current_temperature}°F - ${data.weather.description}`;

            // Display the weather charts
            const ctxTemperature = document.getElementById("temperature-chart").getContext('2d');
            const temperatureChart = new Chart(ctxTemperature, {
                type: "bar",
                data: {
                    labels: ["temperature"],
                    datasets: [{
                        label: "next 24 hours",
                        data: [[data.weather.min_temp_24_hrs, data.weather.min_temp_3_hrs]],
                        backgroundColor: "rgb(200, 200, 200)",
                      }, 
                      {
                        data: [[data.weather.min_temp_3_hrs, data.weather.max_temp_3_hrs]],
                        backgroundColor: "rgb(47, 0, 255)",
                      }, 
                      {
                        data: [[data.weather.max_temp_3_hrs, data.weather.max_temp_24_hrs]],
                        backgroundColor: "rgb(200, 200, 200)",
                      }]
                },
                options: {
                    aspectRatio: 8,
                    maintainAspectRatio: true,
                    responsive: false,
                    indexAxis: "y",
                    scales: {
                        x: {
                            min: data.weather.min_temp_24_hrs,
                            max: data.weather.max_temp_24_hrs,
                            grid: {
                                display: false,
                            },
                            title: {
                                display: true,
                                text: 'Temperature (°F)',
                            },
                            stacked: false,
                        },
                        y: {
                            stacked: true,
                            display: false,
                        },
                    },
                    plugins: {
                        legend: {
                            display: false,
                        },
                    }
                }
            });

            const ctxRain = document.getElementById("rain-chart").getContext('2d');
            const rainChart = new Chart(ctxRain, {
                type: "bar",
                data: {
                    labels: ["rain"],
                    datasets: [ 
                        {
                            label: "next 3 hours",
                            data: [[0, data.weather.max_chance_rain_3_hrs]],
                            backgroundColor: "rgb(47, 0, 255)",
                        },
                        {
                            label: "next 24 hours",
                            data: [[data.weather.max_chance_rain_3_hrs, data.weather.max_chance_rain_24_hrs]],
                            backgroundColor: "rgb(200, 200, 200)",
                      }]
                },
                options: {
                    aspectRatio: 8,
                    maintainAspectRatio: true,
                    responsive: false,
                    indexAxis: "y",
                    scales: {
                        x: {
                            min: 0,
                            max: 100,
                            grid: {
                                display: false,
                            },
                            title: {
                                display: true,
                                text: 'Chance of rain (%)',
                            },
                            stacked: false,
                        },
                        y: {
                            stacked: true,
                            display: false,
                        },
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: "bottom",
                        },
                    }
                }
            });
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}

// Loading PurpleAir is a bit slower (PurpleAir History API is rate-limited)
async function loadPurpleair(url){
    fetch(url)
        .then(response => response.json())
        .then(data => {
            Chart.defaults.font.family = "Arial";

            // Display PurpleAir data on the AQI widget
            const ctxAqiElement = document.getElementById("aqi-chart");
            ctxAqiElement.style.display = "block";
            const aqiChart = new Chart(ctxAqiElement.getContext('2d'), {
                type: 'line',
                data: {
                    datasets: data.purpleair
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    elements: {
                        point:{
                            radius: 0
                        }
                    },
                    scales: {
                        x: {
                            title: {
                                display: true,
                                text: 'PurpleAir monitors near you-- last five hours',
                            },
                            ticks: {
                                callback: function(val, index) {
                                    return ;
                                    // return new Date(val);
                                },
                            }
                        },
                        y: {
                            min: 0,
                        }
                    }
                }
            });
            purpleairPill = document.getElementById("purpleair-pill");
            purpleairPill.style.display = "none";
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}

function loadAQI(url){
    fetch(url)
        .then(response => response.json())
        .then(data => {

            purpleairPill = document.getElementById("purpleair-pill");

            // Populate AQI widget
            aqiPill = document.getElementById("aqi-pill");
            aqiPill.style.background=data.aqi.pill_color_hex;
            aqiPill.style.color=data.aqi.text_color_hex;
            aqiPill.textContent = `${data.aqi.AQI} - ${data.aqi.Category.Name}`;
            aqiPill.addEventListener('click', function() {
                const aqiText = document.getElementById("aqi-description");
                const aqiDiscussion = document.getElementById("aqi-discussion");
                if (aqiText.style.display === "none") {
                    aqiText.style.display = "block";
                    aqiText.style.fontSize = "12px";
                    aqiText.style.color = "rgb(100, 100, 100)";

                    aqiDiscussion.style.display = "block";
                    aqiDiscussion.style.fontSize = "14px";
                    aqiDiscussion.style.color = "rgb(0, 0, 0)";
                    aqiDiscussion.style.whiteSpace = "pre-wrap";
                    aqiDiscussion.textContent = data.aqi.Discussion;

                    purpleairPill.style.display = "inline-block";
                } else {
                    aqiText.style.display = "none";
                    aqiDiscussion.style.display = "none";
                    purpleairPill.style.display = "none";
                }
                });

            purpleairPill.addEventListener('click', function() {
                const urlElements = url.split("&");
                const urlSubset = urlElements.pop();
                const urlNoSubset = urlElements.join("&");
                const urlPurpleair = `${urlNoSubset}&subset=purpleair`;
                purpleairPill.textContent = "Loading PurpleAir data...";
                loadPurpleair(urlPurpleair);
            });

            tippingPointRun = document.getElementById("tipping-point-pill-run");
            tippingPointBike = document.getElementById("tipping-point-pill-bike");
            tippingPointWalk = document.getElementById("tipping-point-pill-walk");

            tippingPointRun.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="6" height="6" fill="currentColor" class="icon" viewBox="0 0 448 512">
                            <path d="M320 48a48 48 0 1 0 -96 0 48 48 0 1 0 96 0zM125.7 175.5c9.9-9.9 23.4-15.5 37.5-15.5c1.9 0 3.8 .1 5.6 .3L137.6 254c-9.3 28 1.7 58.8 26.8 74.5l86.2 53.9-25.4 88.8c-4.9 17 5 34.7 22 39.6s34.7-5 39.6-22l28.7-100.4c5.9-20.6-2.6-42.6-20.7-53.9L238 299l30.9-82.4 5.1 12.3C289 264.7 323.9 288 362.7 288l21.3 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-21.3 0c-12.9 0-24.6-7.8-29.5-19.7l-6.3-15c-14.6-35.1-44.1-61.9-80.5-73.1l-48.7-15c-11.1-3.4-22.7-5.2-34.4-5.2c-31 0-60.8 12.3-82.7 34.3L57.4 153.4c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0l23.1-23.1zM91.2 352L32 352c-17.7 0-32 14.3-32 32s14.3 32 32 32l69.6 0c19 0 36.2-11.2 43.9-28.5L157 361.6l-9.5-6c-17.5-10.9-30.5-26.8-37.9-44.9L91.2 352z"/>
                        </svg> ${data.tipping_points.running}`;
            tippingPointBike.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="6" height="6" fill="currentColor" class="icon" viewBox="0 0 640 512">
                            <path d="M400 96a48 48 0 1 0 0-96 48 48 0 1 0 0 96zm27.2 64l-61.8-48.8c-17.3-13.6-41.7-13.8-59.1-.3l-83.1 64.2c-30.7 23.8-28.5 70.8 4.3 91.6L288 305.1 288 416c0 17.7 14.3 32 32 32s32-14.3 32-32l0-128c0-10.7-5.3-20.7-14.2-26.6L295 232.9l60.3-48.5L396 217c5.7 4.5 12.7 7 20 7l64 0c17.7 0 32-14.3 32-32s-14.3-32-32-32l-52.8 0zM56 384a72 72 0 1 1 144 0A72 72 0 1 1 56 384zm200 0A128 128 0 1 0 0 384a128 128 0 1 0 256 0zm184 0a72 72 0 1 1 144 0 72 72 0 1 1 -144 0zm200 0a128 128 0 1 0 -256 0 128 128 0 1 0 256 0z"/>                      
                        </svg> ${data.tipping_points.cycling}`;
            tippingPointWalk.innerHTML = `<svg xmlns="http://www.w3.org/2000/svg" width="6" height="6" fill="currentColor" class="icon" viewBox="0 0 448 512">
                            <path d="M160 48a48 48 0 1 1 96 0 48 48 0 1 1 -96 0zM126.5 199.3c-1 .4-1.9 .8-2.9 1.2l-8 3.5c-16.4 7.3-29 21.2-34.7 38.2l-2.6 7.8c-5.6 16.8-23.7 25.8-40.5 20.2s-25.8-23.7-20.2-40.5l2.6-7.8c11.4-34.1 36.6-61.9 69.4-76.5l8-3.5c20.8-9.2 43.3-14 66.1-14c44.6 0 84.8 26.8 101.9 67.9L281 232.7l21.4 10.7c15.8 7.9 22.2 27.1 14.3 42.9s-27.1 22.2-42.9 14.3L247 287.3c-10.3-5.2-18.4-13.8-22.8-24.5l-9.6-23-19.3 65.5 49.5 54c5.4 5.9 9.2 13 11.2 20.8l23 92.1c4.3 17.1-6.1 34.5-23.3 38.8s-34.5-6.1-38.8-23.3l-22-88.1-70.7-77.1c-14.8-16.1-20.3-38.6-14.7-59.7l16.9-63.5zM68.7 398l25-62.4c2.1 3 4.5 5.8 7 8.6l40.7 44.4-14.5 36.2c-2.4 6-6 11.5-10.6 16.1L54.6 502.6c-12.5 12.5-32.8 12.5-45.3 0s-12.5-32.8 0-45.3L68.7 398z"/>
                      </svg> ${data.tipping_points.walking}`;

            // when clicking, cycle through tipping points and show text
            const pills = document.querySelectorAll('.pill-tab');

            pills.forEach(pill => {
                pill.addEventListener('click', function() {
                // Remove 'top' class from all pills
                pills.forEach(p => p.classList.remove('top'));

                // Add 'top' class to the clicked pill
                this.classList.add('top');

                // Adjust the z-index of the clicked item.
                const pillRow = document.querySelector(".pill-tab-row")
                const children = Array.from(pillRow.children);
                const clickedIndex = children.indexOf(this);

                children.forEach((child, index) => {
                    if(index < clickedIndex){
                    child.style.zIndex = 1;
                    }else if(index === clickedIndex){
                    child.style.zIndex = 2;
                    }else{
                    child.style.zIndex = 0;
                    }
                })

                // display the description if clicked
                const text = document.getElementById("tipping-point-description");
                if (text.style.display === "none") {
                    text.style.display = "block";
                    text.style.fontSize = "12px";
                    text.style.color = "rgb(100, 100, 100)";
                } else {
                    text.style.display = "none";
                }
                });
            });
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}

// determine whether to fetch from localhost, raspberrypi, or AWS
let url;
let port = "";
var transferProtocol = window.location.protocol;
const hostname = window.location.hostname;
console.log(`running on ${hostname}`);

// if it's running on my raspberry pi, url is the hostname
if (hostname === "raspberrypi.local"){
    url = hostname;
    port = ":8081";
// if it's running on my website
} else if (hostname.includes(".com")) {
    url = `api.${hostname}`;
// otherwise, attempt to use localhost
} else {
    url = "localhost";
    transferProtocol = "http:";
    port = ":8081";
}

// We will try to get a more precise location from the browser
async function locSuccessCallback(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    loadWeather(lat, lon);
    loadAQI(`${transferProtocol}//${url}${port}/?lat=${lat}&lon=${lon}&subset=aqi`);
}

function locErrorCallback(position) {
    fetch(`https://ipinfo.io/json`)
    .then(response => response.json())
    .then(data => {
        const lat = data.loc.split(",")[0];
        const lon = data.loc.split(",")[1];
        loadWeather(lat, lon);
        loadAQI(`${transferProtocol}//${url}${port}/?lat=${lat}&lon=${lon}&subset=aqi`);
    })
    .catch(error => {
        console.error("Error fetching data:", error);
    });
}

document.addEventListener("DOMContentLoaded", () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(locSuccessCallback, locErrorCallback);
    } else {
        fetch(`https://ipinfo.io/json`)
        .then(response => response.json())
        .then(data => {
            const lat = data.loc.split(",")[0];
            const lon = data.loc.split(",")[1];
            loadWeather(lat, lon);
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
        loadAQI(`${transferProtocol}//${url}${port}?subset=aqi`);
    }
});
