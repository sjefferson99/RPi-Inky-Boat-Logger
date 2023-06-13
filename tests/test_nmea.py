from nmea import tcp_nmea
import telnetlib

def test_connect():
    """
    Test init using host and port
    """
    nmea = tcp_nmea()
    nmea.connect("192.168.4.90", 2000)
    assert type(nmea.tn) == type(telnetlib.Telnet())

def test_transducer_types():
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

def test_transducer_units():
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

def test_date_time(mocker):
    output = ["124027.00","A","5053.00348","N","00118.21794","W","0.009","","110623","","","A","63"]
    mocker.patch( "nmea.tcp_nmea.get_nmea_sentence_words", return_value=output )
    nmea = tcp_nmea()
    timestamp = nmea.get_datetime()
    assert timestamp == 1686483627.0