from flask import Flask, request, render_template, jsonify
from geopy.geocoders import Nominatim
from storageutils import MySQLManager
from variables import CONFIG
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('indexx.html')

@app.route('/store_location', methods=['POST'])
def store_location():
    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')
    
    if latitude and longitude:
        geolocator = Nominatim(user_agent="my_geopy_app")
        location = geolocator.reverse(f"{latitude}, {longitude}")
        
        if location:
            address = location.address
            
            # Fetch weather data using OpenWeatherMap API
            weather_api_key = os.getenv('API_KEY')
            weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_key}"
            weather_response = requests.get(weather_url)
            weather_data = weather_response.json()
            
            if weather_response.status_code == 200:
                weather_description = weather_data['weather'][0]['description']
                temperature = weather_data['main']['temp']
                
                # Store location and weather data in the database
                query = """INSERT INTO locations (name, latitude, longitude, weather, temperature) VALUES (%s, %s, %s, %s, %s)"""
                try:
                    MySQLManager.execute_query(query, (address, latitude, longitude, weather_description, temperature), **CONFIG['database']['xyz'])
                    return render_template('result.html', address=address, latitude=latitude, longitude=longitude, weather=weather_description, temperature=temperature)
                except Exception as error:
                    print("Error inserting location:", error)
                    return jsonify({"message": "Error inserting location"}), 500
            else:
                return jsonify({"message": "Error fetching weather data"}), 500
        else:
            return jsonify({"message": "Location not found"}), 404
    else:
        return jsonify({"message": "Invalid latitude or longitude"}), 400

@app.route('/retrieve_location', methods=['POST'])
def retrieve_location():
    location_name = request.form.get("loc")
    query = """SELECT * FROM locations WHERE name=%s"""
    coordinates = MySQLManager.execute_query(query, (location_name,), **CONFIG['database']['xyz'])
    if coordinates:
        return render_template('latlon.html', data=coordinates)
    else:
        return "Unable to process request"

if __name__ == '__main__':
    app.run(debug=True)
