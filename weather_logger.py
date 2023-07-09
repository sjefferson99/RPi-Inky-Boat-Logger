from nmea import tcp_nmea
from open_meteo import weather_api
import config
from time import time
from constants import *
import math

class weather_logger:
    """
    Weather logging via internet or NMEA local instruments
    """
    def __init__(self) -> None:
        if config.use_online_weather:
            self.online_weather = weather_api()
        else:
            self.online_weather = None
        self.offset_hours = config.offset_hours
        self.data_retention = config.data_retention
        self.set_default_lat_long()
        self.init_nmea_connections()
        return None
    
    def set_default_lat_long(self) -> None:
        self.default_lat_long = []
        if self.online_weather and config.city != False and config.countrycode != False:
            self.default_lat_long = self.online_weather.get_latlong(config.city, config.countrycode)

        return None

    def init_nmea_connections(self) -> None:
        """
        If both arguments are not false, configure, if any match an existing config, redirect to prevent connecting twice
        """
        self.gps_nmea = None
        self.sensors_nmea = None
        self.wind_nmea = None

        # GPS NMEA
        if config.gps_nmea_host and config.gps_nmea_port:
            self.gps_nmea = tcp_nmea()
            self.gps_nmea.connect(config.gps_nmea_host, config.gps_nmea_port)
        # Weather NMEA
        if config.sensors_nmea_host and config.sensors_nmea_port:
            if config.sensors_nmea_host == config.gps_nmea_host and config.sensors_nmea_port == config.gps_nmea_port:
                self.sensors_nmea = self.gps_nmea
            else:            
                self.sensors_nmea = tcp_nmea()
                self.sensors_nmea.connect(config.sensors_nmea_host, config.sensors_nmea_port)
        # Wind NMEA
        if config.wind_nmea_host and config.wind_nmea_port:
            if config.wind_nmea_host == config.gps_nmea_host and config.wind_nmea_port == config.gps_nmea_port:
                self.wind_nmea = self.gps_nmea
            elif config.wind_nmea_host == config.sensors_nmea_host and config.wind_nmea_port == config.sensors_nmea_port:
                self.wind_nmea = self.sensors_nmea
            else:
                self.wind_nmea = tcp_nmea()
                self.wind_nmea.connect(config.wind_nmea_host, config.wind_nmea_port)
        
        return None
    
    def ground_wind_from_apparent(self) -> list:
        pass

    # https://www.omnicalculator.com/physics/dew-point#how-to-calculate-dew-point-how-to-calculate-relative-humidity
    def get_dew_point(self, temperature_in_c: float, relative_humidity: int) -> float:
        alphatrh = (math.log((relative_humidity / 100))) + ((17.625 * temperature_in_c) / (243.04 + temperature_in_c))
        dewpoint_in_c = (243.04 * alphatrh) / (17.625 - alphatrh)
        return dewpoint_in_c

    # https://www.calctool.org/atmospheric-thermodynamics/absolute-humidity#what-is-and-how-to-calculate-absolute-humidity
    def relative_to_absolute_humidity(self, relative_humidity, temperature_in_c):
        temperature_in_k = self.celcius_to_kelvin(temperature_in_c)
        actual_vapor_pressure = self.get_actual_vapor_pressure(relative_humidity, temperature_in_k)

        return actual_vapor_pressure / (WATER_VAPOR_SPECIFIC_GAS_CONSTANT * temperature_in_k)

    def absolute_to_relative_humidity(self, absolute_humidity, temperature_in_c):
        temperature_in_k = self.celcius_to_kelvin(temperature_in_c)
        saturation_vapor_pressure = self.get_saturation_vapor_pressure(temperature_in_k)

        return (WATER_VAPOR_SPECIFIC_GAS_CONSTANT * temperature_in_k * absolute_humidity) / saturation_vapor_pressure * 100

    def celcius_to_kelvin(self, temperature_in_c):
        return temperature_in_c + 273.15

    # https://www.calctool.org/atmospheric-thermodynamics/absolute-humidity#actual-vapor-pressure
    # http://cires1.colorado.edu/~voemel/vp.html
    def get_actual_vapor_pressure(self, relative_humidity, temperature_in_k):
        return self.get_saturation_vapor_pressure(temperature_in_k) * (relative_humidity / 100)

    def get_saturation_vapor_pressure(self, temperature_in_k):
        v = 1 - (temperature_in_k / CRITICAL_WATER_TEMPERATURE)

        # empirical constants
        a1 = -7.85951783
        a2 = 1.84408259
        a3 = -11.7866497
        a4 = 22.6807411
        a5 = -15.9618719
        a6 = 1.80122502

        return CRITICAL_WATER_PRESSURE * math.exp(
            CRITICAL_WATER_TEMPERATURE /
            temperature_in_k *
            (a1*v + a2*v**1.5 + a3*v**3 + a4*v**3.5 + a5*v**4 + a6*v**7.5)
        )

    def cardinal_to_signed_lat_long(self, cardinal_lat_long: dict) -> list:
        """
        Convert dictionary of lat long with N/S E/W designation to list of lat long signed floats
        Example:
        input: {"lat": 56.345, "ns": "n", "long": 1.045, "ew": "w"}
        output: [56.345, -1.045]
        """
        lat_long = []
        if cardinal_lat_long["ns"] == "s":
            lat_long.append(cardinal_lat_long["lat"] * -1)
        else:
            lat_long.append(cardinal_lat_long["lat"])
        if cardinal_lat_long["ew"] == "w":
            lat_long.append(cardinal_lat_long["long"] * -1)
        else:
            lat_long.append(cardinal_lat_long["long"])
        
        return lat_long

    def get_reading_time(self) -> time:
        """
        Returns system time or returns GPS time if present and more than 120 seconds different
        """
        system_time = time()
        reading_time = system_time
        gps_time = self.gps_nmea.get_datetime()
        if gps_time:
            if abs(gps_time - system_time) > 120:
                print("System time differs from GPS time by more than 2 minutes, using GPS time")
                reading_time = gps_time   
        return reading_time
    
    def get_lat_long(self) -> list:
        """
        Determine most accurate lat/long for reading
        """
        gps_lat_long = self.gps_nmea.get_lat_long()
        if "e" in gps_lat_long:
            lat_long = self.default_lat_long
        else:
            lat_long = self.cardinal_to_signed_lat_long(gps_lat_long)
        return lat_long
    
    def get_weather_readings(self, lat_long: list = []) -> dict:
        """
        Get weather transducer readings if present, pass a lat/long for online lookup if enabled
        """
        weather_readings = {}
        missing_data = False
        
        local_sensors = self.sensors_nmea.get_transducer_data()
        try:
            weather_readings["temperature"] = local_sensors["Temperature"]
        except:
            weather_readings["temperature"] = None
            missing_data = True
        try:
            weather_readings["pressure"] = local_sensors["Pressure"]
        except:
            weather_readings["pressure"] = None
            missing_data = True
        try:
            weather_readings["humidity"] = local_sensors["Humidity"]
        except:
            weather_readings["humidity"] = None
            missing_data = True
        
        local_wind = self.wind_nmea.get_wind_data()
        if local_wind["reference"] == "R":
            try:
                local_wind["direction"] = local_sensors["wind_direction"]
            except:
                weather_readings["wind_direction"] = None
                missing_data = True
            try:
                local_wind["speed"] = local_sensors["wind_speed"]
            except:
                weather_readings["wind_speed"] = None
                missing_data = True
        else:
            weather_readings["wind_direction"] = None
            weather_readings["wind_speed"] = None
            missing_data = True

        if self.online_weather and lat_long and missing_data == True:
            try:
                net_weather = self.online_weather.get_weather(lat_long, self.offset_hours)
                for reading in weather_readings:
                    if reading == None:
                        #get reading from net_weather
                        print("Not actually looking up weather online right now - code arrives on Tuesday")
                        pass
            except:
                print ("Online weather not enabled and available")
        return weather_readings
    
    def get_weather_data (self) -> dict:
        """
        Collect and log a set of weather data with timestamp
        """
        weather_data = {}
        weather_data["reading_time"] = self.get_reading_time()
        weather_data["lat_long"] = self.get_lat_long()
        weather_data["weather_readings"] = self.get_weather_readings(weather_data["lat_long"])

        return weather_data