from display_driver import LCD_1inch3 as displayClass
# The display driver must contain a colour() function to convert 24-bit
# color space to the color space supported by the display.

class Theme():
    def __init__(self, LCD:displayClass):
        primary_color = LCD.colour(255, 0, 0)
        secondary_color = LCD.colour(90, 90, 90)
        background_color = LCD.colour(255, 255, 255)
        secondary_background_color = LCD.colour(200, 200, 200)
        text_color = LCD.colour(0, 0, 0)
        button_color = LCD.colour(240, 50, 40)
        button_pressed_color = LCD.colour(0, 255, 0)
        button_border_color = LCD.colour(0, 0, 0)
        button_selected_borderColor = LCD.colour(127, 127, 127)
        button_border_thickness = 4,
        button_pressed_textColor = LCD.colour(255, 255, 255)
        vertical_reserve=10,
        horizontal_reserve=6, 