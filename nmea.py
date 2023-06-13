import telnetlib
import time
import re
import config

class tcp_nmea:
    """
    Connect to Telnet NMEA 0183 source over TCP and extract data
    """
    def __init__(self) -> None:
        self.transducer_types = {
            "A":"Angular displacement",
            "C":"Temperature",
            "D":"Depth",
            "F":"Frequency",
            "H":"Humidity",
            "N":"Force",
            "P":"Pressure",
            "R":"Flow"
        }
        self.transducer_units = {
            "A ":" Amperes",
            "B ":" Bars",
            "C ":" Celsius",
            "D ":" Degrees",
            "H ":" Hertz",
            "I ":" Liters/second",
            "K ":" Kelvin",
            "M ":" Meters",
            "N ":" Newton",
            "P ":" Percentage of full range",
            "R ":" RPM",
            "S ":" Parts per thousand",
            "V ":" Volts"
        }
        self.wind_units = {
            "N":"Knots",
            "K": "km/h",
            "M":"m/s"
        }
        self.st60_wind_units = {
            "N":"km/h",
            "K": "Knots",
            "M":"m/s"
        }

        return None
    
    def connect(self, host: str, port: int) -> None:
        self.tn = telnetlib.Telnet(host, port)
        return None

    def get_transducer_types(self) -> dict:
        """
        Return valid transducer types
        """
        return self.transducer_types
    
    def get_transducer_units(self) -> dict:
        """
        Return valid units
        """
        return self.transducer_units

    def get_nmea_sentence_words(self, id: str) -> list:
        """
        Scan for specific sentence id (e.g. "$GPRMC") and return a comma separated list of sentence words including null values
        """
        sentence_id = id + ","
        sentence_id = sentence_id.encode('ascii')

        self.tn.read_until(sentence_id).decode('ascii')

        sentence = self.tn.read_until(b"\n").decode('ascii')
        
        words = re.split(',|\*', sentence) # Split on comma and * for checksum

        return words

    def get_datetime(self) -> time:
        """
        Extract time from recommended minimum specific GPS/Transit data ($GPRMC) and return in unix timestamp format
        """
        gps_words = self.get_nmea_sentence_words("$GPRMC")
        
        if gps_words:
            gps_date = gps_words[8][:-2] # extract year
            gps_year = int(gps_words[8][-2:]) + 2000 # convert to 4 digit year
            gps_longdate = gps_date + str(gps_year) # insert 4 digit year
            gps_time = gps_words[0]
            gps_date_time = gps_longdate + " " + gps_time

            gps_structtime = time.strptime(gps_date_time[:-3], "%d%m%Y %H%M%S")
            gps_timestamp = time.mktime(gps_structtime)
        
        else:
            gps_timestamp = 0

        return gps_timestamp
    
    def get_lat_long(self) -> dict:
        """
        Extract lat/long from recommended minimum specific GPS/Transit data ($GPRMC) and return as a list
        """
        lat_long = {}
        gps_words = self.get_nmea_sentence_words("$GPRMC")
        
        if gps_words:
            lat_long["lat"] = gps_words[2]
            lat_long["lns"] = gps_words[3]
            lat_long["long"] = gps_words[4]
            lat_long["ew"] = gps_words[5]

        else:
            lat_long["e"] = "No result"
        
        return lat_long
            
    def get_transducer_data(self) -> dict:
        """
        Find transducer sentence and extract all items, return a list of readings
        using transducer types and units where valid (get_transducer_types, get_transducer_units)
        """
        weather_data = self.get_nmea_sentence_words("$YXXDR")
        
        weather_readings = {}
        while len(weather_data) >= 4:
            
            if weather_data[0] in self.transducer_types:
                weather_data[0] = self.transducer_types[weather_data[0]]
            if weather_data[2] in self.transducer_units:
                weather_data[2] = self.transducer_units[weather_data[2]]

            weather_readings[weather_data[0]] = {"value" : weather_data[1], "unit" : weather_data[2], "label" : weather_data[3]}
            weather_data = weather_data[4:]
            weather_readings["timestamp"] = time.time()      

        return weather_readings
    
    def get_wind_data(self) -> dict:
        """
        Extract wind data from NMEA sentence $IIMWV
        """
        wind_data = {}

        wind_words = self.get_nmea_sentence_words("$IIMWV")

        if wind_words:
            wind_data["angle"] = wind_words[0]
            wind_data["reference"] = wind_words[1]
            wind_data["speed"] = wind_words[2]
            if config.st60_fix == False:
                wind_data["units"] = self.wind_units[wind_words[3]]
            else:
                wind_data["units"] = self.st60_wind_units[wind_words[3]]

        return wind_data

    def get_cog_sog_data(self) -> dict:
        pass
