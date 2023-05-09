import config
from open_meteo import weather_api

weather = weather_api(config.username, config.password)

latlong = weather.get_latlong(config.city, config.countrycode)

weatherdata = weather.get_weather(latlong)

for parameter in weatherdata:
    print(parameter, weatherdata[parameter])