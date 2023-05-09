# RPi Inky Boat Logger
This project is intended to run on a Raspberry Pi, probably a Zero 2 W or even an original Zero W. Providing it has internet access and is fitted with an inky PHAT: https://shop.pimoroni.com/products/inky-phat?variant=12549254217811

The intended use case is for a low power system to poll a variety of data sources for information that would be useful to have available in the event of a power loss, specifically boat log information offshore. Having an e-ink record of the last known and recent history of lat/long and weather data is useful for ensuring you have as accurate an EP as possible in the result of power loss preventing normal electronic navigation.

## Current development
For now I have adapted the Pimoroni weather PHAT example to consume the Open Meteo API for free account users.
Next up is presenting last know and recent weather data sensibly on the display.
After that, querying NMEA 0183 data for GPS lat long and weather data on the assumption sattelite or mobile data is not available offshore.