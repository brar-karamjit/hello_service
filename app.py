import os

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
OPEN_METEO_URL = os.getenv("OPEN_METEO_URL", "https://api.open-meteo.com/v1/forecast")

@app.route('/')
def hello():
    return 'Hello Service online — cross-app call succeeded.'


@app.route('/weather')
def weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if lat is None or lon is None:
        return jsonify({"error": "Missing required query params: lat, lon"}), 400

    try:
        latitude = float(lat)
        longitude = float(lon)
    except ValueError:
        return jsonify({"error": "Invalid lat/lon. Values must be numeric."}), 400

    if not (-90 <= latitude <= 90) or not (-180 <= longitude <= 180):
        return jsonify({"error": "lat/lon out of valid range"}), 400

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": "true",
        "timezone": "auto",
    }

    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=6)
        response.raise_for_status()
        provider_payload = response.json()
    except requests.RequestException:
        return jsonify({"error": "Weather provider unavailable"}), 502

    current_weather = provider_payload.get("current_weather")
    if not current_weather:
        return jsonify({"error": "Weather data missing from provider"}), 502

    return jsonify({
        "latitude": latitude,
        "longitude": longitude,
        "current_weather": current_weather,
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
