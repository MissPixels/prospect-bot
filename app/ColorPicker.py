import os
import time
from colorsys import hls_to_rgb

from app.Base import Base


class ColorPicker(Base):

    """This class is responsible for generating an HSL color value at a given point in time
    The Saturation and Light values are fixed
    The Hue value cycles from 0 to 360 over a
    revolution period (COLOR_WHEEL_REVOLUTION_DURATION)
    The base time (COLOR_WHEEL_BASE_TIME) represent the beginning of the first cycle
    When a cycle ends, another one starts, resetting Hue to 0


    Attributes:
        baseTime (int): Timestamp representing the beginning of the first cycle
        light (int): Light value
        revolutionDuration (int): Hue value's revolution duration in seconds
        saturation (int): Saturation value
    """

    def __init__(self):
        super(ColorPicker, self).__init__()
        self.saturation = 100
        self.light = 50
        self.revolutionDuration = int(
            os.getenv("COLOR_WHEEL_REVOLUTION_DURATION", 3600)
        )
        self.baseTime = int(os.getenv("COLOR_WHEEL_BASE_TIME", 0))
        self.log("\n* ColorPicker initialized")
        self.log(
            "Revolution duration\t{} days".format(
                self.formatDuration(self.revolutionDuration)
            )
        )
        self.log("Base time\t\t{}".format(self.timestampToDate(self.baseTime)))

    def getCurrentColor(self):
        """Returns the current color

        Returns:
            list: Color values in HSL format
        """
        currentTime = int(time.time())
        secondsFromBaseTime = (currentTime - self.baseTime) % self.revolutionDuration
        currentHue = int((secondsFromBaseTime / self.revolutionDuration) * 360)
        currentColorHsl = [currentHue, self.saturation, self.light]
        return currentColorHsl

    def getCurrentColorRgb(self):
        hsl = self.getCurrentColor()
        hue, sat, light = [float(v) for v in hsl]
        hue /= 360
        sat /= 100
        light /= 100
        rgb = hls_to_rgb(hue, light, sat)
        red, green, blue = [int(v * 255) for v in rgb]
        return red, green, blue
