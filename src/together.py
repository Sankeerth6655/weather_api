from flask import Flask, render_template, request, jsonify
import requests
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from storageutils import MySQLManager
from variables import CONFIG
import nltk
from nltk.stem import PorterStemmer
from datetime import datetime, timedelta
import requests




# Threshold for outdated data (e.g., 1 day)
UPDATE_THRESHOLD = timedelta(days=1)

# Load environment variables (API key)
load_dotenv()

app = Flask(__name__)
api_key = os.getenv('API_KEY')
 
nltk.download('punkt')

# Initialize stemmer
stemmer = PorterStemmer()
def stem_words(word):
    return stemmer.stem(word)

# Get latitude and longitude for a city using OpenWeatherMap Geo API
def get_lat_lon(city_name):
    resp = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={api_key}')
    if resp.status_code == 200:
        data = resp.json()
        if data:
            return data[0]['lat'], data[0]['lon'], data[0]['name']  # Return lat, lon, and city name
    return None, None, None  # Handle case when city is not found

# Convert decimal degrees to degrees, minutes, seconds (DMS) format
def convert_to_dms(degrees, is_longitude=False):
    d = int(degrees)
    m = int((abs(degrees) - abs(d)) * 60)
    s = (abs(degrees) - abs(d) - m / 60) * 3600
    direction = 'N' if degrees >= 0 else 'S' if not is_longitude else 'E' if degrees >= 0 else 'W'
    return f"{abs(d)}°{abs(m)}′{abs(int(s))}″{direction}"

# Get weather information using OpenWeatherMap Weather API and UV Index API
def get_current_weather(lat, lon, location_name):
    weather_resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric')
    uv_resp = requests.get(f'https://api.openweathermap.org/data/2.5/uvi?lat={lat}&lon={lon}&appid={api_key}')
    
    if weather_resp.status_code == 200 and uv_resp.status_code == 200:
        weather_data = weather_resp.json()
        uv_data = uv_resp.json()
        weather_info = {
            "temp": weather_data['main']['temp'],
            "clouds": weather_data['weather'][0]['description'],
            "humidity": weather_data['main']['humidity'],
            "pressure": weather_data['main']['pressure'],
            "wind_speed": weather_data['wind']['speed'],
            "sunrise": weather_data['sys']['sunrise'],
            "sunset": weather_data['sys']['sunset'],
            "icon": weather_data['weather'][0]['icon'],
            "lat": convert_to_dms(lat),
            "lon": convert_to_dms(lon, True),
            "uv_index": uv_data['value'],
            "location": location_name
        }
        return weather_info
    return None

# Get the user's current location using ipconfig.io
def get_current_location():
    resp = requests.get('https://ipconfig.io/json')
    if resp.status_code == 200:
        data = resp.json()
        return data['latitude'], data['longitude'], data['city']
    return None, None, None


# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error_message = None
    if request.method == 'POST':
        city_name = request.form.get('city')  # Get city input from user
        lat, lon, location_name = get_lat_lon(city_name)
        if lat and lon:
            weather_data = get_current_weather(lat, lon, location_name)
        else:
            error_message = "City not found. Please try again."
    else:
        lat, lon, location_name = get_current_location()
        if lat and lon:
            weather_data = get_current_weather(lat, lon, location_name)
        else:
            error_message = "Could not determine your location."

    return render_template('index.html', weather_data=weather_data, error_message=error_message)

@app.route('/store_location', methods=['GET', 'POST'])
def store_location():
    if request.method == 'GET':
        return render_template('indexx.html')

    latitude = request.form.get('latitude')
    longitude = request.form.get('longitude')

    if latitude and longitude:
        geolocator = Nominatim(user_agent="my_geopy_app")
        location = geolocator.reverse(f"{latitude}, {longitude}")

        if location:
            address = location.address
            
            # Fetch weather data using OpenWeatherMap API
            weather_api_key = os.getenv('API_KEY')
            
            weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={weather_api_key}&units=metric"
            print(f"Weather API URL: {weather_url}")  # Debugging line
            
            weather_response = requests.get(weather_url)
            print(f"Weather Response Status Code: {weather_response.status_code}")  # Debugging line
            print(f"Weather Response Data: {weather_response.json()}")  # Debugging line

            if weather_response.status_code == 200:
                weather_data = weather_response.json()
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
                print(f"Error fetching weather data: {weather_response.status_code}, {weather_response.json()}")
                return jsonify({"message": f"Error fetching weather data: {weather_response.status_code}"}), weather_response.status_code
        else:
            return jsonify({"message": "Location not found"}), 404
    else:
        return jsonify({"message": "Invalid latitude or longitude"}), 400



# Route for retrieving a location by name
@app.route('/retrieve_location', methods=['POST'])
def retrieve_location():
    location_name = request.form.get("loc")
    query = """SELECT * FROM locations WHERE name=%s"""
    coordinates = MySQLManager.execute_query(query, (location_name,), **CONFIG['database']['xyz'])
    if coordinates:
        return render_template('latlon.html', data=coordinates)
    else:
        return "Unable to process request"
    



@app.route('/locations_by_climate', methods=['GET', 'POST'])  # Allow both GET and POST methods
def get_locations_by_climate():
    locations = None
    if request.method == "POST":
        preferred_climate = request.form.get('climate')  # Get climate from form data
        if preferred_climate:
            # Prepare the pattern for matching
            pattern = preferred_climate.strip().lower()  # Clean up the input
            
            print(f"User input for climate: {preferred_climate}")  # Debugging output
            print(f"Pattern for match: {pattern}")  # Debugging output
            
            # Get all locations from the database
            query = """SELECT * FROM locations"""
            all_locations = MySQLManager.execute_query(query, (), **CONFIG['database']['xyz'])  # Pass an empty tuple as 'args'

            # Function to check if any word in the weather matches the pattern
            def is_word_match(weather, pattern):
                weather_words = weather.strip().lower().split()  # Split weather description into individual words
                for word in weather_words:
                    if pattern in word:  # Check if user input is part of any word
                        return True
                return False

            updated_locations = []

            for loc in all_locations:
                # Check if the location's weather matches the preferred climate
                if is_word_match(loc['weather'], pattern):
                    updated_locations.append(loc)

            print(f"Locations found: {updated_locations}")  # Debugging output

            if updated_locations:
                return render_template('locations.html', locations=updated_locations)
            else:
                message = "No suitable locations found from our data (last 24-hour period)."
                return render_template('locations.html', message=message), 404
                

        else:
            # Pass a message if climate preference is missing
            message = "Climate preference is required."
            return render_template('locations.html', message=message), 400
    return render_template("locations.html", message=None)  







# Run the Flask application
if __name__ == '__main__':
    app.run("0.0.0.0", port=4000, debug=True)
