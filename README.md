# Weather API

## Important Note
This Weather API project is designed to run **only in local environments**. When executed on a remote server, it will attempt to fetch the server's location, which may lead to inaccurate or unintended results. To ensure accurate location fetching and functionality, please run this application on your local machine.

## Description
The Weather API project is a Python-based application that fetches weather information for current and preferred locations. It allows users to retrieve locations based on specific climate conditions and obtain weather data based on latitude and longitude. This project integrates API calls to gather weather data and uses a database to save and manage location information.

## How to Run the App
### **Using Git Clone**
1. **Clone the GitHub Repository:**
   Set up your workspace and clone the repository using the command:
   ```bash
   git clone --branch retrieval https://github.com/AksharaDondeti/weather_api.git

2. **Install the Necessary Python Packages**
     Navigate to the project directory and install the required packages using:
     ```bash
     pip install -r requirements.txt

3. **Run the Application**
    Use the following command to start the application:
    ```bash
    python src/together.py

### **Using Docker**
1. **Build the Docker Image**
    In the project directory (where the Dockerfile is located), run:
    ``` bash
    docker build -t weather-api-app .
2. **Run the Docker Container**
   After building the image, execute the following command to run the container:
   ```bash
   docker run -p 4000:4000 weather-api-app
 3.**Access the Application**
     Open your web browser and go to http://127.0.0.1:4000 to access the application running in Docker.
