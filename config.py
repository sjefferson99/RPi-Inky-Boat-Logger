# Eink setup
inky = "phat"
inky_colour = "red"

# Manual Lat long setup - not used if GPS data present - Set to False if not wanted as fallback
city = "southampton"
countrycode = "GB"

# Data management
offset_hours = 3 # How many hours to compare to
data_retention = 24 # Hours to store data for use in comparison

#NMEA config - Set to False if not present
gps_nmea_host = "192.168.4.90"
gps_nmea_port = 2000
weather_nmea_host = "192.168.68.201"
weather_nmea_port = 2000
wind_nmea_host = "192.168.4.90"
wind_nmea_port = 2000