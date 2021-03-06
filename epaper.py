# Original code: https://github.com/prehensile/waveshare-clock
# Modifications: https://github.com/pskowronek/epaper-clock-and-more, Apache 2 license

import logging
import json
import os
from PIL import Image

from drawing import Drawing
from providers.luftdaten import Luftdaten
from providers.weather import Weather
from providers.ical import ICal
from providers.system_info import SystemInfo


class EPaper(object):

    # only update once an hour within these ranges
    # eval - don't try this at home :) i.e. don't expose envs to alians
    DEAD_TIMES = eval(os.environ.get("DEAD_TIMES", "[]"))
    # whether to display two vertical dots to separate hrs and mins
    CLOCK_HOURS_MINS_SEPARATOR = os.environ.get("CLOCK_HRS_MINS_SEPARATOR", "true") == "true"
    # whether to prefer AQI temperature instead of DarkSky's
    PREFER_AIRLY_LOCAL_TEMP = os.environ.get("PREFER_AIRLY_LOCAL_TEMP", "false") == "true"

    DEVICE_TYPE = os.environ.get("EPAPER_TYPE", 'waveshare-2.7')


    if DEVICE_TYPE == 'waveshare-2.7':          # TODO refactor to use enums
        # Display resolution for 2.7"
        EPD_WIDTH       = 176
        EPD_HEIGHT      = 264
        MONO_DISPLAY    = False
    elif DEVICE_TYPE == 'waveshare-4.2':
        # Display resolution for 4.2"
        EPD_WIDTH       = 400
        EPD_HEIGHT      = 300
        MONO_DISPLAY    = True
    else:
        raise Exception('Incorrect epaper screen type: ' + DEVICE_TYPE)


    MONO_DISPLAY = os.environ.get("EPAPER_MONO", "true" if MONO_DISPLAY else "false") == "true"  # one may override but must replace relevant library edpXinX.py, by default lib for 2.7 is tri-color, 4.2 is mono
    FAST_REFRESH = os.environ.get("EPAPER_FAST_REFRESH", "false") == "true"


    drawing = Drawing(
        os.environ.get("DARK_SKY_UNITS", "si"),
        int(os.environ.get("WEATHER_STORM_DISTANCE_WARN", "10")),
        int(os.environ.get("AQI_WARN_LEVEL", "75")),
        int(os.environ.get("FIRST_TIME_WARN_ABOVE_PERCENT", "50")),
        int(os.environ.get("SECONDARY_TIME_WARN_ABOVE_PERCENT", "50"))
    )

    airly = Luftdaten(
        os.environ.get("LAT"),
        os.environ.get("LON"),
        int(os.environ.get("AIRLY_TTL", "20"))
    )
    weather = Weather(
        os.environ.get("DARKSKY_KEY"),
        os.environ.get("LAT"),
        os.environ.get("LON"),
        os.environ.get("DARKSKY_UNITS", "si"),
        int(os.environ.get("DARKSKY_TTL", "15"))
    )
    system_info = SystemInfo()

    events = ICal(os.environ.get("EVENTS_ICAL_URL"))


    def __init__(self, debug_mode = False):

        self._debug_mode = debug_mode
        if not debug_mode:
            if self.DEVICE_TYPE == 'waveshare-2.7':
                if self.FAST_REFRESH:
                    logging.info("Using experimental LUT tables!")
                    from epds import epd2in7b_fast_lut
                    self._epd = epd2in7b_fast_lut.EPD()
                else:
                    from epds import epd2in7b
                    self._epd = epd2in7b.EPD()
            elif self.DEVICE_TYPE == 'waveshare-4.2':
                from epds import epd4in2
                self._epd = epd4in2.EPD()

            self._epd.init()

        self._str_time = "XXXX"


    def display(self, black_buf, red_buf, name):
        if self._debug_mode:
            debug_output = "test/epaper-" + ( name.strftime("%H-%M-%S") if type(name) is not str else name )
            logging.info("Debug mode - saving screen output to: " + debug_output + "* bmps")
            black_buf.save(debug_output + "_bw_frame.bmp")
            if not self.MONO_DISPLAY:
                red_buf.save(debug_output + "_red_frame.bmp")
            return

        if not self.MONO_DISPLAY:
            logging.info("Going to display a new tri-color image...")
            self._epd.display_frame(
                self._epd.get_frame_buffer(black_buf),
                self._epd.get_frame_buffer(red_buf)
            )
        else:
            logging.info("Going to display a new mono-color image...")
            self._epd.display_frame(
                self._epd.get_frame_buffer(black_buf)
            )


    def display_buffer(self, black_buf, red_buf, dt):

        if self.DEVICE_TYPE == 'waveshare-2.7' and not self._debug_mode:
            black_buf = black_buf.transpose(Image.ROTATE_90)
            black_buf = black_buf.resize((self.EPD_WIDTH, self.EPD_HEIGHT), Image.LANCZOS)

            red_buf = red_buf.transpose(Image.ROTATE_90)
            red_buf = red_buf.resize((self.EPD_WIDTH, self.EPD_HEIGHT), Image.LANCZOS)

        self.display(black_buf, red_buf, dt)


    def display_shutdown(self):
        black_frame, red_frame = self.drawing.draw_shutdown(self.MONO_DISPLAY)
        self.display_buffer(black_frame, red_frame, 'shutdown')


    def display_airly_details(self):
        black_frame, red_frame = self.drawing.draw_airly_details(self.airly.get())
        self.display_buffer(black_frame, red_frame, 'airly')


    def display_weather_forecast(self):
        black_frame, red_frame = self.drawing.draw_weather_forecast(self.weather.get())
        self.display_buffer(black_frame, red_frame, 'forecast')


    def display_weather_details(self):
        black_frame, red_frame = self.drawing.draw_weather_details(self.weather.get())
        self.display_buffer(black_frame, red_frame, 'weather')


    def display_system_details(self):
        black_frame, red_frame = self.drawing.draw_system_details(self.system_info.get())
        self.display_buffer(black_frame, red_frame, 'system')


    def display_main_screen(self, dt, force = False):
        time_format = "%H%M"
        formatted = dt.strftime(time_format)

        # set blank minutes if time's hour is within dead ranges
        h = formatted[:2]
        for dead_range in self.DEAD_TIMES:
            if int(h) in dead_range:
                formatted = "{}  ".format(h)

        if force or formatted != self._str_time:

            weather_data = self.weather.get()
            logging.info("--- weather: " + json.dumps(weather_data))

            airly_data = self.airly.get()
            logging.info("--- airly: " + json.dumps(airly_data))

            events_data = self.events.get()

            black_frame, red_frame = self.drawing.draw_frame(
                self.MONO_DISPLAY,
                events_data,
                self.CLOCK_HOURS_MINS_SEPARATOR,
                weather_data,
                self.PREFER_AIRLY_LOCAL_TEMP,
                airly_data
            )
            self.display_buffer(black_frame, red_frame, dt)

            self._str_time = formatted

