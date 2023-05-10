#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import os
import time
from sys import exit
import config
from open_meteo import weather_api

#from font_fredoka_one import FredokaOne
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont

# Speed development by disabling display, enable for production
enable_display = True

offset_hours = config.offset_hours

# Details to customise your weather display

print("Boat logger")
print("Displays weather information for a given location in the config file:")

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

#inky_display.set_border(inky_display.BLACK)

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

# Placeholder variables
pressure = 0.0
wind_speed = 0.0
wind_gusts = 0.0
wind_direction = 0.0
temperature = 0.0
weather_icon = None

if weatherdata:
    #pressure = weatherdata["pressure"]
    temperature = weatherdata["temperature"]
    #wind_speed = weatherdata["wind_speed"]
    weathercode = weatherdata["weather_icon"]

else:
    print("Warning, no weather information found!")

# Create a new canvas to draw on
#img = Image.open(os.path.join(PATH, "resources/backdrop.png")).resize(inky_display.resolution)
#draw = ImageDraw.Draw(img)
img = Image.new("P", (inky_display.resolution))
draw = ImageDraw.Draw(img)

# Load our icon files and generate masks
for icon in glob.glob(os.path.join(PATH, "resources/icon-*.png")):
   icon_name = icon.split("icon-")[1].replace(".png", "")
   icon_image = Image.open(icon)
   icons[icon_name] = icon_image
   masks[icon_name] = create_mask(icon_image)

# Load the FredokaOne font
#font = ImageFont.truetype(FredokaOne, 15)
# https://webpagepublicity.com/free-fonts-e.html#FreeFonts
bigfont = ImageFont.truetype("EdenMills.ttf", 16)
littlefont = ImageFont.truetype("EdenMills.ttf", 12)

# Draw lines to frame the weather data
draw.line(((inky_display.resolution[0] / 2), 2, (inky_display.resolution[0] / 2), inky_display.resolution[1] - 2), inky_display.RED) # Centre division
#draw.line((31, 35, 184, 35))      # Horizontal top line
#draw.line((69, 58, 174, 58))      # Horizontal middle line
#draw.line((169, 58, 169, 58), 2)  # Red seaweed pixel :D

# Write text with weather values to the canvas
datetime = time.strftime("%d/%m %H:%M")
time2 = time.time() - offset_hours*60*60
datetime2 = time.strftime("%d/%m %H:%M", time.localtime(time2))

draw.text((0, 0), datetime, inky_display.BLACK, font=bigfont)

# draw.text((72, 34), "T", inky_display.WHITE, font=font)
draw.text((0, 17), "{} C".format(temperature), inky_display.RED, font=bigfont)
#draw.text((0, 34), "{} hPa".format(pressure), inky_display.BLACK, font=littlefont)
# draw.text((92, 34), "{}°C".format(temperature), inky_display.WHITE, font=font)
#draw.text((0, 47), "{} kts".format(wind_speed), inky_display.RED, font=bigfont)
draw.text((0, 64), "{}N, {}E".format(round(latlong[0], 4), round(latlong[1], 4)), inky_display.BLACK, font=littlefont)
draw.text((((inky_display.resolution[0] / 2) + 5), 0), datetime2, inky_display.RED, font=bigfont)

#draw.text((72, 58), "W", inky_display.WHITE, font=font)
#draw.text((92, 58), "{}kmh".format(windspeed), inky_display.WHITE, font=font)

# Draw the current weather icon over the backdrop
#if weather_icon is not None:
#   img.paste(icons[weather_icon], (28, 36), masks[weather_icon])

#else:
#   draw.text((28, 36), "?", inky_display.RED, font=font)

# Display the weather data on Inky pHAT
if enable_display:
    inky_display.set_image(img)
    inky_display.show()