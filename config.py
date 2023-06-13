# Eink setup
inky = "phat"
inky_colour = "red"

# Set to true to fallback to online weather where local data is not available
use_online_weather = True

# Manual Lat long setup - not used if GPS data present - Set to False if not
# wanted as fallback
city = "southampton"
countrycode = "GB"

# Data management
offset_hours = 3 # How many hours to compare to
data_retention = 24 # Hours to store data for use in comparison

#NMEA config - Set to False if not present
gps_nmea_host = "192.168.4.90"
gps_nmea_port = 2000
sensors_nmea_host = "192.168.68.201"
sensors_nmea_port = 2000
wind_nmea_host = "192.168.4.90"
wind_nmea_port = 2000

# Some st60 wind instrument firmware has knots and km/h backwards, set this
# to True to switch from the NMEA standard if you have such a unit
st60_fix = True