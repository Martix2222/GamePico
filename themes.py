from drivers.display_driver import LCD_1inch3 as displayClass
# The display driver must contain a colour() function to convert 24-bit
# color space to the color space supported by the display.

class Default_theme():
    def __init__(self, LCD:displayClass):
        self.primary_color = LCD.color(255, 0, 0)
        self.secondary_color = LCD.color(90, 90, 90)
        self.background_color = LCD.color(255, 255, 255)
        self.secondary_background_color = LCD.color(200, 200, 200)
        self.text_color = LCD.color(0, 0, 0)
        self.button_color = LCD.color(240, 50, 40)
        self.button_pressed_color = LCD.color(0, 255, 0)
        self.button_border_color = LCD.color(0, 0, 0)
        self.button_selected_border_color = LCD.color(127, 127, 127)
        self.button_pressed_text_color = LCD.color(255, 255, 255)
        self.button_border_thickness = 4
        self.vertical_reserve=10
        self.horizontal_reserve=6
        self.intro_circle_thickness=20