"""
This module was written on python v3.11.3
"""

import config
import json

try:
    import geocoder
except ImportError:
    exit("This class requires the geocoder module\nInstall with: sudo pip install geocoder")

try:
    import requests
except ImportError:
    exit("This class requires the requests module\nInstall with: sudo pip install requests")

class weather_api:
    """
    Class for interacting with the Open_meteo API, this assume you have a free
    account and you will need to pass your credentials to instantiate.
    """
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        
        self.get_auth_token(username, password)

        return

    def get_auth_token(self, username: str, password: str) -> int:
        """Use your Open Meteo login to obtain an API token"""
        response = requests.get('https://login.meteomatics.com/api/v1/token', auth=(username, password))
        response.close()
        if response.status_code == 200:
            self.auth_token = response.json()["access_token"]
            print("Auth token:", self.auth_token)
            return 1
        else:
            print("Error generating auth token, check credentials provided")
            return 0

    def get_weather(self, latlong: list) -> dict:
        """
        Get basic weather information for a specified location as of now
        Provide a lat and long in decimal format array with Latitudet in 0
        postion and Longitude in 1
        e.g. latlong[50.9048, -1.4043] for Southampton UK.
        Returns a dictionary of weather information with human readable key names - Nautical metric units.
        """
        weather = {}
        baseurl = "https://api.meteomatics.com/now/"
        parameters = "msl_pressure:hPa,wind_speed_10m:kn,wind_dir_10m:d,wind_gusts_10m_1h:kn,weather_symbol_1h:idx/"
        url = baseurl + parameters + str(latlong[0]) + "," + str(latlong[1]) +"/json?access_token=" + self.auth_token
        print(url)

        response = requests.get(url)
        response.close()
        print("response data:", response.text)
        print("response code:", response.status_code)

        if response.status_code == 403:
            print("Renewing auth token")
            self.get_auth_token(config.username, config.password)
            response = requests.get(url)
            response.close()

        if response.status_code == 200:
            weather = self.process_weather(json.loads(response.text))
        else:
            print("Failure to get weather data.\nStatus code: {}\nResponse text: {}".format(response.status_code, response.text))

        return weather

    def process_weather(self, response_text_json: json) -> dict:
        """
        Pass JSON encoded response text from the Open Meteo API
        Assumes you have used one location and one time parameter, not a range
        
        This function requires python v2.10+

        Supports the following parameters:
        "msl_pressure:hPa"
        "wind_speed_10m:kn"
        "wind_dir_10m:d"
        "wind_gusts_10m_1h:kn"
        "weather_symbol_1h:idx"
        """
        weather = {}
        data = response_text_json["data"]
        print("JSON data:", data, "\n")
        
        #Weather codes from: https://www.meteomatics.com/en/api/available-parameters/derived-weather-and-convenience-parameters/general-weather-state/#weather_symb
        icon_map = {
            "Indeterminate": [0,100],
            "Clear sky": [1,101],
            "Light clouds": [2,102],
            "Partly cloudy": [3,103],
            "Cloudy": [4,104],
            "Rain": [5,105],
            "Rain and snow / sleet": [6,106],
            "Snow": [7,107],
            "Rain shower": [8,108],
            "Snow shower": [9,109],
            "Sleet shower": [10,110],
            "Light Fog": [11,111],
            "Dense fog": [12,112],
            "Freezing rain": [13,113],
            "Thunderstorms": [14,114],
            "Drizzle": [15,115],
            "Sandstorm": [16,116]
        }
        
        for item in data:
            print("Item:", item, "\n")
            # Assumes only one coordinate set and date per item
            if item["parameter"] == "msl_pressure:hPa":
                weather["pressure"] = item["coordinates"][0]["dates"][0]["value"]
            elif item["parameter"] == "wind_speed_10m:kn":
                weather["wind_speed"] = item["coordinates"][0]["dates"][0]["value"]
            elif item["parameter"] == "wind_dir_10m:d":
                weather["wind_direction"] = item["coordinates"][0]["dates"][0]["value"]
            elif item["parameter"] == "wind_gusts_10m_1h:kn":
                weather["wind_gusts"] = item["coordinates"][0]["dates"][0]["value"]
            elif item["parameter"] == "weather_symbol_1h:idx":
                weather["weather_code"] = item["coordinates"][0]["dates"][0]["value"]

            # Needs python 3.10+
            # match item["parameter"]:
            #     case "msl_pressure:hPa":
            #         weather["pressure"] = item["coordinates"][0]["dates"][0]["value"]
            #     case "wind_speed_10m:kn":
            #         weather["wind_speed"] = item["coordinates"][0]["dates"][0]["value"]
            #     case "wind_dir_10m:d":
            #         weather["wind_direction"] = item["coordinates"][0]["dates"][0]["value"]
            #     case "wind_gusts_10m_1h:kn":
            #         weather["wind_gusts"] = item["coordinates"][0]["dates"][0]["value"]
            #     case "weather_symbol_1h:idx":
            #         weather["weather_code"] = item["coordinates"][0]["dates"][0]["value"]
            
        for icon in icon_map:
            if weather["weather_code"] in icon_map[icon]:
                weather["weather_icon"] = icon
                break
        
        for parameter in weather:
            print(parameter, ":", weather[parameter])
        
        return weather
    
    def get_latlong(self, city: str, countrycode: str) -> list:
        """
        Pass a city and country code to get a lat long for weather lookups
        """
        location_string = "{}, {}".format(city, countrycode)
        g = geocoder.arcgis(location_string)
        latlong = g.latlng
        print("Lat/long:",latlong[0], latlong[1])
        return latlong