from nmea import tcp_nmea
import time

def test_get_transducer_types():
    """
    Test correct return of transducer types 
    """
    transducer_types = {
        "A":"Angular displacement",
        "C":"Temperature",
        "D":"Depth",
        "F":"Frequency",
        "H":"Humidity",
        "N":"Force",
        "P":"Pressure",
        "R":"Flow"
    }
    nmea = tcp_nmea()
    get_transducer_types = nmea.get_transducer_types()
    assert transducer_types == get_transducer_types

def test_get_transducer_units():
    """
    Test correct return of transducer units
    """
    transducer_units = {
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
    nmea = tcp_nmea()
    get_transducer_units = nmea.get_transducer_units()
    assert transducer_units == get_transducer_units

def test_get_nmea_sentence_words(mocker):
    output = "124027.00,A,5053.00348,N,00118.21794,W,0.009,,110623,,,A*63"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    nmea = tcp_nmea()
    nmea_words = nmea.get_nmea_sentence_words("$GPRMC")
    words = ["124027.00","A","5053.00348","N","00118.21794","W","0.009","","110623","","","A","63"]
    assert words == nmea_words

def test_get_date_time(mocker):
    output = "124027.00,A,5053.00348,N,00118.21794,W,0.009,,110623,,,A*63"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    nmea = tcp_nmea()
    timestamp = nmea.get_datetime()
    assert timestamp == 1686483627.0

def test_get_lat_long(mocker):
    output = "124027.00,A,5053.00348,N,00118.21794,W,0.009,,110623,,,A*63"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    nmea = tcp_nmea()
    nmea_lat_long = nmea.get_lat_long()
    lat_long = {"lat":"5053.00348", "ns":"N", "long":"00118.21794", "ew":"W"}
    assert lat_long == nmea_lat_long

def test_get_transducer_data_humidity(mocker):
    output = "C,22.36,C,AIRTEMP,P,1.00167,B,BARO,H,62.21,P,HUMIDITY*39"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    nmea = tcp_nmea()
    nmea_transducer_data = nmea.get_transducer_data()
    transducer_data = {'Humidity': {'label': 'HUMIDITY', 'unit': 'P', 'value': '62.21'},
   'Pressure': {'label': 'BARO', 'unit': 'B', 'value': '1.00167'},
   'Temperature': {'label': 'AIRTEMP', 'unit': 'C', 'value': '22.36'},
   'timestamp': 1687108979.4467692}
    assert nmea_transducer_data["Humidity"] == transducer_data["Humidity"]

def test_get_transducer_data_pressure(mocker):
    output = "C,22.36,C,AIRTEMP,P,1.00167,B,BARO,H,62.21,P,HUMIDITY*39"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    nmea = tcp_nmea()
    nmea_transducer_data = nmea.get_transducer_data()
    transducer_data = {'Humidity': {'label': 'HUMIDITY', 'unit': 'P', 'value': '62.21'},
   'Pressure': {'label': 'BARO', 'unit': 'B', 'value': '1.00167'},
   'Temperature': {'label': 'AIRTEMP', 'unit': 'C', 'value': '22.36'},
   'timestamp': 1687108979.4467692}
    assert nmea_transducer_data["Pressure"] == transducer_data["Pressure"]

def test_get_transducer_data_temperature(mocker):
    output = "C,22.36,C,AIRTEMP,P,1.00167,B,BARO,H,62.21,P,HUMIDITY*39"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    nmea = tcp_nmea()
    nmea_transducer_data = nmea.get_transducer_data()
    transducer_data = {'Humidity': {'label': 'HUMIDITY', 'unit': 'P', 'value': '62.21'},
   'Pressure': {'label': 'BARO', 'unit': 'B', 'value': '1.00167'},
   'Temperature': {'label': 'AIRTEMP', 'unit': 'C', 'value': '22.36'},
   'timestamp': 1687108979.4467692}
    assert nmea_transducer_data["Temperature"] == transducer_data["Temperature"]

def test_get_transducer_data_timestamp(mocker):
    output = "C,22.36,C,AIRTEMP,P,1.00167,B,BARO,H,62.21,P,HUMIDITY*39"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    nmea = tcp_nmea()
    nmea_transducer_data = nmea.get_transducer_data()
    time_now = time.time()
    time_diff = time_now - nmea_transducer_data["timestamp"]
    assert time_diff == 0

def test_get_wind_data(mocker):
    output = "230.5,R,2.9,N,A*32"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    mocker.patch('config.st60_fix', False)
    nmea = tcp_nmea()
    nmea_wind_data = nmea.get_wind_data()
    wind_data = {'angle': '230.5', 'reference': 'R', 'speed': '2.9', 'units': 'Knots'}
    assert nmea_wind_data == wind_data

def test_get_wind_data_st60(mocker):
    output = "230.5,R,2.9,N,A*32"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    mocker.patch('config.st60_fix', True)
    nmea = tcp_nmea()
    nmea_wind_data = nmea.get_wind_data()
    wind_data = {'angle': '230.5', 'reference': 'R', 'speed': '2.9', 'units': 'km/h'}
    assert nmea_wind_data == wind_data

def test_get_cog_sog_data(mocker):
    output = ",018,T,021,M,2.4,N,4.445,K,A*0B"
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence", return_value=output )
    nmea = tcp_nmea()
    nmea_cog_sog_data = nmea.get_cog_sog_data()
    cog_sog_data = {'cog': '018', 'sog': '2.4'}
    assert nmea_cog_sog_data == cog_sog_data