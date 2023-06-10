from nmea import tcp_nmea

print("Instantiating weather NMEA")
wnmea = tcp_nmea("192.168.68.201", 2000)

print("Retrieving transducer data")
weather_data = wnmea.get_transducer_data()

print(weather_data)

print("The temperature is {} {}".format(weather_data["Temperature"]["value"], weather_data["Temperature"]["unit"]))