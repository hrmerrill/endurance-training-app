document.addEventListener("DOMContentLoaded", () => {
    fetch("http://localhost:8000/")
        .then(response => response.json())
        .then(data => {
            // Populate workout widget
            document.getElementById("workout-summary").innerText = "Today's workout: 5km run";

            // Populate weather widget
            // const weather = data.weather.map(hour => `${hour.temperature}°C, ${hour.description}`).join("\n");
            const weather = "test";
            document.getElementById("weather-summary").innerText = weather;

            // Populate AQI widget
            const aqi = `AirNow Forecast: ${data.aqi.AQI}`;
            document.getElementById("aqi-summary").innerText = aqi;
            document.getElementById("aqi-pill").style.background=data.aqi.pill_color_hex;
            document.getElementById("aqi-pill").style.color=data.aqi.text_color_hex;
            document.getElementById("aqi-pill").textContent = data.aqi.Category.Name;

            // Display PurpleAir data on the AQI widget
            Chart.defaults.font.family = "Arial";
            const ctx = document.getElementById("aqi-chart").getContext('2d');
            const aqi_chart = new Chart(ctx, {
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
                                text: 'nearby PurpleAir monitors-- last three hours',
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
});
