import telnetlib
import time
import re

class tcp_nmea:
    """
    Connect to Telnet NMEA 0183 source over TCP and extract data
    """
    def __init__(self, host: str, port: int) -> None:
        self.tn = telnetlib.Telnet(host, port)
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
        self.units = {
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

    def get_nmea_sentence_words(self, id: str) -> list:
        """
        Scan for specific sentence id (e.g. "$GPRMC") and return comma separated list of sentence words including null values
        """
        sentence_id = id + ","
        sentence_id = sentence_id.encode('ascii')

        self.tn.read_until(sentence_id)

        sentence = ""
        while "\n" not in sentence:
            sentence += self.tn.read_some().decode('ascii')
        
        words = re.split(',|\*', sentence) # Split on comma and * for checksum
        
        # Trim off any extra data captured from next sentence
        i = 0
        for word in words:
            if "$" in word:
                break
            i += 1
            
        words = words[:i]        

        return words

    def get_datetime(self) -> time:
        """
        Extract time from recommended minimum specific GPS/Transit data ($GPRMC) and return in unix timestamp format
        """
        gps_words = self.get_nmea_sentence_words("$GPRMC")
        
        gps_date = gps_words[8][:-2] # extract year
        gps_year = int(gps_words[8][-2:]) + 2000 # convert to 4 digit year
        gps_longdate = gps_date + str(gps_year) # insert 4 digit year
        gps_time = gps_words[0]
        gps_date_time = gps_longdate + " " + gps_time

        gps_structtime = time.strptime(gps_date_time[:-3], "%d%m%Y %H%M%S")
        gps_timestamp = time.mktime(gps_structtime)

        return gps_timestamp
    
    def get_transducer_data(self) -> dict:
        """
        Find transducer sentence and extract all items, return a list of readings
        using transducer types and units where valid (get_transducer_types, get_units)
        """
        weather_data = self.get_nmea_sentence_words("$YXXDR")
        
        weather_readings = {}
        while len(weather_data) >= 4:
            
            if weather_data[0] in self.transducer_types:
                weather_data[0] = self.transducer_types[weather_data[0]]
            if weather_data[2] in self.units:
                weather_data[2] = self.units[weather_data[2]]

            weather_readings[weather_data[0]] = {"value" : weather_data[1], "unit" : weather_data[2], "label" : weather_data[3], "timestamp" : time.time()}
            weather_data = weather_data[4:]

        return weather_readings
    
    def get_transducer_types(self) -> dict:
        """
        Return valid transducer types
        """
        return self.transducer_types
    
    def get_units(self) -> dict:
        """
        Return valid units
        """
        return self.units