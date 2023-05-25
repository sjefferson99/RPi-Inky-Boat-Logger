import telnetlib
import time

class tcp_nmea:
    """
    Connect to Telnet NMEA 0183 source over TCP and extract data
    """
    def __init__(self, host: str, port: int) -> None:
        self.tn = telnetlib.Telnet(host, port)

    def get_nmea_sentence_words(self, id: str) -> list:
        """
        Scan for specific sentence id (e.g. "$GPRMC") and return comma separated list of sentence words including null values
        Note this is a lazy implementation and may return parts of the next sentence as further list items
        """
        sentence_id = id + ","
        sentence_id = sentence_id.encode('ascii')

        self.tn.read_until(sentence_id)

        sentence = ""
        while "\n" not in sentence:
            sentence += self.tn.read_some().decode('ascii')

        words = sentence.split(",")

        return words

    def get_nmea_datetime(self) -> time:
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