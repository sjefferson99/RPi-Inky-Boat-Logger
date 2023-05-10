#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
from sys import exit
import config
from open_meteo import weather_api
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont

# Speed development by disabling display, enable for production
enable_display = True

offset_hours = config.offset_hours

# Get the current path
PATH = os.path.dirname(__file__)

# Set up the display
try:
    inky_display = InkyPHAT('red')
except TypeError:
    raise TypeError("You need to update the Inky library to >= v1.1.0")

if inky_display.resolution not in ((212, 104), (250, 122)):
    w, h = inky_display.resolution
    raise RuntimeError("This example does not support {}x{}".format(w, h))

def create_mask(source, mask=(inky_display.WHITE, inky_display.BLACK, inky_display.RED)):
    """Create a transparency mask.

    Takes a paletized source image and converts it into a mask
    permitting all the colours supported by Inky pHAT (0, 1, 2)
    or an optional list of allowed colours.

    :param mask: Optional list of Inky pHAT colours to allow.

    """
    mask_image = Image.new("1", source.size)
    w, h = source.size
    for x in range(w):
        for y in range(h):
            p = source.getpixel((x, y))
            if p in mask:
                mask_image.putpixel((x, y), 255)

    return mask_image

# Dictionaries to store our icons and icon masks in
icons = {}
masks = {}

# Get the weather data for the given location
weather = weather_api()
latlong = weather.get_latlong(config.city, config.countrycode)
weatherdata = weather.get_weather(latlong, offset_hours)

# Create a new canvas to draw on
img = Image.new("P", (inky_display.resolution))
draw = ImageDraw.Draw(img)

# Load our icon files and generate masks
for icon in glob.glob(os.path.join(PATH, "resources/icon-*.png")):
   icon_name = icon.split("icon-")[1].replace(".png", "")
   icon_image = Image.open(icon)
   icons[icon_name] = icon_image
   masks[icon_name] = create_mask(icon_image)

# https://webpagepublicity.com/free-fonts-e.html#FreeFonts
bigfont = ImageFont.truetype("EdenMills.ttf", 14)
littlefont = ImageFont.truetype("EdenMills.ttf", 12)

# Draw line to separate the weather data
draw.line(((inky_display.resolution[0] / 2), 2, (inky_display.resolution[0] / 2), inky_display.resolution[1] - 2), inky_display.RED) # Centre division

# Write text with weather values to the canvas
datetime = time.strftime("%d/%m %H:%M")
time2 = time.time() - offset_hours*60*60
datetime2 = time.strftime("%d/%m %H:%M", time.localtime(time2))

draw.text((0, 0), datetime, inky_display.BLACK, font=bigfont)
draw.text((0, 15), "{} C".format(weatherdata["temperature"]), inky_display.BLACK, font=littlefont)
draw.text((0, 28), "{} hPa".format(weatherdata["pressure"]), inky_display.BLACK, font=littlefont)
draw.text((0, 41), "{} kts".format(weatherdata["wind_speed"]), inky_display.BLACK, font=littlefont)
draw.text((0, 54), "{} kts Gust".format(weatherdata["wind_gusts"]), inky_display.BLACK, font=littlefont)
draw.text((0, 67), "{} Deg".format(weatherdata["wind_direction"]), inky_display.BLACK, font=littlefont)
draw.text((0, 80), "{} C Dew".format(weatherdata["dewpoint"]), inky_display.BLACK, font=littlefont)
draw.text((0, 93), "{}N, {}E".format(latlong[0], latlong[1]), inky_display.BLACK, font=littlefont)
img.paste(icons[weatherdata["weather_icon"]], (55, 10), masks[weatherdata["weather_icon"]])

draw.text((((inky_display.resolution[0] / 2) + 5), 0), datetime2, inky_display.RED, font=bigfont)
draw.text((((inky_display.resolution[0] / 2) + 5), 15), "{} C".format(weatherdata["offset_temperature"]), inky_display.RED, font=littlefont)
draw.text((((inky_display.resolution[0] / 2) + 5), 28), "{} hPa".format(weatherdata["offset_pressure"]), inky_display.RED, font=littlefont)
draw.text((((inky_display.resolution[0] / 2) + 5), 41), "{} kts".format(weatherdata["offset_wind_speed"]), inky_display.RED, font=littlefont)
draw.text((((inky_display.resolution[0] / 2) + 5), 54), "{} kts Gust".format(weatherdata["offset_wind_gusts"]), inky_display.RED, font=littlefont)
draw.text((((inky_display.resolution[0] / 2) + 5), 67), "{} Deg".format(weatherdata["offset_wind_direction"]), inky_display.RED, font=littlefont)
draw.text((((inky_display.resolution[0] / 2) + 5), 80), "{} C Dew".format(weatherdata["offset_dewpoint"]), inky_display.RED, font=littlefont)
draw.text((((inky_display.resolution[0] / 2) + 5), 93), "{}N, {}E".format(latlong[0], latlong[1]), inky_display.RED, font=littlefont)
img.paste(icons[weatherdata["offset_weather_icon"]], (165, 10), masks[weatherdata["offset_weather_icon"]])

# Draw the current weather icon over the backdrop
#if weather_icon is not None:
#   img.paste(icons[weather_icon], (28, 36), masks[weather_icon])

#else:
#   draw.text((28, 36), "?", inky_display.RED, font=font)

# Display the weather data on Inky pHAT
if enable_display:
    inky_display.set_image(img)
    inky_display.show()