from flask import Flask, jsonify, request

app = Flask(__name__)

# Simulated weather data (like a small database)
weather_data = {
    "Delhi": {"temperature": "35°C", "condition": "Sunny"},
    "Mumbai": {"temperature": "30°C", "condition": "Cloudy"},
    "Bangalore": {"temperature": "28°C", "condition": "Rainy"}
}

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')  # Get city from client request
    if city in weather_data:
        return jsonify({"status": "success", "data": weather_data[city]})
    else:
        return jsonify({"status": "error", "message": "City not found"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
