# import requests
# import os
# from dotenv import load_dotenv
# from dataclasses import dataclass



# load_dotenv()


# api_key = os.getenv('API_KEY')
# # @dataclass
# # class WeatherData:
# #     pass


# def get_lat_lon(city_name, api_key):  # Keep it lowercase
   
#     resp = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={api_key}')

#     if resp.status_code == 200:
#         return resp.json()  
#     else:
#         return {"error": resp.status_code, "message": resp.text} 

# def get_current_weather(lat,lon,api_key) :
#     resp= requests.get('https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric').json()
#     print(resp)
# # def kel_to_cel(kelvin):
# #     celsius=kelvin-273.15
# #     return celsius

# # tem_kelvin=response['main']['temp']
# # temp_celsius= kel_to_cel(temp_kelvin)
# if __name__ =="__main__":
#     lat,lon = get_lat_lon('Mumbai',api_key)
#     get_current_weather(lat,lon,api_key)
# # print(get_lat_lon('Mumbai', api_key)) 




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
            "lat": convert_to_dms(lat),  
            "lon": convert_to_dms(lon, True),  
            "uv_index": uv_data['value'],  
            "location": location_name 
        }
        return weather_info
    return None

# Main route to display weather form and results
@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error_message = None
    if request.method == 'POST':
        city_name = request.form.get('city')  # Get city input from user
        user_name= request.form.get('User name')
        pref_climate=request.form.get('Preferred Climate:')

    return render_template('index.html', weather_data=weather_data, error_message=error_message)  # Render HTML with weather data or error message

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True, port=5001)

