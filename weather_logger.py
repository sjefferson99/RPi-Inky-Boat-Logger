from nmea import tcp_nmea
from open_meteo import weather_api
import config
from time import time

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
        if self.online_weather:
            self.online_weather = weather_api()
            if config.city != False and config.countrycode != False:
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
            self.gps_nmea = tcp_nmea(config.gps_nmea_host, config.gps_nmea_port)
        # Weather NMEA
        if config.sensors_nmea_host and config.sensors_nmea_port:
            if config.sensors_nmea_host == config.gps_nmea_host and config.sensors_nmea_port == config.gps_nmea_port:
                self.sensors_nmea = self.gps_nmea
            else:            
                self.sensors_nmea = tcp_nmea(config.sensors_nmea_host, config.sensors_nmea_port)
        # Wind NMEA
        if config.wind_nmea_host and config.wind_nmea_port:
            if config.wind_nmea_host == config.gps_nmea_host and config.wind_nmea_port == config.gps_nmea_port:
                self.wind_nmea = self.gps_nmea
            elif config.wind_nmea_host == config.sensors_nmea_host and config.wind_nmea_port == config.sensors_nmea_port:
                self.wind_nmea = self.sensors_nmea
            else:
                self.wind_nmea = tcp_nmea(config.wind_nmea_host, config.wind_nmea_port)
        
        return None
    
    def cardinal_to_signed_lat_long(self, cardinal_lat_long: dict) -> list:
        """
        Convert dictionary of lat long with N/S E/W designation to list of lat long signed floats
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
        Determine most accurate available time for reading
        """
        system_time = time.time()
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
            lat_long = self.convert_to_signed_lat_long(gps_lat_long)
        return lat_long
    
    def get_weather_readings(self, lat_long: list = []) -> dict:
        """
        Get weather transducer readings if present, pass a lat/long for online lookup if enabled
        """
        weather_readings = {}
        
        local_sensors = self.sensors_nmea.get_transducer_data()
        try:
            weather_readings["temperature"] = local_sensors["Temperature"]
        except:
            weather_readings["temperature"] = None
        try:
            weather_readings["pressure"] = local_sensors["Pressure"]
        except:
            weather_readings["pressure"] = None
        try:
            weather_readings["humidity"] = local_sensors["Humidity"]
        except:
            weather_readings["humidity"] = None
        local_wind = self.wind_nmea.get_wind_data()
        if self.online_weather and lat_long:
            try:
                net_weather = self.online_weather.get_weather(lat_long, self.offset_hours)
                for reading in weather_readings:
                    if reading == None:
                        #get reading from net_weather
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