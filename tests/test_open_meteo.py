from open_meteo import weather_api
import requests
import responses
import time
import json

def test_get_lat_long():
    """
    Test correct format lat long is generated from a city and country code
    """
    weather = weather_api()
    lat_long = weather.get_latlong("southampton", "GB")
    assert lat_long == [50.9049, -1.4043]

def test_get_lat_long_city_case():
    """
    Test correct format lat long is generated from a city and country code with capitalised city
    """
    weather = weather_api()
    lat_long = weather.get_latlong("Southampton", "GB")
    assert lat_long == [50.9049, -1.4043]

def test_get_lat_long_country_case():
    """
    Test correct format lat long is generated from a city and country code with lowercase country code
    """
    weather = weather_api()
    lat_long = weather.get_latlong("southampton", "gb")
    assert lat_long == [50.9049, -1.4043]

def test_get_lat_long_precision():
    """
    Test correct format lat long is generated from a city and country code with lower precision
    """
    weather = weather_api()
    lat_long = weather.get_latlong("southampton", "GB", 3)
    assert lat_long == [50.905, -1.404]

@responses.activate
def test_get_weather(mocker):
    """
    Confirm correct processing of API data for given known JSON for a lat/long and date
    """
    responses.add(responses.GET, 'https://api.open-meteo.com/v1/forecast?latitude=50.904&longitude=-1.404&hourly=temperature_2m,dewpoint_2m,weathercode,pressure_msl,windspeed_10m,winddirection_10m,windgusts_10m&current_weather=true&past_days=1&forecast_days=1&windspeed_unit=kn&timezone=GB&timeformat=unixtime',
                  json={"latitude":50.9,"longitude":-1.4000001,"generationtime_ms":0.7939338684082031,"utc_offset_seconds":3600,"timezone":"GB","timezone_abbreviation":"BST","elevation":22.0,"current_weather":{"temperature":23.3,"windspeed":4.9,"winddirection":182.0,"weathercode":0,"is_day":1,"time":1687629600},"hourly_units":{"time":"unixtime","temperature_2m":"°C","dewpoint_2m":"°C","weathercode":"wmo code","pressure_msl":"hPa","windspeed_10m":"kn","winddirection_10m":"°","windgusts_10m":"kn"},"hourly":{"time":[1687474800,1687478400,1687482000,1687485600,1687489200,1687492800,1687496400,1687500000,1687503600,1687507200,1687510800,1687514400,1687518000,1687521600,1687525200,1687528800,1687532400,1687536000,1687539600,1687543200,1687546800,1687550400,1687554000,1687557600,1687561200,1687564800,1687568400,1687572000,1687575600,1687579200,1687582800,1687586400,1687590000,1687593600,1687597200,1687600800,1687604400,1687608000,1687611600,1687615200,1687618800,1687622400,1687626000,1687629600,1687633200,1687636800,1687640400,1687644000],"temperature_2m":[17.7,17.0,16.4,15.9,15.5,15.0,15.0,15.6,16.9,18.7,20.5,21.4,22.4,23.1,23.3,23.1,22.7,22.2,21.9,21.6,20.5,19.3,18.0,17.2,16.6,16.2,16.0,16.0,15.9,15.9,16.3,17.4,18.8,19.9,21.3,21.7,22.8,23.4,24.4,24.8,24.5,24.4,24.0,23.3,22.7,21.1,19.7,18.9],"dewpoint_2m":[12.6,13.5,13.7,13.7,13.7,13.5,13.3,13.5,13.4,13.6,14.2,13.8,14.3,14.1,13.7,13.8,14.0,14.3,14.3,15.2,15.3,15.7,15.8,15.7,15.5,15.2,15.4,15.4,15.3,15.3,15.5,15.5,15.3,15.3,16.0,16.2,15.9,16.0,15.6,14.8,14.8,13.9,13.3,12.0,12.6,13.7,14.3,14.3],"weathercode":[0,0,0,0,2,3,3,3,2,2,2,3,2,2,3,3,3,3,1,3,1,0,0,0,0,1,2,2,2,2,3,3,3,3,3,3,3,2,1,0,0,0,0,0,0,0,0,0],"pressure_msl":[1022.5,1022.5,1022.4,1022.5,1022.6,1023.5,1023.7,1024.1,1024.1,1024.4,1024.7,1024.6,1024.7,1024.4,1024.8,1024.5,1025.5,1025.0,1024.7,1025.4,1024.8,1025.1,1025.3,1025.1,1025.5,1025.2,1024.8,1024.7,1024.4,1024.4,1024.7,1024.4,1025.3,1024.9,1024.4,1024.4,1024.0,1023.6,1022.9,1022.7,1022.1,1021.5,1021.0,1020.6,1020.3,1020.3,1020.1,1019.4],"windspeed_10m":[4.1,3.4,4.1,3.7,2.3,2.6,3.1,3.9,3.9,4.3,5.2,5.8,7.1,8.2,8.9,9.6,9.9,9.6,8.9,8.1,7.3,5.5,3.9,3.2,3.3,3.5,3.4,2.7,2.9,2.6,2.9,5.5,5.4,5.4,5.1,4.5,5.3,6.6,6.2,6.7,6.2,5.8,5.7,4.9,3.8,5.0,4.3,4.4],"winddirection_10m":[295,286,287,288,275,261,266,279,273,260,243,240,235,218,218,218,222,227,226,224,230,225,213,218,220,218,223,225,228,228,233,243,235,226,217,211,216,201,200,202,204,201,198,182,165,138,133,122],"windgusts_10m":[10.7,7.8,8.0,8.0,7.2,4.9,6.2,6.2,8.6,9.9,12.4,12.8,15.4,17.1,18.7,20.0,20.4,21.0,19.8,18.3,16.7,14.8,10.9,7.8,6.4,6.8,7.4,6.8,5.6,5.6,5.8,12.1,11.5,11.5,11.3,11.1,11.7,13.6,14.4,14.8,15.6,14.0,13.0,12.2,10.7,9.9,9.7,8.6]}}, status = 200)
    output = time.localtime(1687633200)
    mocker.patch("time.localtime", return_value=output)
    weather = weather_api()
    weather_data = weather.get_weather([50.904, -1.404], 3)
    expected_weather_data ={
    'dewpoint': 12.6,
   'offset_dewpoint': 13.9,
   'offset_pressure': 1021.5,
   'offset_temperature': 24.4,
   'offset_weather_code': 0,
   'offset_weather_icon': 'sun',
   'offset_wind_direction': 201,
   'offset_wind_gusts': 14.0,
   'offset_wind_speed': 5.8,
   'pressure': 1020.3,
   'temperature': 22.7,
   'weather_code': 0,
   'weather_icon': 'sun',
   'wind_direction': 165,
   'wind_gusts': 10.7,
   'wind_speed': 3.8} 
    assert weather_data == expected_weather_data

def test_process_weather_data():
    """
    Test processing of given JSON returns correct values
    """
    weather = weather_api()
    json_data = json.loads('{"latitude":50.9,"longitude":-1.4000001,"generationtime_ms":0.7939338684082031,"utc_offset_seconds":3600,"timezone":"GB","timezone_abbreviation":"BST","elevation":22.0,"current_weather":{"temperature":23.3,"windspeed":4.9,"winddirection":182.0,"weathercode":0,"is_day":1,"time":1687629600},"hourly_units":{"time":"unixtime","temperature_2m":"°C","dewpoint_2m":"°C","weathercode":"wmo code","pressure_msl":"hPa","windspeed_10m":"kn","winddirection_10m":"°","windgusts_10m":"kn"},"hourly":{"time":[1687474800,1687478400,1687482000,1687485600,1687489200,1687492800,1687496400,1687500000,1687503600,1687507200,1687510800,1687514400,1687518000,1687521600,1687525200,1687528800,1687532400,1687536000,1687539600,1687543200,1687546800,1687550400,1687554000,1687557600,1687561200,1687564800,1687568400,1687572000,1687575600,1687579200,1687582800,1687586400,1687590000,1687593600,1687597200,1687600800,1687604400,1687608000,1687611600,1687615200,1687618800,1687622400,1687626000,1687629600,1687633200,1687636800,1687640400,1687644000],"temperature_2m":[17.7,17.0,16.4,15.9,15.5,15.0,15.0,15.6,16.9,18.7,20.5,21.4,22.4,23.1,23.3,23.1,22.7,22.2,21.9,21.6,20.5,19.3,18.0,17.2,16.6,16.2,16.0,16.0,15.9,15.9,16.3,17.4,18.8,19.9,21.3,21.7,22.8,23.4,24.4,24.8,24.5,24.4,24.0,23.3,22.7,21.1,19.7,18.9],"dewpoint_2m":[12.6,13.5,13.7,13.7,13.7,13.5,13.3,13.5,13.4,13.6,14.2,13.8,14.3,14.1,13.7,13.8,14.0,14.3,14.3,15.2,15.3,15.7,15.8,15.7,15.5,15.2,15.4,15.4,15.3,15.3,15.5,15.5,15.3,15.3,16.0,16.2,15.9,16.0,15.6,14.8,14.8,13.9,13.3,12.0,12.6,13.7,14.3,14.3],"weathercode":[0,0,0,0,2,3,3,3,2,2,2,3,2,2,3,3,3,3,1,3,1,0,0,0,0,1,2,2,2,2,3,3,3,3,3,3,3,2,1,0,0,0,0,0,0,0,0,0],"pressure_msl":[1022.5,1022.5,1022.4,1022.5,1022.6,1023.5,1023.7,1024.1,1024.1,1024.4,1024.7,1024.6,1024.7,1024.4,1024.8,1024.5,1025.5,1025.0,1024.7,1025.4,1024.8,1025.1,1025.3,1025.1,1025.5,1025.2,1024.8,1024.7,1024.4,1024.4,1024.7,1024.4,1025.3,1024.9,1024.4,1024.4,1024.0,1023.6,1022.9,1022.7,1022.1,1021.5,1021.0,1020.6,1020.3,1020.3,1020.1,1019.4],"windspeed_10m":[4.1,3.4,4.1,3.7,2.3,2.6,3.1,3.9,3.9,4.3,5.2,5.8,7.1,8.2,8.9,9.6,9.9,9.6,8.9,8.1,7.3,5.5,3.9,3.2,3.3,3.5,3.4,2.7,2.9,2.6,2.9,5.5,5.4,5.4,5.1,4.5,5.3,6.6,6.2,6.7,6.2,5.8,5.7,4.9,3.8,5.0,4.3,4.4],"winddirection_10m":[295,286,287,288,275,261,266,279,273,260,243,240,235,218,218,218,222,227,226,224,230,225,213,218,220,218,223,225,228,228,233,243,235,226,217,211,216,201,200,202,204,201,198,182,165,138,133,122],"windgusts_10m":[10.7,7.8,8.0,8.0,7.2,4.9,6.2,6.2,8.6,9.9,12.4,12.8,15.4,17.1,18.7,20.0,20.4,21.0,19.8,18.3,16.7,14.8,10.9,7.8,6.4,6.8,7.4,6.8,5.6,5.6,5.8,12.1,11.5,11.5,11.3,11.1,11.7,13.6,14.4,14.8,15.6,14.0,13.0,12.2,10.7,9.9,9.7,8.6]}}')
    weather_data = weather.process_weather(json_data, 3)
    expected_weather_data ={
    'dewpoint': 12.6,
   'offset_dewpoint': 13.9,
   'offset_pressure': 1021.5,
   'offset_temperature': 24.4,
   'offset_weather_code': 0,
   'offset_weather_icon': 'sun',
   'offset_wind_direction': 201,
   'offset_wind_gusts': 14.0,
   'offset_wind_speed': 5.8,
   'pressure': 1020.3,
   'temperature': 22.7,
   'weather_code': 0,
   'weather_icon': 'sun',
   'wind_direction': 165,
   'wind_gusts': 10.7,
   'wind_speed': 3.8} 
    assert weather_data == expected_weather_data