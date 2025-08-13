import time
import random
from collections import OrderedDict

from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a color() function to convert 24-bit
# color space to the color space supported by the display.

from menus import Menus
from themes import Default_theme as themeClass

color = displayClass.color


class TwentyFortyEight(Menus):
    def __init__(self, LCD: displayClass, theme: themeClass):
        super().__init__(LCD, theme)