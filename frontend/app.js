document.addEventListener("DOMContentLoaded", () => {
    fetch("http://localhost:8000/data")
        .then(response => response.json())
        .then(data => {
            // Populate workout widget
            document.getElementById("workout-summary").innerText = "Today's workout: 5km run";

            // Populate weather widget
            const weather = data.weather.map(hour => `${hour.temperature}°C, ${hour.description}`).join("\n");
            document.getElementById("weather-summary").innerText = weather;

            // Populate AQI widget
            const aqi = `AQI: ${data.aqi.AQI}, ${data.aqi.Category.Name}`;
            document.getElementById("aqi-summary").innerText = aqi;
        })
        .catch(error => {
            console.error("Error fetching data:", error);
        });
});