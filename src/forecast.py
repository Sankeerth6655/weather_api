# response time is too high
# import os
# import time
# from dotenv import load_dotenv
# import requests
# from flask import Flask, render_template, request
# from variables import CONFIG

# load_dotenv()

# app = Flask(__name__)

# @app.route('/', methods=['GET', 'POST'])
# def index():
#     forecast_data = None
#     error_message = None

#     if request.method == 'POST':
#         location = request.form['location']
#         forecast_data, error_message = get_forecast_data(location)

#     return render_template('foreacast.html', forecast_data=forecast_data, error_message=error_message)

# def get_forecast_data(location):
#      api_key = os.getenv('API_KEY')
#      start_time = time.time()
#      response = requests.get(f'http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={api_key}&exclude=alerts,hourly,minutely,current&units=metric')
#      end_time = time.time()
    
#     # Calculate the elapsed time
#      elapsed_time = end_time - start_time
    
#     # Log the time taken
#      print(f"Time taken to fetch data for {location}: {elapsed_time:.2f} seconds")
    
#      if response.status_code == 200:
#         data = response.json()
#         return process_forecast_data(data), None
#      else:
#          return None, "Unable to fetch data for the given location."

# def process_forecast_data(data):
#     # Process the response data and extract necessary information
#     forecast = []
#     for entry in data['list'][:8]:  # Get the first 8 entries (every 3 hours)
#         forecast.append({
#             'date': entry['dt_txt'],
#             'temp': entry['main']['temp'],
#             'icon': entry['weather'][0]['icon'],
#             'description': entry['weather'][0]['description'],
#             'humidity': entry['main']['humidity'],
#             'wind_speed': entry['wind']['speed']
#         })
#     return forecast

# if __name__ == '__main__':
#     app.run(debug=True)
