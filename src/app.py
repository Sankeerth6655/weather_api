from flask import Flask, request, jsonify, render_template
import mysql.connector
from variables import CONFIG  # Import the CONFIG variable

app = Flask(__name__)

# Database configuration from variables.py
db_config = CONFIG['database']['xyz']

# Establish a database connection
def get_db_connection():
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database'],
        port=db_config['port']
    )
    return conn

# Route to render the weather preferences page
@app.route('/weather-preferences')
def weather_preferences():
    return render_template('weather_preferences.html')

# API endpoint to get location details by weather
@app.route('/get-location', methods=['GET'])
def get_location_by_weather():
    weather = request.args.get('weather')  # Get the 'weather' input from the request
    if not weather:
        return jsonify({"error": "Please provide the weather parameter"}), 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # Enable dictionary output for easier JSON response

    try:
        # SQL query to get the location data based on weather
        query = "SELECT id, name, latitude, longitude, temperature FROM locations WHERE weather = %s"
        cursor.execute(query, (weather,))
        result = cursor.fetchall()  # Fetch all the matching rows

        if not result:
            return jsonify({"message": f"No locations found for weather: {weather}"}), 404
        
        # Return the results as a JSON response
        return jsonify(result), 200
    
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    
    finally:
        # Close the database connection
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
