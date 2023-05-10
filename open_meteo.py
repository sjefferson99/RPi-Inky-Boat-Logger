"""
This module was written on python v3.11.3
"""

import json
import time

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
    Class for interacting with the Open_Meteo API
    """
    def __init__(self, username: str, password: str) -> None:
        return

    def get_weather(self, latlong: list, offset_hours: int) -> dict:
        """
        Get basic weather information for a specified location as of now
        Provide a lat and long in decimal format array with Latitudet in 0
        postion and Longitude in 1
        e.g. latlong[50.9048, -1.4043] for Southampton UK.
        Returns a dictionary of weather information with human readable key names - Nautical metric units.
        """
        weather = {}
        baseurl = "https://api.open-meteo.com/v1/forecast?latitude={}}&longitude={}".format(latlong[0], latlong[1])
        parameters = "&hourly=temperature_2m,dewpoint_2m,weathercode,pressure_msl,windspeed_10m,winddirection_10m,windgusts_10m&current_weather=true&past_days=1&forecast_days=1&windspeed_unit=kn&timezone=GB&timeformat=unixtime"
        url = baseurl + parameters
        print(url)

        response = requests.get(url)
        response.close()
        print("response data:", response.text)
        print("response code:", response.status_code)

        if response.status_code == 200:
            weather = self.process_weather(json.loads(response.text), offset_hours)
        else:
            print("Failure to get weather data.\nStatus code: {}\nResponse text: {}".format(response.status_code, response.text))

        return weather

    def process_weather(self, response_text_json: json, offset_hours: int) -> dict:
        """
        Pass JSON encoded response text from the Open Meteo API

        Supports the following parameters:
        
        """
        weather = {}
        data = response_text_json["hourly"]
        print("JSON data:", data, "\n")
        hour = time.localtime()["tm_hour"]
        current_hour = hour + 24
        offset_hour = current_hour - offset_hours
        
        #Weather codes from: https://www.meteomatics.com/en/api/available-parameters/derived-weather-and-convenience-parameters/general-weather-state/#weather_symb
        icon_map = {
            "snow": [71, 73, 75, 77, 85, 86],
            "rain": [51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82],
            "cloud": [1, 2, 3, 45, 48],
            "sun": [0],
            "storm": [95, 96, 99],
            "wind": []
        }
        
        weather["temperature"] = data["temperature_2m"][current_hour]
        weather["offset_temperature"] = data["temperature_2m"][offset_hour]
        weather["weather_code"] = data["weathercode"][current_hour]
        weather["offset_weather_code"] = data["weathercode"][offset_hour]

        for icon in icon_map:
            if weather["weather_code"] in icon_map[icon]:
                weather["weather_icon"] = icon
                break
        
        for icon in icon_map:
            if weather["offset_weather_code"] in icon_map[icon]:
                weather["offset_weather_icon"] = icon
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