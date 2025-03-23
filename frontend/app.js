function loadApp(url){
    fetch(url)
        .then(response => response.json())
        .then(data => {
            Chart.defaults.font.family = "Arial";

            // Populate workout widget
            document.getElementById("workout-summary").innerText = "Today's workout: 5km run";

            // Populate weather widget
            document.getElementById("weather-summary").innerText = data.weather.description;

            // Display the weather charts
            const ctx_temperature = document.getElementById("temperature-chart").getContext('2d');
            const temperature_chart = new Chart(ctx_temperature, {
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

            const ctx_rain = document.getElementById("rain-chart").getContext('2d');
            const rain_chart = new Chart(ctx_rain, {
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

            // Populate AQI widget
            const aqi = `AirNow forecast: ${data.aqi.AQI}`;
            document.getElementById("aqi-summary").innerText = aqi;
            document.getElementById("aqi-pill").style.background=data.aqi.pill_color_hex;
            document.getElementById("aqi-pill").style.color=data.aqi.text_color_hex;
            document.getElementById("aqi-pill").textContent = data.aqi.Category.Name;

            tipping_point_button = document.getElementById("tipping-point-pill");
            tipping_point_button.textContent = data.tipping_points.running;

            // when clicking, cycle through tipping points
            tipping_point_button.onclick = function() {
                if(tipping_point_button.textContent.includes("Running")) {
                    tipping_point_button.textContent = data.tipping_points.cycling;
                } else if(tipping_point_button.textContent.includes("Cycling")) {
                    tipping_point_button.textContent = data.tipping_points.walking;
                } else {
                    tipping_point_button.textContent = data.tipping_points.running;
                }
            }

            // Display PurpleAir data on the AQI widget
            const ctx_aqi = document.getElementById("aqi-chart").getContext('2d');
            const aqi_chart = new Chart(ctx_aqi, {
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
                                text: 'PurpleAir monitors near you-- last three hours',
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
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
}

async function locSuccessCallback(position) {
    const lat = position.coords.latitude;
    const lon = position.coords.longitude;
    loadApp(`http://localhost:8000/?lat=${lat}&lon=${lon}`);
}

function locErrorCallback(position) {
    loadApp("http://localhost:8000/");
}

document.addEventListener("DOMContentLoaded", () => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(locSuccessCallback, locErrorCallback);
    } else {
        loadApp("http://localhost:8000");
    }
});
