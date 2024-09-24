from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv

# Load environment variables (API key)
load_dotenv()

app = Flask(__name__)
api_key = os.getenv('API_KEY')

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
            "wind_speed": weather_data['wind']['speed'],  # Add wind speed
            "sunrise": weather_data['sys']['sunrise'],  # Add sunrise time
            "sunset": weather_data['sys']['sunset'],  # Add sunset time
            "icon": weather_data['weather'][0]['icon'],  # Add weather icon
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

    return render_template('index.html', weather_data=weather_data, error_message=error_message)  # Render HTML with weather data or error message

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True, port=5001)


# from flask import Flask, render_template, request
# import requests
# import os
# from dotenv import load_dotenv
# from geopy.geocoders import Nominatim

# # Load environment variables (API key)
# load_dotenv()

# app = Flask(__name__)
# api_key = os.getenv('API_KEY')

# # Get latitude and longitude for a city using OpenWeatherMap Geo API
# def get_lat_lon(city_name):
#     resp = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={api_key}')
#     if resp.status_code == 200:
#         data = resp.json()
#         if data:
#             return data[0]['lat'], data[0]['lon'], data[0]['name']  # Return lat, lon, and city name
#     return None, None, None  # Handle case when city is not found

# # Convert decimal degrees to degrees, minutes, seconds (DMS) format
# def convert_to_dms(degrees, is_longitude=False):
#     d = int(degrees)
#     m = int((abs(degrees) - abs(d)) * 60)
#     s = (abs(degrees) - abs(d) - m / 60) * 3600
#     direction = 'N' if degrees >= 0 else 'S' if not is_longitude else 'E' if degrees >= 0 else 'W'
#     return f"{abs(d)}°{abs(m)}′{abs(int(s))}″{direction}"

# # Get weather information using OpenWeatherMap Weather API and UV Index API
# def get_current_weather(lat, lon, location_name):
#     weather_resp = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric')
#     uv_resp = requests.get(f'https://api.openweathermap.org/data/2.5/uvi?lat={lat}&lon={lon}&appid={api_key}')
    
#     if weather_resp.status_code == 200 and uv_resp.status_code == 200:
#         weather_data = weather_resp.json()
#         uv_data = uv_resp.json()
#         weather_info = {
#             "temp": weather_data['main']['temp'],
#             "clouds": weather_data['weather'][0]['description'],
#             "humidity": weather_data['main']['humidity'],
#             "pressure": weather_data['main']['pressure'],
#             "wind_speed": weather_data['wind']['speed'],  # Add wind speed
#             "sunrise": weather_data['sys']['sunrise'],  # Add sunrise time
#             "sunset": weather_data['sys']['sunset'],  # Add sunset time
#             "icon": weather_data['weather'][0]['icon'],  # Add weather icon
#             "lat": convert_to_dms(lat),  
#             "lon": convert_to_dms(lon, True),  
#             "uv_index": uv_data['value'],  
#             "location": location_name 
#         }
#         return weather_info
#     return None

# # Get the user's current location using geopy
# def get_current_location():
#     geolocator = Nominatim(user_agent="weather_app")
#     location = geolocator.geocode("Your Address Here")  # Replace with a method to get the user's address
#     if location:
#         return location.latitude, location.longitude, location.address
#     return None, None, None

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     weather_data = None
#     error_message = None
#     if request.method == 'POST':
#         city_name = request.form.get('city')  # Get city input from user
#         lat, lon, location_name = get_lat_lon(city_name)
#         if lat and lon:
#             weather_data = get_current_weather(lat, lon, location_name)
#         else:
#             error_message = "City not found. Please try again."
#     else:
#         lat, lon, location_name = get_current_location()
#         if lat and lon:
#             weather_data = get_current_weather(lat, lon, location_name)
#         else:
#             error_message = "Could not determine your location."

#     return render_template('index.html', weather_data=weather_data, error_message=error_message)  # Render HTML with weather data or error message

# # Run the Flask application
# if __name__ == "__main__":
#     app.run(debug=True, port=5001)
