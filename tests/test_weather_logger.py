from weather_logger import weather_logger
import config
from open_meteo import weather_api
import time

def test_weather_logger_online_weather_false(mocker):
    """
    Tests online weather value when disabled
    """
    config.gps_nmea_host = None
    config.gps_nmea_port = None
    config.wind_nmea_host = None
    config.wind_nmea_port = None
    config.sensors_nmea_host = None
    config.sensors_nmea_port = None
    config.use_online_weather = False
    output = "Dummy telnet connection"
    mocker.patch("nmea.tcp_nmea.connect", return_value=output)
    wl = weather_logger()
    assert wl.online_weather == None

def test_weather_logger_online_weather_true():
    """
    Tests online weather value when enabled
    """
    config.gps_nmea_host = None
    config.gps_nmea_port = None
    config.wind_nmea_host = None
    config.wind_nmea_port = None
    config.sensors_nmea_host = None
    config.sensors_nmea_port = None
    config.use_online_weather = True
    wl = weather_logger()
    weather = weather_api()
    assert type(wl.online_weather) == type(weather)

def test_weather_logger_lat_long_online_weather_false():
    """
    Tests default lat long when no online weather
    """
    config.gps_nmea_host = None
    config.gps_nmea_port = None
    config.wind_nmea_host = None
    config.wind_nmea_port = None
    config.sensors_nmea_host = None
    config.sensors_nmea_port = None
    config.use_online_weather = False
    wl = weather_logger()
    wl.set_default_lat_long()
    assert wl.default_lat_long == []

def test_weather_logger_lat_long_no_location():
    """
    Tests default lat long when no location given
    """
    config.gps_nmea_host = None
    config.gps_nmea_port = None
    config.wind_nmea_host = None
    config.wind_nmea_port = None
    config.sensors_nmea_host = None
    config.sensors_nmea_port = None
    config.use_online_weather = True
    config.city = False
    config.countrycode = False
    wl = weather_logger()
    wl.set_default_lat_long()
    assert wl.default_lat_long == []

def test_weather_logger_lat_long_valid_location():
    """
    Tests default lat long when valid location given
    """
    config.gps_nmea_host = None
    config.gps_nmea_port = None
    config.wind_nmea_host = None
    config.wind_nmea_port = None
    config.sensors_nmea_host = None
    config.sensors_nmea_port = None
    config.use_online_weather = True
    config.city = "southampton"
    config.countrycode = "GB"
    wl = weather_logger()
    wl.set_default_lat_long()
    assert wl.default_lat_long == [50.9049, -1.4043]

# I can't work out how to patch this function, so moving on for now.
#def test_nmea_connection(mocker):
    """
    Test that appropriate nmea connections are set up (test same, different and not specified)
    Instead of mocking up whole telnet response, use sideeffect to return the host and ports that would have been used
    """
    # https://stackoverflow.com/questions/16162015/mocking-python-function-based-on-input-arguments
    # https://stackoverflow.com/questions/7665682/python-mock-object-with-method-called-multiple-times/7665754#7665754
    
    # config.gps_nmea_host = "192.168.1.1"
    # config.gps_nmea_port = 2000
    # config.wind_nmea_host = "192.168.1.2"
    # config.wind_nmea_port = 2001
    # config.sensors_nmea_host = "192.168.1.3"
    # config.sensors_nmea_port = 2002

    #wl = weather_logger()

    #mocker.patch("weather_logger.weather_logger.gps_nmea.connect", return_value={"host": "192.168.1.1", "port": 2000})

    #assert wl.gps_nmea == {"host": "192.168.1.1", "port": 2000}
    #assert wl.wind_nmea == {"host": "192.168.1.2", "port": 2001}
    #assert wl.sensors_nmea == {"host": "192.168.1.3", "port": 2002}

def test_cardinal_to_signed_lat_long():
    """
    Tests returning a signed lat long from a cardinal version
    """
    config.gps_nmea_host = None
    config.gps_nmea_port = None
    config.wind_nmea_host = None
    config.wind_nmea_port = None
    config.sensors_nmea_host = None
    config.sensors_nmea_port = None
    config.use_online_weather = True
    wl = weather_logger()

    cardinal_lat_long1 = {"lat": 56.345, "ns": "n", "long": 1.045, "ew": "w"}
    converted1 = wl.cardinal_to_signed_lat_long(cardinal_lat_long1)
    lat_long1 = [56.345, -1.045]
    assert converted1 == lat_long1
    cardinal_lat_long2 = {"lat": 56.345, "ns": "s", "long": 1.045, "ew": "w"}
    converted2 = wl.cardinal_to_signed_lat_long(cardinal_lat_long2)
    lat_long2 = [-56.345, -1.045]
    assert converted2 == lat_long2
    cardinal_lat_long3 = {"lat": 56.345, "ns": "n", "long": 1.045, "ew": "e"}
    converted3 = wl.cardinal_to_signed_lat_long(cardinal_lat_long3)
    lat_long3 = [56.345, 1.045]
    assert converted3 == lat_long3

# Need to mock the whole nmea thing as object doesn't exist if skip connection
# def test_get_reading_time(mocker):
#     """
#     Get system time when GPS time similar
#     """
#     config.gps_nmea_host = None
#     config.gps_nmea_port = None
#     config.wind_nmea_host = None
#     config.wind_nmea_port = None
#     config.sensors_nmea_host = None
#     config.sensors_nmea_port = None
#     config.use_online_weather = True
#     wl = weather_logger()

#     mocker.patch("weather_logger.weather_logger.gps_nmea.get_datetime", return_value = time.time() + 110)
#     now = time.time()
#     reading_time = wl.get_reading_time()
#     assert now == reading_time