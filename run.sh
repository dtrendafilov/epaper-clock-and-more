#!/bin/bash

# This script is to either:
# - test and trial run epaper-clock-and-more manually
# - be luanched by provided epaper.service (that must be registered under /etc/systemd - your mileage may vary depending what distribution you use)


# WARNING WARNING WARNING
# comment out the following 2 lines but only if you re-configured the environment variables below
echo "Please edit and configure this script for your needs"
exit 1

# Developer debug mode - no epaper device is required to develop or debug - the output that is originally 
# sent to device is being saved as bmp files here: /tmp/epaper*.bmp
#EPAPER_DEBUG_MODE=no

# Lat & lon of your home (a base point)
export LAT=50.0720519
export LON=20.0373204

# A key for traffic delays from Google Maps Distance Matrix API
export GOOGLE_MAPS_KEY=GET_YOUR_OWN_KEY     # get the key from: https://developers.google.com/maps/documentation/embed/get-api-key
# A key for weather forecasts from DarkSky.net API
export DARKSKY_KEY=GET_YOUR_OWN_KEY         # get the key from: https://darksky.net/dev/register
# A key for AQI (Air Quality Index) from AIRLY.EU API (data for certain countries only, as yet, but you may order their device to provide data also for your neighbours)
export AIRLY_KEY=GET_YOUR_OWN_KEY           # get the key from: https://developer.airly.eu/register

export AQI_WARN_LEVEL=75                    # above this value the displayed gauge will become red (on supported displays)

# Lat & lon of destination you want to calculate the current driving time including traffic
export FIRST_TIME_TO_DESTINATION_LAT=49.9684476
export FIRST_TIME_TO_DESTINATION_LON=20.4303646
# The displayed gauge will become red (on supported displays) when driving time exceeds by % 
export FIRST_TIME_WARN_ABOVE_PERCENT=50

# Lat & lon of second destination (for a second member of a household?) you want to calculate the current driving time including traffic
export SECOND_TIME_TO_DESTINATION_LAT=49.9684476
export SECOND_TIME_TO_DESTINATION_LON=20.4303646
# The displayed gauge will become red (on supported displays) when driving time exceeds by % 
export SECOND_TIME_WARN_ABOVE_PERCENT=50

# Dead times - between stated hours data & display update is being done once in an hour and minutes won't be displayed. Default is [] - no dead times.
# This env var will be evaluated by python - so becareful, first: don't expose this env to outside world (security), second: follow the syntax otherwise program will die
#export DEAD_TIMES="[range(1,5),range(10,15)]"

# A type of EPAPER display you want to use - either Waveshare 4"2 (b&w) or 2"7 (tri-color) - this automatically sets EPAPER_MONO to True for 2"7 and to False for 4"2
#export EPAPER_TYPE=waveshare-4.2
export EPAPER_TYPE=waveshare-2.7
# You can override the setting as whether the display is mono or not - though, it will require update (replacement) of relevant epdXinX.py library to support mono or tri-color
#export EPAPER_MONO=True
# You can override whether to listen for button press (enabled by default)
#export EPAPER_BUTTONS_ENABLED=True
# You can override GPIO pins assigned to buttons (these values are set by default and reflect 2.7" HUT version)
#export EPAPER_GPIO_PIN_FOR_KEY1=5
#export EPAPER_GPIO_PIN_FOR_KEY2=6
#export EPAPER_GPIO_PIN_FOR_KEY3=13
#export EPAPER_GPIO_PIN_FOR_KEY4=19

python main.py
